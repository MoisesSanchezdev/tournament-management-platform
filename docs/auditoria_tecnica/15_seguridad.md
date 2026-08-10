# 15. Seguridad

## Configuracion Django

| Control | Evidencia |
| --- | --- |
| `DEBUG=False` por defecto | `config/settings.py` |
| `SECRET_KEY` obligatoria sin debug | `ImproperlyConfigured` si falta |
| `ALLOWED_HOSTS` obligatorio sin debug | `ImproperlyConfigured` si falta |
| CSRF middleware activo | `CsrfViewMiddleware` |
| Clickjacking | `X_FRAME_OPTIONS = "DENY"` |
| MIME sniffing | `SECURE_CONTENT_TYPE_NOSNIFF = True` |
| Referrer policy | `SECURE_REFERRER_POLICY = "same-origin"` |
| Cookies seguras | `CSRF_COOKIE_SECURE` y `SESSION_COOKIE_SECURE` son `not DEBUG` |
| HSTS | Activado cuando `not DEBUG` |
| SSL redirect | Activado cuando `not DEBUG` |

## Autorizacion

Panel interno y comunicaciones usan `@login_required` y `@user_passes_test(is_organizer)`.

`is_organizer` exige usuario autenticado y `is_staff` o `is_superuser`.

## CSRF

Se confirmo uso de `{% csrf_token %}` en formularios POST. `control.js` envia `X-CSRFToken` en peticiones AJAX.

## Comunicaciones reales

| Control | Evidencia |
| --- | --- |
| Dry-run por defecto | Formularios y comandos |
| Prueba controlada | `test_recipient` redirige fisicamente los correos |
| Confirmacion explicita | `confirm_real_send` o `--yes` |
| Validacion SMTP | `is_real_email_configured` |
| Bloqueo de placeholders | `_looks_like_placeholder_secret` |
| Logs por destinatario | `CommunicationLog` |

## Datos sensibles

`.gitignore` ignora `.env`, `.env.*` excepto `.env.example`, `db.sqlite3`, `*.sqlite3`, `media/` y listados reales en `docs/correos/`.

La auditoria no documenta valores secretos reales.

## Riesgos

| Riesgo | Evidencia | Recomendacion |
| --- | --- | --- |
| `reset_tournament_demo.py` borra datos | Usa `.delete()` masivo en modelos operativos | Ejecutar solo en entorno demo |
| Panel staff/superuser sin roles finos | Autorizacion binaria en `is_organizer` | Definir permisos por accion antes de produccion |
| Logs pueden guardar previews | `rendered_preview` en `CommunicationLog` hasta 4000 chars | Revisar si preview puede contener datos personales |
| Confirmacion asistencia sin login | Token UUID en URL | Mantener tokens no predecibles y HTTPS |
| Assets externos | Imagenes externas en home | Revisar disponibilidad y politicas de terceros |

## No confirmado

| Punto | Estado |
| --- | --- |
| Politica de privacidad | NO CONFIRMADO |
| Gestion formal de datos personales | NO CONFIRMADO |
| Auditoria de acceso por usuario | Parcial; hay logs de competencia y comunicaciones, no auditoria auth completa |
| Proteccion rate-limit | NO CONFIRMADO |
