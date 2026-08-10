# 23. Trazabilidad

## Fuentes revisadas

| Area | Archivos |
| --- | --- |
| Configuracion | `config/settings.py`, `config/urls.py`, `.env.example`, `.gitignore`, `requirements.txt` |
| Core | `apps/core/views.py`, `apps/core/urls.py`, templates core |
| Participantes | `apps/participants/models.py`, `forms.py`, `views.py`, `services.py`, `urls.py`, `admin.py`, migraciones |
| Torneo | `apps/tournament/models.py`, `formats.py`, `planner.py`, `recommendations.py`, `services.py`, `views.py`, `urls.py`, `admin.py`, comandos, tests, migraciones, templates |
| Invitaciones | `apps/invitations/models.py`, `forms.py`, `services.py`, `views.py`, `urls.py`, `admin.py`, comandos, tests, migraciones, templates |
| Frontend | `static/css/app.css`, `static/js/app.js`, `static/js/control.js` |
| Documentacion previa | `README.md` |

## Trazabilidad por documento

| Documento | Evidencia principal |
| --- | --- |
| `00_resumen_ejecutivo.md` | Git, settings, requirements, apps, manage.py check |
| `01_estructura_proyecto.md` | `rg --files`, listado de directorios |
| `02_tecnologias.md` | `requirements.txt`, settings, services |
| `03_configuracion.md` | `config/settings.py`, `.env.example`, `.gitignore` |
| `04_apps.md` | `INSTALLED_APPS`, `apps.py`, imports y relaciones |
| `05_modelos.md` | `models.py`, migraciones |
| `06_urls.md` | `config/urls.py`, `apps/*/urls.py` |
| `07_views.md` | `views.py` de cada app |
| `08_forms.md` | `forms.py` de participants e invitations |
| `09_servicios.md` | `services.py`, `formats.py`, `planner.py`, `recommendations.py` |
| `10_flujo_competencia.md` | `apps/tournament/services.py`, `formats.py`, `recommendations.py` |
| `11_templates.md` | Templates Django |
| `12_frontend.md` | Templates base, CSS, JS |
| `13_javascript.md` | `static/js/app.js`, `static/js/control.js` |
| `14_css.md` | `static/css/app.css` |
| `15_seguridad.md` | `settings.py`, decorators, forms, services, `.gitignore` |
| `16_base_datos.md` | `settings.py`, modelos, migraciones |
| `17_migraciones.md` | `apps/*/migrations/*.py` |
| `18_pruebas.md` | `apps/tournament/tests.py`, `apps/invitations/tests.py` |
| `19_despliegue.md` | README, settings, requirements |
| `20_mantenimiento.md` | Comandos de gestion y estructura |
| `21_riesgos.md` | Hallazgos transversales |
| `22_glosario.md` | Nombres de modelos, enums y servicios |
| `24_revision_calidad.md` | Revision cruzada de Fase 2 y decision de aprobacion |

## Comandos ejecutados

| Comando | Proposito | Modifica estado |
| --- | --- | --- |
| `Get-Location` | Confirmar ruta | No |
| `git rev-parse --show-toplevel` | Confirmar raiz repo | No |
| `git status` | Estado Git | No |
| `git branch --show-current` | Rama actual | No |
| `git log -5 --oneline` | Historial reciente | No |
| `python -c "import sys; print(sys.executable)"` | Python de shell | No |
| `.venv\Scripts\python.exe -c "import sys; print(sys.executable)"` | Python de proyecto | No |
| `.venv\Scripts\python.exe manage.py check` | Validacion Django | No |
| `rg --files` | Inventario | No |
| `Get-Content` | Lectura de archivos | No |

## Comandos no ejecutados

| Comando | Motivo |
| --- | --- |
| `migrate` | Prohibido modificar base |
| `makemigrations` | Prohibido modificar migraciones |
| `collectstatic` | Prohibido generar/modificar salida funcional |
| `test` | Evitado para no crear base de pruebas ni alterar estado |
| `commit` / `push` | Prohibido |

## Validacion final requerida

Debe ejecutarse `git status` al terminar la escritura documental para confirmar que solo existen archivos nuevos en `docs/auditoria_tecnica/`.

## Mejora realizada en Fase 2

Se amplio la trazabilidad para incluir `admin.py` de `tournament` e `invitations`, y se agrego la referencia del documento `24_revision_calidad.md`.
