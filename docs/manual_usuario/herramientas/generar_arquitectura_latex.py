from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "planificacion"


CHAPTERS = [
    ("01_descripcion_general", "Descripción general", "Comprender el alcance funcional de la plataforma.", "Todos", "P-01", "MU-001"),
    ("02_acceso_navegacion", "Acceso y navegación", "Entrar al panel interno y reconocer la navegación principal.", "Organizador", "P-09", "MU-012"),
    ("03_sitio_publico", "Sitio público", "Consultar información pública, reglas y patrocinadores.", "Visitante", "P-01, P-02, P-03", "MU-001, MU-002, MU-003"),
    ("04_registro_participantes", "Registro de participantes", "Registrar equipos y confirmar asistencia con datos correctos.", "Participante", "P-04, P-05, P-06, P-07, P-08", "MU-004, MU-005, MU-006, MU-007, MU-008, MU-009, MU-010, MU-011"),
    ("05_gestion_organizacion", "Gestión de organización", "Ubicar el panel de organización y las divisiones del torneo.", "Organizador", "P-10", "MU-013, MU-014"),
    ("06_preparacion_competencia", "Preparación de competencia", "Configurar formato, grupos y distribución manual.", "Operador torneo", "P-10, P-11, P-12", "MU-015, MU-016, MU-017"),
    ("07_fase_grupos", "Fase de grupos", "Guardar clasificados de grupos y revisar resultados visibles.", "Operador torneo", "P-13, P-16", "MU-018, MU-019, MU-020"),
    ("08_eliminatorias_repechaje", "Eliminatorias y repechaje", "Operar batallas, clasificados múltiples, fase recomendada, repechaje y fase manual.", "Operador torneo", "P-14, P-15, P-17, P-18, P-19", "MU-021, MU-022, MU-023, MU-024, MU-025, MU-026, MU-027"),
    ("09_fases_finales_podio", "Fases finales y podio", "Registrar resultados finales y consultar el podio.", "Operador torneo", "P-22", "MU-031"),
    ("10_correcciones_manual_override", "Correcciones y confirmación manual", "Aplicar correcciones sensibles solo cuando el operador comprende el impacto.", "Operador torneo", "P-20, P-21", "MU-028, MU-029, MU-030"),
    ("11_comunicaciones", "Comunicaciones", "Gestionar plantillas, destinatarios, invitaciones, confirmaciones e historial.", "Operador comunicaciones", "P-23, P-24, P-25, P-26, P-27", "MU-032, MU-033, MU-034, MU-035, MU-036, MU-037, MU-038, MU-039"),
    ("12_django_admin", "Django Admin", "Revisar datos de soporte desde la administración solo cuando sea necesario.", "Superusuario", "P-28", "MU-040, MU-041, MU-042"),
    ("13_estados_mensajes", "Estados y mensajes", "Interpretar estados visuales, mensajes de éxito, error y advertencia.", "Todos", "Consulta transversal", "MU-006, MU-010, MU-011, MU-018, MU-026, MU-027"),
    ("14_problemas_frecuentes", "Problemas frecuentes", "Resolver errores operativos sin recurrir a explicación técnica.", "Todos", "Consulta transversal", "MU-006, MU-011, MU-028, MU-039"),
    ("15_recomendaciones_torneo", "Recomendaciones de operación del torneo", "Reducir riesgos antes, durante y después del evento.", "Organizador", "Consulta transversal", "MU-013, MU-020, MU-031"),
]


ANNEXES = [
    ("anexo_a_botones_acciones", "Botones y acciones", "Consulta rápida de botones principales y efecto esperado."),
    ("anexo_b_estados_visuales", "Estados visuales", "Resumen de estados pendiente, ganador, perdedor, clasificado y completado."),
    ("anexo_c_mensajes_respuestas", "Mensajes y respuestas", "Mensajes de confirmación, error, validación y advertencia."),
    ("anexo_d_checklist_previo", "Checklist previo al torneo", "Verificaciones antes de abrir operación real."),
    ("anexo_e_checklist_cierre", "Checklist de cierre", "Verificaciones al terminar competencia y comunicaciones."),
]


PROCEDURES = [
    ("P-01", "Consultar información pública del torneo", "Visitante", "03", "MU-001", "MU-001 puede reutilizarse como entrada general.", "No aplica", "Incluido"),
    ("P-02", "Consultar reglas oficiales y PDF", "Visitante", "03", "MU-002", "Referencia cruzada desde consulta pública.", "Verificar vigencia de reglas.", "Incluido"),
    ("P-03", "Consultar patrocinadores", "Visitante", "03", "MU-003", "Uso contextual.", "Marcas solo en entorno demo.", "Incluido"),
    ("P-04", "Elegir categoría de registro", "Participante", "04", "MU-004", "Entrada para escolar y universitario.", "Seleccionar categoría correcta.", "Incluido"),
    ("P-05", "Registrar robot escolar", "Participante", "04", "MU-005, MU-006, MU-008", "MU-006 cubre validación.", "Datos personales en operación real.", "Incluido"),
    ("P-06", "Registrar robot universitario", "Participante", "04", "MU-007, MU-008", "MU-008 se comparte con registro escolar.", "Semestre máximo.", "Incluido"),
    ("P-07", "Corregir errores de formulario antes de enviar", "Participante", "04", "MU-006", "Se referencia desde ambos registros.", "No insistir con datos duplicados.", "Incluido"),
    ("P-08", "Confirmar asistencia por token", "Participante", "04", "MU-009, MU-010, MU-011", "MU-011 cubre enlace inválido.", "No compartir tokens.", "Incluido"),
    ("P-09", "Iniciar sesión en panel interno", "Organizador", "02", "MU-012", "Se referencia desde módulos internos.", "No capturar credenciales.", "Incluido"),
    ("P-10", "Generar o asegurar tablero de competencia", "Operador torneo", "05, 06", "MU-013, MU-014, MU-015", "MU-013 contextual.", "No regenerar sin revisar progreso.", "Agrupado"),
    ("P-11", "Aplicar modo sugerido o formato manual", "Operador torneo", "06", "MU-015, MU-016", "MU-015 contextual.", "Impacta estructura inicial.", "Incluido"),
    ("P-12", "Ajustar distribución manual de grupos", "Operador torneo", "06", "MU-017", "Uso puntual.", "Mover equipos con cuidado.", "Incluido"),
    ("P-13", "Guardar clasificados de grupos", "Operador torneo", "07", "MU-018, MU-019", "MU-019 se resuelve editorialmente.", "Confirmación sensible.", "Incluido"),
    ("P-14", "Guardar ganador de batalla", "Operador torneo", "08", "MU-026", "Base para eliminatorias.", "Afecta fases posteriores.", "Incluido"),
    ("P-15", "Guardar clasificados múltiples de batalla", "Operador torneo", "08", "MU-027", "Base para campales.", "Respetar número requerido.", "Incluido"),
    ("P-16", "Usar guardado general de resultados", "Operador torneo", "07", "MU-020", "Referencia desde grupos y batallas.", "Guardar solo cambios revisados.", "Incluido"),
    ("P-17", "Crear fase recomendada", "Operador torneo", "08", "MU-021, MU-022", "MU-021 muestra modal general.", "No avanzar con resultados incompletos.", "Incluido"),
    ("P-18", "Crear repechaje", "Operador torneo", "08", "MU-023", "Secuencia del mismo modal.", "Evitar duplicar fases.", "Incluido"),
    ("P-19", "Generar y confirmar fase manual", "Operador torneo", "08", "MU-024, MU-025", "Procedimiento avanzado.", "Revisar propuesta antes de aceptar.", "Incluido"),
    ("P-20", "Corregir resultado con confirmación manual", "Operador torneo", "10", "MU-028", "Elemento editorial reusable.", "manual_override es sensible.", "Incluido"),
    ("P-21", "Editar estado de participante en modal", "Operador torneo", "10", "MU-029, MU-030", "MU-029 sirve como detalle.", "Evitar destinos incompatibles.", "Incluido"),
    ("P-22", "Guardar podio final", "Operador torneo", "09", "MU-031", "Cierre de competencia.", "No duplicar posiciones.", "Incluido"),
    ("P-23", "Gestionar plantillas de comunicación", "Operador comunicaciones", "11", "MU-033, MU-034, MU-035", "Secuencia completa.", "No subir archivos sensibles.", "Incluido"),
    ("P-24", "Gestionar destinatarios", "Operador comunicaciones", "11", "MU-036, MU-037", "MU-036 contextual.", "Correos reales en operación real.", "Incluido"),
    ("P-25", "Procesar invitaciones en simulación o prueba", "Operador comunicaciones", "11", "MU-032, MU-036, MU-039", "MU-032 entrada al módulo.", "Evitar envío real accidental.", "Incluido"),
    ("P-26", "Enviar solicitudes de asistencia", "Operador comunicaciones", "11", "MU-038", "Referencia desde asistencia.", "Confirmar modo dry-run/test.", "Incluido"),
    ("P-27", "Consultar historial de comunicaciones", "Operador comunicaciones", "11", "MU-039", "Tabla de auditoría.", "Privacidad de correos.", "Incluido"),
    ("P-28", "Revisar y corregir datos desde Django Admin", "Superusuario", "12", "MU-040, MU-041, MU-042", "Anexo de administración.", "Evitar cambios masivos no revisados.", "Incluido"),
]


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + "\n", encoding="utf-8")


def figure_for(captures: str) -> str:
    first = captures.split(",")[0].strip()
    filename = {
        "MU-001": "MU-001-inicio-publico.png",
        "MU-002": "MU-002-reglas-publicas.png",
        "MU-003": "MU-003-patrocinadores.png",
        "MU-004": "MU-004-seleccion-registro.png",
        "MU-005": "MU-005-registro-escolar.png",
        "MU-006": "MU-006-registro-escolar-error.png",
        "MU-007": "MU-007-registro-universitario.png",
        "MU-008": "MU-008-registro-exito.png",
        "MU-009": "MU-009-confirmacion-asistencia.png",
        "MU-010": "MU-010-asistencia-confirmada.png",
        "MU-011": "MU-011-token-invalido.png",
        "MU-012": "MU-012-login-panel.png",
        "MU-013": "MU-013-panel-torneo.png",
        "MU-014": "MU-014-generar-competencia.png",
        "MU-015": "MU-015-configuracion-division.png",
        "MU-016": "MU-016-formato-manual.png",
        "MU-017": "MU-017-distribucion-grupos.png",
        "MU-018": "MU-018-clasificados-grupo.png",
        "MU-019": "MU-019-guardar-grupo.png",
        "MU-020": "MU-020-guardar-todos.png",
        "MU-021": "MU-021-modal-siguiente-fase.png",
        "MU-022": "MU-022-crear-fase-recomendada.png",
        "MU-023": "MU-023-repechaje.png",
        "MU-024": "MU-024-asistente-manual.png",
        "MU-025": "MU-025-propuesta-manual.png",
        "MU-026": "MU-026-batalla-ganador.png",
        "MU-027": "MU-027-batalla-clasificados.png",
        "MU-028": "MU-028-confirmacion-correccion.png",
        "MU-029": "MU-029-modal-participante.png",
        "MU-030": "MU-030-edicion-participante.png",
        "MU-031": "MU-031-podio-final.png",
        "MU-032": "MU-032-dashboard-comunicaciones.png",
        "MU-033": "MU-033-lista-plantillas.png",
        "MU-034": "MU-034-nueva-plantilla.png",
        "MU-035": "MU-035-preview-plantilla.png",
        "MU-036": "MU-036-invitaciones-lote.png",
        "MU-037": "MU-037-destinatario-manual.png",
        "MU-038": "MU-038-confirmaciones-asistencia.png",
        "MU-039": "MU-039-historial-comunicaciones.png",
        "MU-040": "MU-040-admin-modelos.png",
        "MU-041": "MU-041-admin-registros.png",
        "MU-042": "MU-042-admin-torneo.png",
    }.get(first, "MU-001-inicio-publico.png")
    return rf"\figuraManual{{capturas/finales/{filename}}}{{Captura base {first} para este capítulo.}}{{fig:{first.lower()}}}"


def latex_files() -> None:
    write("manual_usuario.tex", r"""
\documentclass[11pt,a4paper,twoside,openany]{book}
\input{configuracion/paquetes}
\input{configuracion/colores}
\input{configuracion/estilo}
\input{configuracion/comandos}
\input{configuracion/metadatos}
\input{configuracion/hipervinculos}

\begin{document}
\frontmatter
\input{preliminares/portada}
\input{preliminares/control_versiones}
\input{preliminares/introduccion}
\input{preliminares/contenido}
\input{preliminares/lista_figuras}
\input{preliminares/convenciones}
\input{preliminares/perfiles_usuario}

\mainmatter
\input{capitulos/01_descripcion_general}
\input{capitulos/02_acceso_navegacion}
\input{capitulos/03_sitio_publico}
\input{capitulos/04_registro_participantes}
\input{capitulos/05_gestion_organizacion}
\input{capitulos/06_preparacion_competencia}
\input{capitulos/07_fase_grupos}
\input{capitulos/08_eliminatorias_repechaje}
\input{capitulos/09_fases_finales_podio}
\input{capitulos/10_correcciones_manual_override}
\input{capitulos/11_comunicaciones}
\input{capitulos/12_django_admin}
\input{capitulos/13_estados_mensajes}
\input{capitulos/14_problemas_frecuentes}
\input{capitulos/15_recomendaciones_torneo}

\appendix
\input{anexos/anexo_a_botones_acciones}
\input{anexos/anexo_b_estados_visuales}
\input{anexos/anexo_c_mensajes_respuestas}
\input{anexos/anexo_d_checklist_previo}
\input{anexos/anexo_e_checklist_cierre}
\end{document}
""")
    write("latexmkrc", r"""
$pdf_mode = 4;
$lualatex = 'lualatex -interaction=nonstopmode -halt-on-error %O %S';
$out_dir = 'build';
$aux_dir = 'build';
""")
    write(".gitignore", r"""
build/
*.aux
*.fdb_latexmk
*.fls
*.log
*.out
*.toc
*.lof
*.lot
*.synctex.gz
""")
    write("configuracion/paquetes.tex", r"""
\usepackage{fontspec}
\usepackage[spanish,es-nodecimaldot]{babel}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{longtable}
\usepackage{array}
\usepackage{enumitem}
\usepackage[most]{tcolorbox}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{caption}
\usepackage{float}
\usepackage{hyperref}
\usepackage[nameinlink,noabbrev]{cleveref}
""")
    write("configuracion/colores.tex", r"""
\definecolor{MUPrincipal}{HTML}{006D8F}
\definecolor{MUAdvertencia}{HTML}{B24A3B}
\definecolor{MUSegura}{HTML}{248A58}
\definecolor{MUTinta}{HTML}{1F2933}
\definecolor{MUFondo}{HTML}{F5F7FA}
\definecolor{MUBorde}{HTML}{D7DEE8}
""")
    write("configuracion/estilo.tex", r"""
\setmainfont{Latin Modern Roman}
\setsansfont{Latin Modern Sans}
\setmonofont{Latin Modern Mono}
\geometry{margin=2.4cm,inner=2.7cm,outer=2.1cm,headheight=15pt}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE,RO]{\thepage}
\fancyhead[LO]{\nouppercase{\rightmark}}
\fancyhead[RE]{\nouppercase{\leftmark}}
\titleformat{\chapter}{\Huge\bfseries\sffamily\color{MUPrincipal}}{\thechapter}{1em}{}
\titleformat{\section}{\Large\bfseries\sffamily\color{MUTinta}}{\thesection}{0.75em}{}
\captionsetup{font=small,labelfont=bf}
\setlist[itemize]{topsep=2pt,itemsep=2pt}
""")
    write("configuracion/comandos.tex", r"""
\newcommand{\estadoDocumento}{EN PREPARACIÓN}
\newcommand{\marcadorpendiente}{\textcolor{MUAdvertencia}{[Redacción pendiente]}}

\newtcolorbox{procedimiento}[2]{
  enhanced,
  colback=MUFondo,
  colframe=MUPrincipal,
  title={#1},
  fonttitle=\bfseries\sffamily,
  subtitle style={colback=MUBorde},
  before upper={\textbf{Perfil:} #2\par}
}
\newtcolorbox{precondiciones}{colback=white,colframe=MUBorde,title={Precondiciones}}
\newtcolorbox{resultadoesperado}{colback=white,colframe=MUSegura,title={Resultado esperado}}
\newtcolorbox{nota}{colback=MUFondo,colframe=MUPrincipal,title={Nota}}
\newtcolorbox{advertencia}{colback=white,colframe=MUAdvertencia,title={Advertencia}}
\newtcolorbox{operacionsensible}{colback=white,colframe=MUAdvertencia,title={Operación sensible}}
\newcommand{\paso}[2]{\par\textbf{Paso #1.} #2\par}
\newcommand{\capturasprevistas}[1]{\textbf{Capturas previstas:} #1\par}
\newcommand{\procedimientosprevistos}[1]{\textbf{Procedimientos previstos:} #1\par}
\newcommand{\figuraManual}[3]{%
  \begin{figure}[H]
    \centering
    \includegraphics[width=\linewidth,height=.62\textheight,keepaspectratio]{#1}
    \caption{#2}
    \label{#3}
  \end{figure}
}
""")
    write("configuracion/metadatos.tex", r"""
\newcommand{\TituloManual}{Manual de Usuario de la Plataforma Web Robot Explota Globos}
\newcommand{\Universidad}{Universidad Tecnológica de Pereira}
\newcommand{\SiglaUniversidad}{UTP}
\newcommand{\Semillero}{Semillero de Investigación Kilby}
\newcommand{\ResponsableManual}{Yurley Tatiana Tovar Martínez}
\newcommand{\DesarrolladoresManual}{Moisés Sánchez Naranjo\\Tomás Bermúdez Londoño}
\newcommand{\VersionManual}{0.1}
""")
    write("configuracion/hipervinculos.tex", r"""
\hypersetup{
  pdftitle={\TituloManual},
  pdfauthor={\Universidad},
  colorlinks=true,
  linkcolor=MUPrincipal,
  urlcolor=MUPrincipal,
  citecolor=MUPrincipal
}
\crefname{figure}{figura}{figuras}
\Crefname{figure}{Figura}{Figuras}
""")
    write("preliminares/portada.tex", r"""
\begin{titlepage}
\centering
\vspace*{2cm}
{\Huge\sffamily\bfseries \TituloManual\par}
\vspace{1.5cm}
{\Large \Universidad\ (\SiglaUniversidad)\par}
\vspace{0.5cm}
{\large \Semillero\par}
\vfill
\begin{tabular}{ll}
Responsable: & \ResponsableManual\\
Desarrolladores: & \begin{tabular}[t]{l}\DesarrolladoresManual\end{tabular}\\
Versión documental: & \VersionManual\\
Estado: & \estadoDocumento\\
\end{tabular}
\vfill
{\large \today\par}
\end{titlepage}
""")
    write("preliminares/control_versiones.tex", r"""
\chapter*{Control de versiones}
\begin{tabularx}{\linewidth}{llllX}
\toprule
Versión & Estado & Responsable & Fecha & Observaciones\\
\midrule
0.1 & EN PREPARACIÓN & Yurley Tatiana Tovar Martínez & \today & Arquitectura documental y banco visual final.\\
\bottomrule
\end{tabularx}
""")
    write("preliminares/introduccion.tex", r"""
\chapter*{Introducción}
Este documento será el manual de uso de la plataforma. En esta fase se define la arquitectura editorial, la estructura de capítulos y el banco visual definitivo.

\marcadorpendiente
""")
    write("preliminares/contenido.tex", r"""
\tableofcontents
""")
    write("preliminares/lista_figuras.tex", r"""
\listoffigures
""")
    write("preliminares/convenciones.tex", r"""
\chapter*{Convenciones del manual}
\begin{nota}
Las capturas finales usan datos ficticios y marcadores numerados discretos. Las explicaciones largas se ubicarán en el texto o en el pie de figura, no dentro de la imagen.
\end{nota}
""")
    write("preliminares/perfiles_usuario.tex", r"""
\chapter*{Perfiles de usuario}
\begin{itemize}
\item Visitante.
\item Participante.
\item Organizador.
\item Operador de torneo.
\item Operador de comunicaciones.
\item Superusuario.
\end{itemize}
\marcadorpendiente
""")

    for filename, title, objective, profile, procedures, captures in CHAPTERS:
        body = rf"""
\chapter{{{title}}}
\begin{{procedimiento}}{{Objetivo del capítulo}}{{{profile}}}
{objective}
\end{{procedimiento}}
\procedimientosprevistos{{{procedures}}}
\capturasprevistas{{{captures}}}
{figure_for(captures)}
\section{{Procedimientos incluidos}}
\marcadorpendiente
\section{{Precondiciones}}
\marcadorpendiente
\section{{Pasos previstos}}
\marcadorpendiente
\section{{Resultado esperado}}
\marcadorpendiente
"""
        if filename == "07_fase_grupos":
            body += "\n\\input{elementos_editoriales/confirmacion_operacion_sensible}\n"
        if filename == "10_correcciones_manual_override":
            body += "\n\\input{elementos_editoriales/confirmacion_manual_override}\n"
        write(f"capitulos/{filename}.tex", body)

    for filename, title, summary in ANNEXES:
        write(f"anexos/{filename}.tex", rf"""
\chapter{{{title}}}
{summary}

\marcadorpendiente
""")
    write("elementos_editoriales/confirmacion_operacion_sensible.tex", r"""
\begin{operacionsensible}
\textbf{Confirmación nativa de guardado de resultados.}
La apariencia exacta del diálogo depende del navegador y del sistema operativo. Texto exacto documentado:
\emph{¿Seguro que deseas guardar estas selecciones? Podrás editarlas después, pero verifica bien antes de continuar.}

Opciones reales: aceptar o cancelar. Al aceptar, la operación se envía al servidor. Al cancelar, no se guardan los cambios. Recomendación: revisar selección, grupo y cantidad de clasificados antes de aceptar.
\end{operacionsensible}
""")
    write("elementos_editoriales/confirmacion_manual_override.tex", r"""
\begin{operacionsensible}
\textbf{Confirmación nativa de corrección manual.}
La apariencia exacta del diálogo depende del navegador y del sistema operativo. Texto exacto documentado:
\emph{Este cambio puede afectar fases posteriores ya iniciadas. ¿Deseas aplicar la corrección manual?}

Opciones reales: aceptar o cancelar. Al aceptar, se envía la corrección con \texttt{manual\_override}. Al cancelar, se conserva el resultado anterior. Recomendación: usarlo solo como contingencia operativa documentada.
\end{operacionsensible}
""")


def planning_docs() -> None:
    manifest = json.loads((ROOT / "capturas" / "finales" / "metadata_capturas_finales.json").read_text(encoding="utf-8-sig"))
    recortes = [item for item in manifest if item["tipo"] == "RECORTE"]
    anotaciones = [item for item in manifest if item["tipo"] == "ANOTACION"]
    previas = [item for item in manifest if item["tipo"] == "CAPTURA_PREVIA_DIALOGO_NATIVO"]

    rows = [
        "# Índice funcional del Manual de Usuario",
        "",
        "| Capítulo | Objetivo del usuario | Perfil | Procedimientos | Capturas | Advertencias | Prerrequisitos | Resultado esperado | Extensión | Anexos | Estado |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for index, (_filename, title, objective, profile, procedures, captures) in enumerate(CHAPTERS, start=1):
        warn = "Operación sensible" if index in {7, 8, 10, 11, 12} else "Sin advertencia especial"
        prereq = "Datos demo o sesión según perfil"
        expected = "Usuario completa o comprende el flujo sin apoyo técnico"
        pages = "3-7"
        annex = "A-E según consulta"
        rows.append(f"| {index:02d}. {title} | {objective} | {profile} | {procedures} | {captures} | {warn} | {prereq} | {expected} | {pages} pág. | {annex} | Pendiente de redacción |")
    write("planificacion/17_indice_manual_usuario.md", "\n".join(rows))

    write("planificacion/18_guia_visual.md", f"""
# Guía visual del Manual de Usuario

## Paleta

| Uso | Color | Valor |
| --- | --- | --- |
| Resaltado principal | Azul petróleo | `#006D8F` |
| Advertencia | Rojo sobrio | `#B24A3B` |
| Acción segura | Verde operativo | `#248A58` |
| Texto | Gris tinta | `#1F2933` |
| Fondo auxiliar | Gris claro | `#F5F7FA` |

## Marcadores

- Recuadro de 3 px, opacidad de relleno aproximada del 5 %.
- Círculo numerado de 38 px.
- Máximo de 4 marcadores por imagen.
- Las etiquetas largas no se insertan en el PNG; se explican en pie de figura o texto.
- Flechas solo si el recuadro no identifica claramente la acción.

## Capturas

- Página completa: ancho máximo de línea en LaTeX.
- Recorte: mantener encabezado o contexto suficiente.
- Modal: centrar el diálogo y conservar el fondo necesario.
- Secuencia: usar numeración de figura y referencia cruzada.
- Márgenes: evitar bordes cortados y conservar botones completos.
""")

    matrix = [
        "# Matriz procedimientos-capturas",
        "",
        "| Procedimiento | Perfil | Capítulo | Capturas | Reutilización | Advertencia | Estado |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for proc in PROCEDURES:
        matrix.append("| " + " | ".join(proc) + " |")
    matrix.append("\nTotal: 28 procedimientos incluidos o agrupados justificadamente. No hay procedimientos obligatorios sin capítulo.")
    write("planificacion/19_matriz_procedimientos_capturas.md", "\n".join(matrix))

    pages = [
        "# Mapa de páginas estimado",
        "",
        "| Bloque | Páginas | Figuras | Tablas | Riesgo editorial |",
        "| --- | ---: | ---: | ---: | --- |",
        "| Preliminares | 6 | 0 | 1 | Breve, suficiente |",
    ]
    total_pages = 6
    total_figures = 0
    estimates = [4, 4, 5, 7, 4, 5, 5, 7, 4, 5, 8, 5, 4, 4, 4]
    for idx, chapter in enumerate(CHAPTERS, start=1):
        figs = len([x for x in chapter[5].split(",") if x.strip()])
        total_pages += estimates[idx - 1]
        total_figures += figs
        risk = "Revisar longitud" if estimates[idx - 1] >= 8 else "Controlado"
        pages.append(f"| Capítulo {idx:02d}. {chapter[1]} | {estimates[idx - 1]} | {figs} | 0-1 | {risk} |")
    pages.append("| Anexos | 8 | 0 | 5 | Mantener como consulta, no duplicar procedimientos |")
    total_pages += 8
    pages.append("")
    pages.append(f"Total esperado: **{total_pages} páginas**, **{total_figures} figuras referenciadas en capítulos** y tablas principalmente en anexos. Rango editorial objetivo: 55 a 90 páginas.")
    write("planificacion/20_mapa_paginas_estimado.md", "\n".join(pages))

    review = [
        "# Revisión del procesamiento visual",
        "",
        f"- Imágenes finales creadas: {len(manifest)}.",
        f"- Recortes aplicados: {len(recortes)}.",
        f"- Anotaciones aplicadas: {len(anotaciones)}.",
        f"- Confirmaciones resueltas editorialmente: {len(previas)}.",
        "- Imágenes rechazadas: 0.",
        "- Privacidad: OK; datos ficticios y correos `example.com`.",
        "- Consistencia: marcadores uniformes, recortes conservadores y rutas relativas.",
        "",
        "## Recortes",
        "",
        "| ID | Archivo | Original | Final | Región | Justificación |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in recortes:
        review.append(f"| {item['id']} | `{item['archivo']}` | {item['original']} | {item['final']} | {item['region']} | {item['justificacion']} |")
    review.extend(["", "## Anotaciones", "", "| ID | Archivo | Marcadores | Justificación |", "| --- | --- | ---: | --- |"])
    for item in anotaciones:
        review.append(f"| {item['id']} | `{item['archivo']}` | {item['marcadores']} | {item['justificacion']} |")
    review.extend(["", "## Confirmaciones editoriales", ""])
    for item in previas:
        review.append(f"- {item['id']} `{item['archivo']}`: {item['justificacion']}")
    review.extend(["", "## Decisión", "", "**BANCO VISUAL APROBADO CON AJUSTES MENORES.** Ajustes menores: revisar pies de figura durante la redacción para explicar los marcadores numerados."])
    write("planificacion/21_revision_procesamiento_visual.md", "\n".join(review))

    write("planificacion/22_plan_redaccion.md", """
# Plan de redacción

| Bloque | Archivos | Procedimientos | Capturas | Criterios de aceptación | Dependencias | Riesgo de redundancia |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Preliminares, navegación y sitio público | `preliminares/*`, capítulos 01-03 | P-01, P-02, P-03, P-09 | MU-001 a MU-003, MU-012 | Usuario entiende alcance, perfiles y navegación | Banco visual final | Repetir descripción general |
| 2. Registro, organización y equipos | capítulos 04-06 | P-04 a P-12 | MU-004 a MU-017 | Registro y preparación quedan explicados por flujo | Capturas recortadas | Repetir validaciones |
| 3. Competencia | capítulos 07-09 | P-13 a P-19, P-22 | MU-018 a MU-027, MU-031 | Grupos, batallas, repechaje y podio quedan conectados | Elemento de confirmación sensible | Capítulos largos |
| 4. Correcciones, comunicaciones y Admin | capítulos 10-12 | P-20, P-21, P-23 a P-28 | MU-028 a MU-042 | Operaciones sensibles y administrativas diferenciadas | Elemento manual_override | Exceso de detalle técnico |
| 5. Estados, problemas y recomendaciones | capítulos 13-15, anexos | Consulta transversal | Referencias cruzadas | Consulta breve y no repetitiva | Capítulos previos redactados | Convertir anexos en manual paralelo |
| 6. Revisión editorial y publicación | todos | Todos | Todas | Consistencia, privacidad y compilación | Redacción completa | Ajustes de paginación |
""")


def readme() -> None:
    write("README.md", """
# Manual de Usuario

Estructura documental del Manual de Usuario de la Plataforma Web Robot Explota Globos.

## Estado

Versión documental inicial: 0.1. Estado: EN PREPARACIÓN.

## Compilación prevista

Motor objetivo: LuaLaTeX, sin `shell-escape`.

```powershell
lualatex -interaction=nonstopmode -halt-on-error manual_usuario.tex
```

Si `latexmk` está disponible:

```powershell
latexmk manual_usuario.tex
```

## Banco visual

- Capturas base: `capturas/base/`.
- Capturas finales procesadas: `capturas/finales/`.
- Pruebas POC conservadas: `capturas/prueba/`.
""")


def main() -> None:
    latex_files()
    planning_docs()
    readme()


if __name__ == "__main__":
    main()
