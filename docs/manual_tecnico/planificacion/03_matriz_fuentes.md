# 03. Matriz de fuentes

Esta matriz evita contenido inventado. Todo capitulo debe sostenerse en auditoria, codigo fuente verificado o decision editorial registrada.

| Capitulo | Seccion prevista | Documento fuente | Codigo fuente | Tipo de evidencia | Confianza | Verificacion adicional | Figura | Tabla | Anexo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Contexto | 00, 24 | No aplica | Auditoria validada | Alta | No | No | Si | D |
| 2 | Alcance/no confirmados | 00, 02, 03, 19, 24 | No aplica | Dictamen documental | Alta | Confirmacion humana para produccion | No | Si | D |
| 3 | Dominios | 00, 04 | `apps/*` si hay duda | Auditoria + estructura | Alta | Baja | Si | Si | D |
| 4 | Arquitectura | 01, 04, 06 | `config/urls.py`, `apps/*/urls.py` | Codigo + auditoria | Alta | Media para diagramas | Si | Si | A, D |
| 5 | Stack | 02, 03 | `requirements.txt`, `config/settings.py` | Archivos de configuracion | Alta | Confirmar produccion | No | Si | E |
| 6 | Requisitos | Auditoria completa | Codigo si se derivan reglas | Inferencia documentada | Media | Alta | No | Si | F |
| 7 | Estructura | 01 | Arbol de repo | Inventario de archivos | Alta | Actualizar antes de publicar | No | Si | A |
| 8 | Configuracion | 03, 19 | `config/settings.py` | Codigo + auditoria | Alta | No incluir secretos | No | Si | E, I |
| 9 | Apps | 04 | `apps/*/apps.py`, `admin.py` | Codigo + auditoria | Alta | Revisar Admin si cambia | No | Si | D |
| 10 | Datos | 05, 16, 17 | `models.py`, migraciones | Codigo + migraciones | Alta | Detallar `configuration` | No | Si | B |
| 11 | URLs/vistas/forms | 06, 07, 08 | `urls.py`, `views.py`, `forms.py` | Codigo + auditoria | Alta | Validar permisos y metodos | No | Si | C |
| 12 | Servicios | 09, 24 | `services.py`, `formats.py`, `recommendations.py` | Codigo + auditoria | Media | Profundizar contratos | No | Si | D |
| 13 | Competencia | 10, 09, 24 | `tournament/services.py`, `recommendations.py` | Codigo + flujos | Media | Escenarios alternos | Si | Si | F |
| 14 | Templates/frontend | 11, 12, 14 | `templates/`, `static/css/app.css` | Archivos frontend | Alta | Capturas si se requieren | Si | Si | D |
| 15 | JS/AJAX | 13 | `static/js/app.js`, `static/js/control.js` | Codigo JS | Media | Matriz `data-*` | No | Si | C |
| 16 | Seguridad | 15, 21 | settings, vistas protegidas | Configuracion + codigo | Alta | Revisar secretos | No | Si | E, I |
| 17 | Pruebas | 18, 24 | `apps/*/tests.py` | Tests existentes | Alta | Plan E2E pendiente | No | Si | F |
| 18 | Despliegue | 19, 03 | settings, archivos operativos | Documental | Media | Confirmar servidor real | No | Si | G, I |
| 19 | Mantenimiento | 20, 21 | management commands, admin | Codigo + auditoria | Alta | Identificar comandos riesgosos | No | Si | H, I |
| 20 | Respaldo | 16, 19, 24 | No aplica | Riesgo/documental | Media | Politica humana | No | Si | G, H |
| 21 | Riesgos | 21, 24 | Codigo critico si se necesita | Auditoria validada | Alta | Repriorizar al final | No | Si | D, H |
| 22 | Escalabilidad | 09, 16, 19, 21 | Servicios y DB | Analisis tecnico | Media | Validar supuestos | No | Si | D |
| 23 | Conclusiones | Manual completo | No aplica | Sintesis validada | Media | Despues de QA | No | Si | Todos |
