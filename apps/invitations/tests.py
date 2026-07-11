import os
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from django.core import mail
from django.test import SimpleTestCase, TestCase, override_settings
from docx import Document

from .models import CommunicationBatch, CommunicationLogStatus
from .services import (
    EmailConfigurationStatus,
    PDF_CONVERSION_ERROR_MESSAGE,
    PDFConversionError,
    build_pdf_attachment,
    convert_docx_to_pdf,
    sanitize_attachment_filename,
    send_communication_email,
    send_rendered_invitation,
)


def make_docx(path, text="Hola {{NOMBRE}}"):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(path)


class PDFConversionTests(SimpleTestCase):
    def test_conversion_success_returns_pdf_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = Path(tmpdir) / "invitacion.docx"
            make_docx(docx_path)

            def fake_run(command, **kwargs):
                outdir = Path(command[command.index("--outdir") + 1])
                (outdir / "invitacion.pdf").write_bytes(b"%PDF-1.4")
                return subprocess.CompletedProcess(command, 0, "", "")

            with patch("apps.invitations.services.resolve_libreoffice_binary", return_value="soffice"):
                with patch("apps.invitations.services.subprocess.run", side_effect=fake_run):
                    pdf_path = convert_docx_to_pdf(docx_path, tmpdir)

            self.assertTrue(pdf_path.endswith(".pdf"))
            self.assertTrue(Path(pdf_path).exists())

    def test_libreoffice_absent_raises_clear_error(self):
        with override_settings(LIBREOFFICE_BINARY=""):
            with patch("apps.invitations.services.shutil.which", return_value=None):
                with self.assertRaisesRegex(PDFConversionError, "No fue posible generar el PDF"):
                    from .services import resolve_libreoffice_binary

                    resolve_libreoffice_binary()

    def test_conversion_timeout_raises_controlled_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = Path(tmpdir) / "invitacion.docx"
            make_docx(docx_path)
            with patch("apps.invitations.services.resolve_libreoffice_binary", return_value="soffice"):
                with patch(
                    "apps.invitations.services.subprocess.run",
                    side_effect=subprocess.TimeoutExpired("soffice", 60),
                ):
                    with self.assertRaisesRegex(PDFConversionError, "tiempo limite"):
                        convert_docx_to_pdf(docx_path, tmpdir)

    def test_missing_pdf_after_success_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = Path(tmpdir) / "invitacion.docx"
            make_docx(docx_path)
            with patch("apps.invitations.services.resolve_libreoffice_binary", return_value="soffice"):
                with patch(
                    "apps.invitations.services.subprocess.run",
                    return_value=subprocess.CompletedProcess(["soffice"], 0, "", ""),
                ):
                    with self.assertRaisesRegex(PDFConversionError, "no genero el archivo PDF"):
                        convert_docx_to_pdf(docx_path, tmpdir)

    def test_attachment_filename_is_sanitized(self):
        filename = sanitize_attachment_filename("../Moisés Sánchez: Equipo #1", ".pdf")
        self.assertEqual(filename, "Moises_Sanchez_Equipo_1.pdf")
        self.assertNotIn("..", filename)
        self.assertTrue(filename.endswith(".pdf"))

    def test_build_pdf_attachment_uses_pdf_mime(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "invitacion.pdf"
            pdf_path.write_bytes(b"%PDF-1.4")
            name, content, mime = build_pdf_attachment(pdf_path, "Invitacion Test.pdf")
        self.assertEqual(name, "Invitacion_Test.pdf")
        self.assertEqual(content, b"%PDF-1.4")
        self.assertEqual(mime, "application/pdf")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="no-reply@example.com",
)
class InvitationEmailTests(TestCase):
    def test_email_attaches_pdf_and_not_docx(self):
        with patch(
            "apps.invitations.services.is_real_email_configured",
            return_value=EmailConfigurationStatus(True, "smtp", "ok", "no-reply@example.com"),
        ):
            log = send_communication_email(
                recipient_name="Colegio Ejemplo",
                recipient_email="destino@example.com",
                communication_type="colegio",
                subject="Invitacion",
                body="Adjunto",
                attachments=[("Invitacion.pdf", b"%PDF-1.4", "application/pdf")],
                dry_run=False,
            )

        self.assertEqual(log.status, CommunicationLogStatus.SENT)
        self.assertEqual(len(mail.outbox), 1)
        attachments = mail.outbox[0].attachments
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0][0], "Invitacion.pdf")
        self.assertEqual(attachments[0][2], "application/pdf")
        self.assertFalse(any(item[0].lower().endswith(".docx") for item in attachments))

    def test_temporary_files_are_cleaned_after_invitation_render(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "template.docx"
            make_docx(template_path)
            captured_dirs = []

            def fake_convert(docx_path, output_dir):
                captured_dirs.append(output_dir)
                self.assertTrue(Path(docx_path).exists())
                pdf_path = Path(output_dir) / "rendered.pdf"
                pdf_path.write_bytes(b"%PDF-1.4")
                return str(pdf_path)

            def fake_send(**kwargs):
                attachments = kwargs["attachments"]
                self.assertEqual(len(attachments), 1)
                self.assertTrue(attachments[0][0].endswith(".pdf"))
                self.assertEqual(attachments[0][2], "application/pdf")
                return SimpleNamespace(status=CommunicationLogStatus.DRY_RUN)

            with patch("apps.invitations.services.convert_docx_to_pdf", side_effect=fake_convert):
                with patch("apps.invitations.services.send_communication_email", side_effect=fake_send):
                    send_rendered_invitation(
                        batch=None,
                        template=SimpleNamespace(file=str(template_path)),
                        recipient={
                            "name": "Colegio Ejemplo",
                            "email": "colegio@example.com",
                            "institution_name": "Colegio Ejemplo",
                        },
                        communication_type="colegio",
                        dry_run=True,
                    )

        self.assertTrue(captured_dirs)
        self.assertFalse(os.path.exists(captured_dirs[0]))

    def test_conversion_failure_does_not_mark_sent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "template.docx"
            make_docx(template_path)
            batch = CommunicationBatch.objects.create(
                name="Lote prueba",
                communication_type="colegio",
                dry_run=True,
            )
            with patch("apps.invitations.services.convert_docx_to_pdf", side_effect=PDFConversionError(PDF_CONVERSION_ERROR_MESSAGE)):
                log = send_rendered_invitation(
                    batch=batch,
                    template=SimpleNamespace(file=str(template_path)),
                    recipient={
                        "name": "Colegio Ejemplo",
                        "email": "colegio@example.com",
                        "institution_name": "Colegio Ejemplo",
                    },
                    communication_type="colegio",
                    dry_run=True,
                )

        self.assertEqual(log.status, CommunicationLogStatus.FAILED)
        self.assertEqual(batch.logs.filter(status=CommunicationLogStatus.SENT).count(), 0)
