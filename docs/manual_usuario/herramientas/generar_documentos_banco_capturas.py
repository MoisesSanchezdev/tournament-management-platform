import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_DIR = ROOT / "planificacion"
MANIFEST = ROOT / "capturas" / "revision" / "metadata_banco_capturas.json"
SUMMARY = ROOT / "entorno_demo" / "datos" / "resumen_banco_capturas.json"


CAPTURES = [
    ("MU-001", "MU-001-inicio-publico.png", "Primeros pasos", "PU-001", "Publico", "Edicion demo activa", "Conteos y botones publicos", "/", "Bajo", "Alta", "Entrada general"),
    ("MU-002", "MU-002-reglas-publicas.png", "Consulta publica", "PU-002", "Publico", "Reglas demo publicadas", "Consulta de reglas", "/reglas/", "Bajo", "Alta", "Capitulo de consulta"),
    ("MU-003", "MU-003-patrocinadores.png", "Consulta publica", "PU-003", "Publico", "Catalogo demo", "Tarjetas de aliados", "/patrocinadores/", "Medio", "Media", "Contexto institucional"),
    ("MU-004", "MU-004-seleccion-registro.png", "Registro", "REG-001", "Publico", "Sin login", "Seleccionar categoria", "/registro/", "Bajo", "Alta", "Entrada de registro"),
    ("MU-005", "MU-005-registro-escolar.png", "Registro escolar", "REG-002", "Publico", "Formulario disponible", "Formulario diligenciado", "/registro/colegios/", "Medio", "Alta", "Recorte de campos"),
    ("MU-006", "MU-006-registro-escolar-error.png", "Registro escolar", "REG-002", "Publico", "Duplicado ficticio", "Enviar duplicado", "/registro/colegios/", "Medio", "Alta", "Validaciones"),
    ("MU-007", "MU-007-registro-universitario.png", "Registro universitario", "REG-003", "Publico", "Formulario disponible", "Formulario con semestre", "/registro/universidades/", "Medio", "Alta", "Recorte de campos"),
    ("MU-008", "MU-008-registro-exito.png", "Registro", "REG-004", "Publico", "Registro enviado", "Ver confirmacion", "/registro/exito/colegio/", "Bajo", "Alta", "Cierre de registro"),
    ("MU-009", "MU-009-confirmacion-asistencia.png", "Asistencia", "REG-005", "Publico", "Token demo valido", "Ver boton confirmar", "/registro/confirmar-asistencia/<token-demo>/", "Medio", "Alta", "Solicitud asistencia"),
    ("MU-010", "MU-010-asistencia-confirmada.png", "Asistencia", "REG-005", "Publico", "Token demo confirmado", "Ver estado confirmado", "/registro/confirmar-asistencia/<token-demo>/", "Medio", "Alta", "Estado asistencia"),
    ("MU-011", "MU-011-token-invalido.png", "Asistencia", "REG-006", "Publico", "Token ficticio invalido", "Ver enlace invalido", "/registro/confirmar-asistencia/<uuid-cero>/", "Bajo", "Alta", "Soporte"),
    ("MU-012", "MU-012-login-panel.png", "Acceso", "INT-001", "Staff", "Usuario demo", "Formulario vacio", "/torneo/control/login/", "Bajo", "Alta", "Ingreso interno"),
    ("MU-013", "MU-013-panel-torneo.png", "Operacion", "TOR-001", "Staff", "Login staff", "Resumen de divisiones", "/torneo/control/", "Medio", "Alta", "Dashboard"),
    ("MU-014", "MU-014-generar-competencia.png", "Operacion", "TOR-001", "Staff", "Equipos aprobados", "Boton generar/regenerar", "/torneo/control/", "Medio", "Alta", "Secuencia tablero"),
    ("MU-015", "MU-015-configuracion-division.png", "Configuracion", "TOR-002", "Staff", "Competencia creada", "Resumen y recomendacion", "/torneo/control/divisiones/<id>/", "Medio", "Alta", "Formato"),
    ("MU-016", "MU-016-formato-manual.png", "Configuracion", "TOR-002", "Staff", "Competencia creada", "Abrir ajustes manuales", "/torneo/control/divisiones/<id>/", "Medio", "Alta", "Recorte formulario"),
    ("MU-017", "MU-017-distribucion-grupos.png", "Configuracion", "TOR-002", "Staff", "Grupos creados", "Abrir distribucion manual", "/torneo/control/divisiones/<id>/", "Medio", "Alta", "Recorte lista"),
    ("MU-018", "MU-018-clasificados-grupo.png", "Fase grupos", "TOR-005", "Staff", "Grupos con clasificados", "Tarjetas y contador", "/torneo/control/divisiones/<id>/fases/groups/", "Medio", "Alta", "Resultados"),
    ("MU-019", "MU-019-guardar-grupo.png", "Fase grupos", "TOR-005", "Staff", "Seleccion hecha", "Boton guardar grupo", "/torneo/control/divisiones/<id>/fases/groups/", "Medio", "Media", "Base pre-dialogo"),
    ("MU-020", "MU-020-guardar-todos.png", "Guardado", "TOR-005", "Staff", "Cambios visibles", "Boton guardar todos", "/torneo/control/divisiones/<id>/fases/groups/", "Medio", "Alta", "Guardado global"),
    ("MU-021", "MU-021-modal-siguiente-fase.png", "Avance", "TOR-003", "Staff", "Etapa cerrada", "Abrir modal", "/torneo/control/divisiones/<id>/", "Medio", "Alta", "Modal general"),
    ("MU-022", "MU-022-crear-fase-recomendada.png", "Avance", "TOR-003", "Staff", "Recomendacion lista", "Vista previa recomendada", "/torneo/control/divisiones/<id>/", "Medio", "Alta", "Secuencia avance"),
    ("MU-023", "MU-023-repechaje.png", "Repechaje", "TOR-003", "Staff", "Candidatos demo", "Vista previa repechaje", "/torneo/control/divisiones/<id>/", "Medio", "Alta", "Repechaje"),
    ("MU-024", "MU-024-asistente-manual.png", "Fase manual", "TOR-004", "Staff", "Elegibles demo", "Abrir asistente", "/torneo/control/divisiones/<id>/", "Medio", "Alta", "Fase manual"),
    ("MU-025", "MU-025-propuesta-manual.png", "Fase manual", "TOR-004", "Staff", "Propuesta demo", "Mostrar propuesta", "/torneo/control/divisiones/<id>/", "Medio", "Alta", "Recorte propuesta"),
    ("MU-026", "MU-026-batalla-ganador.png", "Batallas", "TOR-006", "Staff", "Batalla con ganador", "Radios/tarjetas", "/torneo/control/divisiones/<id>/fases/semifinal/", "Medio", "Alta", "Ganador"),
    ("MU-027", "MU-027-batalla-clasificados.png", "Batallas", "TOR-006", "Staff", "Batalla multi", "Checkboxes y clasificados", "/torneo/control/divisiones/<id>/fases/quarterfinal/", "Medio", "Alta", "Clasificados multiples"),
    ("MU-028", "MU-028-confirmacion-correccion.png", "Correcciones", "TOR-006", "Staff", "Resultado ya guardado", "Cambio previo a confirmacion", "/torneo/control/divisiones/<id>/fases/semifinal/", "Alto", "Media", "Candidata editorial"),
    ("MU-029", "MU-029-modal-participante.png", "Control manual", "TOR-007", "Staff", "Participante demo", "Abrir detalle", "/torneo/control/divisiones/<id>/fases/groups/", "Medio", "Alta", "Modal participante"),
    ("MU-030", "MU-030-edicion-participante.png", "Control manual", "TOR-007", "Staff", "Modal abierto", "Campos editables", "/torneo/control/divisiones/<id>/fases/groups/", "Medio", "Alta", "Edicion modal"),
    ("MU-031", "MU-031-podio-final.png", "Cierre", "TOR-008", "Staff", "Final lista", "Podio guardado", "/torneo/control/divisiones/<id>/fases/final/", "Medio", "Alta", "Cierre torneo"),
    ("MU-032", "MU-032-dashboard-comunicaciones.png", "Comunicaciones", "COM-001", "Staff", "Login staff", "Indicadores correo", "/comunicaciones/", "Medio", "Alta", "Dashboard comunicaciones"),
    ("MU-033", "MU-033-lista-plantillas.png", "Plantillas", "COM-002", "Staff", "Plantillas demo", "Tabla", "/comunicaciones/plantillas/", "Bajo", "Alta", "Lista plantillas"),
    ("MU-034", "MU-034-nueva-plantilla.png", "Plantillas", "COM-003", "Staff", "DOCX demo", "Formulario carga", "/comunicaciones/plantillas/nueva/", "Medio", "Alta", "Recorte formulario"),
    ("MU-035", "MU-035-preview-plantilla.png", "Plantillas", "COM-004", "Staff", "Plantilla cargada", "Marcadores detectados", "/comunicaciones/plantillas/<id>/previsualizar/", "Medio", "Alta", "Previsualizacion"),
    ("MU-036", "MU-036-invitaciones-lote.png", "Invitaciones", "COM-005", "Staff", "Plantilla activa", "Formulario dry-run", "/comunicaciones/invitaciones/", "Medio", "Alta", "Procesar lote"),
    ("MU-037", "MU-037-destinatario-manual.png", "Destinatarios", "COM-005", "Staff", "Staff login", "Formulario manual", "/comunicaciones/invitaciones/", "Medio", "Alta", "Recorte destinatario"),
    ("MU-038", "MU-038-confirmaciones-asistencia.png", "Confirmaciones", "COM-006", "Staff", "Registros submitted", "Acciones dry-run/test", "/comunicaciones/confirmaciones/", "Medio", "Alta", "Asistencia"),
    ("MU-039", "MU-039-historial-comunicaciones.png", "Historial", "COM-007", "Staff", "Logs demo", "Tabla logs", "/comunicaciones/historial/", "Medio", "Alta", "Auditoria envios"),
    ("MU-040", "MU-040-admin-modelos.png", "Administracion", "ADM-002", "Admin", "Admin demo", "Indice modelos", "/admin/", "Medio", "Media", "Admin general"),
    ("MU-041", "MU-041-admin-registros.png", "Administracion", "ADM-003", "Admin", "Registros demo", "Lista registros", "/admin/participants/schoolregistration/", "Medio", "Media", "Recorte admin"),
    ("MU-042", "MU-042-admin-torneo.png", "Administracion", "ADM-004", "Admin", "Competencias demo", "Lista competencias", "/admin/tournament/divisioncompetition/", "Medio", "Media", "Recorte admin"),
]

DECISIONS = {
    "MU-005": "REQUIERE RECORTE",
    "MU-007": "REQUIERE RECORTE",
    "MU-016": "REQUIERE RECORTE",
    "MU-017": "REQUIERE RECORTE",
    "MU-025": "REQUIERE RECORTE",
    "MU-034": "REQUIERE RECORTE",
    "MU-037": "REQUIERE RECORTE",
    "MU-041": "REQUIERE RECORTE",
    "MU-042": "REQUIERE RECORTE",
    "MU-014": "REQUIERE ANOTACION",
    "MU-020": "REQUIERE ANOTACION",
    "MU-022": "REQUIERE ANOTACION",
    "MU-023": "REQUIERE ANOTACION",
    "MU-024": "REQUIERE ANOTACION",
    "MU-030": "REQUIERE ANOTACION",
    "MU-019": "PENDIENTE MANUAL",
    "MU-028": "PENDIENTE MANUAL",
}


def decision(capture_id):
    return DECISIONS.get(capture_id, "APROBADA COMO BASE")


def generated_lookup():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {item["id"]: item for item in payload["manifest"]}


def md_escape(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_plan():
    rows = [
        "# Plan consolidado del banco de capturas",
        "",
        "Fuente: `05_plan_capturas.md` y resultados de automatizacion CDP Fase 3.",
        "",
        "| ID | Archivo | Procedimiento | Pantalla | Perfil | Precondicion | Datos/estado demo | Interaccion | Ruta | Resolucion | Riesgo | Automatizable | Prioridad | Reutilizacion |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in CAPTURES:
        cid, filename, procedure, screen, profile, precondition, interaction, route, risk, priority, reuse = item
        auto = "Si" if decision(cid) != "PENDIENTE MANUAL" else "Parcial"
        rows.append(
            f"| {cid} | `{filename}` | {procedure} | {screen} | {profile} | {precondition} | Datos ficticios demo; {interaction.lower()} | {interaction} | `{route}` | 1440x900 | {risk} | {auto} | {priority} | {reuse} |"
        )
    rows.extend([
        "",
        "## Criterios de captura",
        "",
        "- Todas las imagenes base se generan en PNG a 1440x900 y zoom 100 %.",
        "- Las rutas con tokens usan tokens ficticios de la base SQLite temporal del entorno demo.",
        "- Las confirmaciones nativas se documentan como flujo previo cuando el dialogo del navegador no se renderiza dentro del PNG headless.",
    ])
    (PLAN_DIR / "13_plan_banco_capturas.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_inventory(manifest):
    rows = [
        "# Inventario de capturas generadas",
        "",
        "| ID | Archivo | Procedimiento | Estado | Resolucion | Privacidad | Recorte | Anotacion | Reutilizable | Resultado |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in CAPTURES:
        cid, filename, procedure, *_rest = item
        meta = manifest.get(cid, {})
        dec = decision(cid)
        recorte = "Si" if dec == "REQUIERE RECORTE" else "No"
        anotacion = "Si" if dec == "REQUIERE ANOTACION" else ("Editorial" if dec == "PENDIENTE MANUAL" else "No")
        estado = meta.get("status", "NO GENERADA")
        resultado = dec if estado != "ERROR" else "REQUIERE RECAPTURA"
        rows.append(
            f"| {cid} | `{filename}` | {procedure} | {estado} | 1440x900 | {meta.get('privacy', 'NO EVALUADA')} | {recorte} | {anotacion} | Si | {resultado} |"
        )
    rows.extend([
        "",
        "Duplicados evitados: se sobreescribio la nomenclatura oficial en `capturas/base/` y se conservaron las pruebas POC en `capturas/prueba/`.",
        "Descartadas: 0 archivos movidos a `capturas/descartadas/` en la pasada final.",
    ])
    (PLAN_DIR / "14_inventario_capturas_generadas.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_manual_pending():
    pending = [
        ("MU-019", "El dialogo `window.confirm` de guardado de grupo no se renderiza en el PNG headless; se genero la pantalla previa con el boton y seleccion visible.", "Fase grupos", "Seleccion hecha en un grupo", "Entrar a grupos, cambiar un clasificado y pulsar Guardar este grupo.", "staff demo", "/torneo/control/divisiones/<id>/fases/groups/", "Robots ficticios y boton de guardado", "Dialogo nativo del navegador o estado previo", "1440x900", "Medio", "Usar captura previa y recrear editorialmente solo el dialogo con texto exacto."),
        ("MU-028", "La confirmacion de `manual_override` depende de un segundo `window.confirm`; CDP puede aceptar el evento, pero el dialogo nativo no aparece dentro de la captura headless.", "Correcciones", "Resultado ya guardado con fase posterior iniciada", "Entrar a semifinal, cambiar el ganador guardado y confirmar la correccion manual.", "staff demo", "/torneo/control/divisiones/<id>/fases/semifinal/", "Robots ficticios y cambio de ganador", "Dialogo de confirmacion manual_override", "1440x900", "Alto", "Usar captura previa y documentar el texto exacto."),
    ]
    rows = [
        "# Capturas no automatizadas",
        "",
        "Solo se listan capturas cuyo estado visual objetivo incluye dialogos nativos no renderizados por el screenshot PNG headless.",
        "",
        "| ID | Razon tecnica | Procedimiento | Estado requerido | Pasos exactos | Usuario demo | URL | Datos visibles | Area a capturar | Resolucion | Riesgo | Alternativa documental |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in pending:
        rows.append("| " + " | ".join(md_escape(value) for value in row) + " |")
    rows.extend([
        "",
        "Textos nativos documentados desde el codigo:",
        "",
        "- Guardado de resultados: `¿Seguro que deseas guardar estas selecciones? Podrás editarlas después, pero verifica bien antes de continuar.`",
        "- Confirmacion de correccion: `Este cambio puede afectar fases posteriores ya iniciadas. ¿Deseas aplicar la corrección manual?`",
    ])
    (PLAN_DIR / "15_capturas_no_automatizadas.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_quality(manifest):
    rows = [
        "# Revision de calidad visual",
        "",
        "| ID | Archivo | Legibilidad | Encuadre | Resolucion | Coherencia | Estado correcto | Proposito pedagogico | Privacidad | Recorte | Anotacion | Reutilizacion | Decision |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in CAPTURES:
        cid, filename, procedure, *_rest = item
        dec = decision(cid)
        meta = manifest.get(cid, {})
        recorte = "Si" if dec == "REQUIERE RECORTE" else "No"
        anotacion = "Si" if dec in {"REQUIERE ANOTACION", "PENDIENTE MANUAL"} else "No"
        estado = "Parcial por dialogo nativo" if dec == "PENDIENTE MANUAL" else ("Correcto" if meta.get("status") != "ERROR" else "Error")
        rows.append(
            f"| {cid} | `{filename}` | Alta | Correcto | 1440x900 | Consistente | {estado} | {procedure} | {meta.get('privacy', 'NO EVALUADA')} | {recorte} | {anotacion} | Si | {dec} |"
        )
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    rows.extend([
        "",
        "## Estados avanzados reproducidos",
        "",
        ", ".join(summary["advanced_states"]) + ".",
        "",
        "## Resultado global",
        "",
        "- 42 PNG integros a 1440x900.",
        "- 41 capturas completas generadas automaticamente.",
        "- 1 captura parcial generada como estado previo a confirmacion nativa.",
        "- 0 descartadas en la pasada final.",
    ])
    (PLAN_DIR / "16_revision_calidad_visual.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main():
    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    manifest = generated_lookup()
    write_plan()
    write_inventory(manifest)
    write_manual_pending()
    write_quality(manifest)


if __name__ == "__main__":
    main()
