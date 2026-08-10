# 00. Indice maestro del Manual Tecnico

Estado general: PENDIENTE.

Este indice organiza la redaccion progresiva del manual. Cada capitulo debe redactarse desde la auditoria tecnica validada, codigo fuente solo cuando sea necesario y observaciones de `24_revision_calidad.md`.

| No. | Titulo | Objetivo | Contenido esperado | Fuente principal | Tablas requeridas | Figuras requeridas | Diagramas requeridos | Anexos | Dependencias | Profundidad | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Introduccion | Contextualizar el manual y el sistema | Antecedentes, alcance documental, base de auditoria, estado aprobado con observaciones | `00_resumen_ejecutivo.md`, `24_revision_calidad.md` | Tabla de fuentes base | Ninguna obligatoria | Ninguno | D | Ninguna | Media | PENDIENTE |
| 2 | Objetivos y alcance | Delimitar uso del manual | Objetivo general, objetivos especificos, alcance, exclusiones, informacion no confirmada | `00_resumen_ejecutivo.md`, `24_revision_calidad.md` | Tabla de exclusiones y no confirmados | Ninguna | Ninguno | D | 1 | Media | PENDIENTE |
| 3 | Descripcion del sistema | Explicar proposito y dominios funcionales | Registro, comunicaciones, torneo, panel interno, usuarios y responsabilidades | `00_resumen_ejecutivo.md`, `04_apps.md` | Tabla de dominios funcionales | Figura de modulos | Diagrama de alto nivel | D | 1, 2 | Media | PENDIENTE |
| 4 | Arquitectura | Describir organizacion tecnica | Django MTV, apps, capas, flujo HTTP, dependencias | `01_estructura_proyecto.md`, `04_apps.md`, `06_urls.md` | Tabla de capas y responsabilidades | Figura arquitectura | Arquitectura general, MTV, dependencias, peticion HTTP | A, D | 3 | Alta | PENDIENTE |
| 5 | Tecnologias | Inventariar stack confirmado | Python, Django, DB, frontend, correo, PDF, LibreOffice, dependencias externas | `02_tecnologias.md`, `03_configuracion.md` | Tabla de tecnologias | Ninguna | Ninguno | E | 4 | Media | PENDIENTE |
| 6 | Requisitos | Derivar requisitos del sistema existente | Requisitos funcionales, no funcionales, operativos y restricciones | Auditoria completa | Tabla RF/RNF | Ninguna | Ninguno | F, G | 3, 5 | Media | PENDIENTE |
| 7 | Estructura del proyecto | Explicar carpetas y archivos | Raiz, apps, config, static, templates, media, comandos, pruebas | `01_estructura_proyecto.md` | Tabla de carpetas | Ninguna | Arbol resumido opcional | A | 4 | Media | PENDIENTE |
| 8 | Instalacion y configuracion | Guiar preparacion tecnica | Entorno, variables, settings, DB, static/media, correo, validaciones | `03_configuracion.md`, `19_despliegue.md` | Variables de entorno | Ninguna | Flujo de configuracion | E, I | 5 | Alta | PENDIENTE |
| 9 | Aplicaciones Django | Explicar apps del proyecto | `core`, `participants`, `tournament`, `invitations`, `common`, Admin | `04_apps.md` | Tabla app/responsabilidad | Ninguna | Dependencias entre apps | D | 4, 7 | Alta | PENDIENTE |
| 10 | Modelo de datos | Documentar persistencia | Entidades, relaciones, enums, restricciones, JSON dinamico | `05_modelos.md`, `16_base_datos.md` | Resumen de entidades, campos criticos | Ninguna | Modelo entidad-relacion | B | 9 | Alta | PENDIENTE |
| 11 | URLs, vistas y formularios | Trazar interfaz backend | Rutas, vistas, permisos, POST, formularios y validaciones | `06_urls.md`, `07_views.md`, `08_forms.md` | Matriz endpoint/vista/form | Ninguna | Flujo HTTP | C | 9, 10 | Alta | PENDIENTE |
| 12 | Servicios y logica de negocio | Explicar contratos internos | Servicios de participantes, torneo, recomendaciones, invitaciones y efectos colaterales | `09_servicios.md`, `24_revision_calidad.md` | Tabla funcion/entrada/salida/efecto | Ninguna | Flujos de servicios criticos | D | 10, 11 | Alta | PENDIENTE |
| 13 | Flujo de competencia | Documentar flujo central | Inicializacion, grupos, eliminatorias, repechajes, fases manuales, podio | `10_flujo_competencia.md`, `09_servicios.md` | Estados y transiciones | Figura timeline | Grupos, eliminatorias, repechaje, correccion manual | F | 10, 12 | Alta | PENDIENTE |
| 14 | Frontend y templates | Explicar presentacion | Layouts, templates publicos/internos, CSS, componentes, responsividad | `11_templates.md`, `12_frontend.md`, `14_css.md` | Tabla template/proposito | Capturas futuras | Ninguno obligatorio | D | 11 | Media | PENDIENTE |
| 15 | JavaScript y AJAX | Documentar interacciones dinamicas | `app.js`, `control.js`, contratos `data-*`, CSRF, guardado AJAX | `13_javascript.md` | Matriz evento/endpoint/data | Ninguna | Flujo AJAX de guardado | C | 11, 14 | Alta | PENDIENTE |
| 16 | Seguridad | Describir controles y riesgos | Settings, autorizacion, CSRF, datos personales, correo, secretos | `15_seguridad.md`, `21_riesgos.md` | Tabla control/riesgo | Ninguna | Flujo de autorizacion opcional | E, I | 8, 11, 15 | Alta | PENDIENTE |
| 17 | Pruebas y calidad | Planificar QA | Pruebas existentes, gaps, matriz de pruebas, criterios de aceptacion | `18_pruebas.md`, `24_revision_calidad.md` | Matriz de pruebas | Ninguna | Flujo de validacion | F | 6, 12, 13 | Alta | PENDIENTE |
| 18 | Despliegue | Documentar despliegue soportado | Configuracion productiva, static/media, servidor no confirmado, correo, riesgos | `19_despliegue.md` | Checklist despliegue resumido | Ninguna | Flujo de despliegue | G, I | 8, 16 | Alta | PENDIENTE |
| 19 | Mantenimiento | Definir operacion recurrente | Tareas, comandos, Admin, precauciones, deuda tecnica | `20_mantenimiento.md`, `21_riesgos.md` | Tabla tarea/frecuencia/riesgo | Ninguna | Flujo mantenimiento correctivo | H, I | 12, 18 | Alta | PENDIENTE |
| 20 | Respaldo y recuperacion | Preparar continuidad operativa | Politica pendiente, backup DB/media, restauracion, pruebas de recuperacion | `16_base_datos.md`, `19_despliegue.md`, `24_revision_calidad.md` | Matriz backup/restauracion | Ninguna | Flujo respaldo/restauracion | G, H, I | 18, 19 | Media | PENDIENTE |
| 21 | Riesgos y limitaciones | Consolidar riesgos | Riesgos tecnicos, funcionales, operativos, documentales y mitigaciones | `21_riesgos.md`, `24_revision_calidad.md` | Matriz de riesgos | Ninguna | Mapa de riesgos opcional | D, H | Todos | Alta | PENDIENTE |
| 22 | Escalabilidad | Analizar evolucion | Cuellos de botella, servicios extensos, DB, frontend, despliegue, pruebas | `21_riesgos.md`, `09_servicios.md`, `19_despliegue.md` | Tabla limite/recomendacion | Ninguna | Ninguno obligatorio | D | 12, 18, 21 | Media | PENDIENTE |
| 23 | Conclusiones tecnicas | Cerrar dictamen tecnico | Estado del sistema, condiciones para operacion y recomendaciones priorizadas | Manual completo validado | Tabla recomendaciones | Ninguna | Ninguno | Todos | Todos | Media | PENDIENTE |

## Subsecciones planificadas

| Capitulo | Subsecciones previstas |
| --- | --- |
| 1. Introduccion | 1.1 Contexto institucional; 1.2 Proposito del manual; 1.3 Base documental; 1.4 Estado de la auditoria validada |
| 2. Objetivos y alcance | 2.1 Objetivo general; 2.2 Objetivos especificos; 2.3 Alcance tecnico; 2.4 Exclusiones; 2.5 Informacion no confirmada |
| 3. Descripcion del sistema | 3.1 Vision general; 3.2 Actores; 3.3 Dominios funcionales; 3.4 Flujo operativo resumido |
| 4. Arquitectura | 4.1 Arquitectura general; 4.2 Patron MTV; 4.3 Aplicaciones Django; 4.4 Dependencias; 4.5 Flujo HTTP |
| 5. Tecnologias | 5.1 Stack confirmado; 5.2 Dependencias Python; 5.3 Frontend; 5.4 Servicios externos; 5.5 Tecnologias no confirmadas |
| 6. Requisitos | 6.1 Requisitos funcionales; 6.2 Requisitos no funcionales; 6.3 Requisitos operativos; 6.4 Restricciones |
| 7. Estructura del proyecto | 7.1 Raiz y carpetas; 7.2 Configuracion; 7.3 Apps; 7.4 Recursos estaticos; 7.5 Comandos y pruebas |
| 8. Instalacion y configuracion | 8.1 Entorno local; 8.2 Variables; 8.3 Base de datos; 8.4 Static/media; 8.5 Correo; 8.6 Validaciones |
| 9. Aplicaciones Django | 9.1 `core`; 9.2 `participants`; 9.3 `tournament`; 9.4 `invitations`; 9.5 `common`; 9.6 Django Admin |
| 10. Modelo de datos | 10.1 Modelo base; 10.2 Participantes; 10.3 Torneo; 10.4 Comunicaciones; 10.5 Restricciones; 10.6 JSON dinamico |
| 11. URLs, vistas y formularios | 11.1 Rutas raiz; 11.2 Rutas publicas; 11.3 Rutas internas; 11.4 Vistas; 11.5 Formularios; 11.6 Permisos |
| 12. Servicios y logica de negocio | 12.1 Participantes; 12.2 Torneo; 12.3 Recomendaciones; 12.4 Invitaciones; 12.5 Contratos criticos |
| 13. Flujo de competencia | 13.1 Inicializacion; 13.2 Grupos; 13.3 Eliminatorias; 13.4 Repechaje; 13.5 Correccion manual; 13.6 Podio |
| 14. Frontend y templates | 14.1 Layouts; 14.2 Templates publicos; 14.3 Panel interno; 14.4 CSS; 14.5 Responsividad |
| 15. JavaScript y AJAX | 15.1 `app.js`; 15.2 `control.js`; 15.3 Contratos `data-*`; 15.4 CSRF; 15.5 Guardado AJAX |
| 16. Seguridad | 16.1 Configuracion Django; 16.2 Autorizacion; 16.3 CSRF; 16.4 Datos sensibles; 16.5 Riesgos |
| 17. Pruebas y calidad | 17.1 Pruebas existentes; 17.2 Gaps; 17.3 Matriz recomendada; 17.4 Validacion manual; 17.5 Criterios de aceptacion |
| 18. Despliegue | 18.1 Configuracion soportada; 18.2 Variables; 18.3 Static/media; 18.4 Correo; 18.5 Datos productivos pendientes; 18.6 Riesgos |
| 19. Mantenimiento | 19.1 Tareas recurrentes; 19.2 Comandos; 19.3 Django Admin; 19.4 Precauciones; 19.5 Deuda tecnica |
| 20. Respaldo y recuperacion | 20.1 Situacion actual confirmada; 20.2 Procedimiento recomendado; 20.3 Politica pendiente; 20.4 Restauracion; 20.5 Pruebas |
| 21. Riesgos y limitaciones | 21.1 Riesgos tecnicos; 21.2 Riesgos funcionales; 21.3 Riesgos operativos; 21.4 Riesgos documentales; 21.5 Mitigaciones |
| 22. Escalabilidad | 22.1 Limites actuales; 22.2 Cuellos de botella; 22.3 Evolucion tecnica; 22.4 Recomendaciones |
| 23. Conclusiones tecnicas | 23.1 Estado final; 23.2 Condiciones de operacion; 23.3 Recomendaciones priorizadas; 23.4 Cierre |
