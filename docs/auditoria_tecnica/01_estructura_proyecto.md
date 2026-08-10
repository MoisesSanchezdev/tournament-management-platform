# 01. Estructura del proyecto

## Raiz confirmada

Proyecto oficial: `C:\Projects\pre_explotaglobos`

## Arbol principal

```text
pre_explotaglobos/
  apps/
    common/
    core/
    invitations/
    participants/
    tournament/
  config/
  docs/
    correos/
    screenshots/
    auditoria_tecnica/
  logos_patrocinadores/
  media/
  static/
    css/
    docs/
    js/
    sponsors/
  manage.py
  requirements.txt
  README.md
  .env.example
  db.sqlite3
```

## Componentes por carpeta

| Ruta | Responsabilidad confirmada |
| --- | --- |
| `config/` | Configuracion central Django, URL raiz, ASGI y WSGI |
| `apps/common/` | Modelo abstracto reutilizable `TimeStampedModel` |
| `apps/core/` | Home publica, reglas y patrocinadores |
| `apps/participants/` | Registro publico, confirmacion de asistencia, sincronizacion a equipos |
| `apps/tournament/` | Dominio de torneo, formatos, planner, recomendaciones, servicios y panel interno |
| `apps/invitations/` | Plantillas DOCX, destinatarios, lotes, logs, envio de invitaciones y asistencia |
| `static/css/app.css` | Estilos publicos e internos |
| `static/js/app.js` | Interacciones publicas y tema |
| `static/js/control.js` | Interacciones del panel interno y AJAX |
| `static/docs/ExplotaGlobos.pdf` | Reglamento/documento publico embebido |
| `docs/screenshots/` | Capturas de referencia del README |
| `docs/correos/` | Plantillas y archivo XLSX de ejemplo para comunicaciones |

## Archivos de aplicacion

| App | Archivos principales |
| --- | --- |
| `core` | `views.py`, `urls.py`, `apps.py`, templates `home.html`, `rules.html`, `sponsors.html`, `base.html` |
| `participants` | `models.py`, `forms.py`, `views.py`, `services.py`, `urls.py`, `admin.py`, migraciones |
| `tournament` | `models.py`, `formats.py`, `planner.py`, `recommendations.py`, `services.py`, `views.py`, `urls.py`, comandos, migraciones, templates |
| `invitations` | `models.py`, `forms.py`, `services.py`, `views.py`, `urls.py`, comandos, migraciones, templates, tests |
| `common` | `models.py`, `apps.py`, paquete `migrations/` sin migraciones numeradas |

## Observaciones

1. Se detectan archivos `__pycache__` locales y bases SQLite ignoradas por `.gitignore`.
2. Existe una carpeta `.venv` operativa dentro del proyecto.
3. Existe una carpeta local cuyo nombre incluye una referencia a una copia de entorno virtual antigua; no fue utilizada para la auditoria.
4. `docs/auditoria_tecnica/` fue creada como unica carpeta de salida de esta auditoria.

## Mejora realizada en Fase 2

Se corrigio la descripcion de `apps/common`: no existe una migracion numerada inicial; solo se confirma el paquete `migrations/` con `__init__.py`.
