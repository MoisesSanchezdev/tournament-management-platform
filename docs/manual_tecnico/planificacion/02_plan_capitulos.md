# 02. Plan de capitulos

## Clasificacion

| Grupo | Capitulos |
| --- | --- |
| Nucleo conceptual | 1, 2, 3, 6, 23 |
| Nucleo tecnico | 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 |
| Aseguramiento de calidad | 17 |
| Produccion | 18, 19, 20 |
| Riesgo y evolucion | 21, 22 |
| Anexos | A, B, C, D, E, F, G, H, I |

## Plan editorial por capitulo

| Cap. | Proposito | Audiencia | Extension estimada | Auditoria fuente | Codigo a verificar si aplica | Tablas/figuras/diagramas | Riesgo de duplicacion | Criterio de aceptacion | Orden |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Abrir el manual | Todos | 2-3 paginas | 00, 24 | No requerido | Tabla de fuentes | Bajo | Contexto claro y sin detalle tecnico prematuro | 1 |
| 2 | Definir alcance | Todos | 3-4 paginas | 00, 24 | No requerido | Tabla de no confirmados | Medio | Limites y exclusiones explicitos | 2 |
| 3 | Describir sistema | Tecnico/funcional | 4-5 paginas | 00, 04 | URLs principales | Figura modulos | Medio | Dominios funcionales diferenciados | 3 |
| 4 | Explicar arquitectura | Desarrollador | 6-8 paginas | 01, 04, 06 | `config/urls.py`, apps | 4 diagramas | Alto | Capas, apps y flujo HTTP entendibles | 4 |
| 5 | Tecnologias | Desarrollador/ops | 3-5 paginas | 02, 03 | `requirements.txt`, settings | Tabla stack | Bajo | Solo tecnologias confirmadas | 5 |
| 6 | Requisitos | Tecnico/gestion | 4-6 paginas | Auditoria completa | No requerido | Tabla RF/RNF | Medio | Requisitos derivados de evidencia | 6 |
| 7 | Estructura | Desarrollador | 3-4 paginas | 01 | Arbol de archivos | Anexo A | Alto | Resumen sin duplicar arbol completo | 7 |
| 8 | Configuracion | Desarrollador/ops | 6-8 paginas | 03, 19 | `config/settings.py` | Tabla variables | Medio | Sin secretos ni valores reales | 8 |
| 9 | Apps Django | Desarrollador | 6-8 paginas | 04 | `apps/*` | Tabla apps | Alto | Responsabilidades y Admin claros | 9 |
| 10 | Datos | Desarrollador/DBA | 8-12 paginas | 05, 16 | `models.py`, migraciones | ER + tablas | Alto | Relaciones y JSON dinamico explicados | 10 |
| 11 | URLs/vistas/forms | Desarrollador | 8-10 paginas | 06, 07, 08 | `urls.py`, `views.py`, `forms.py` | Matriz endpoints | Alto | Trazabilidad ruta-vista-formulario | 11 |
| 12 | Servicios | Desarrollador senior | 10-14 paginas | 09, 24 | Servicios principales | Tabla contratos | Alto | Entradas, salidas y efectos colaterales | 12 |
| 13 | Competencia | Desarrollador/operador | 10-14 paginas | 10, 09 | `services.py`, `recommendations.py` | 6 diagramas | Alto | Escenarios normales y alternos cubiertos | 13 |
| 14 | Frontend/templates | Desarrollador frontend | 5-7 paginas | 11, 12, 14 | templates, CSS | Tabla templates | Medio | Acoplamientos JS visibles | 14 |
| 15 | JS/AJAX | Desarrollador frontend | 6-8 paginas | 13 | `control.js`, `app.js` | Flujo AJAX | Medio | Contratos `data-*` y endpoints claros | 15 |
| 16 | Seguridad | Tecnico/ops | 6-8 paginas | 15, 21 | settings, vistas protegidas | Tabla controles | Bajo | Riesgos y controles diferenciados | 16 |
| 17 | Pruebas | QA/desarrollador | 6-8 paginas | 18, 24 | tests existentes | Matriz pruebas | Bajo | Gaps convertidos en plan accionable | 17 |
| 18 | Despliegue | Ops | 6-8 paginas | 19 | settings, README existente solo consulta | Flujo despliegue | Medio | Lo no confirmado marcado | 18 |
| 19 | Mantenimiento | Ops/desarrollador | 5-7 paginas | 20, 21 | comandos/admin | Checklist | Medio | Acciones seguras y riesgos operativos | 19 |
| 20 | Respaldo | Ops | 4-6 paginas | 16, 19, 24 | No requerido | Flujo backup | Bajo | Politica pendiente no inventada | 20 |
| 21 | Riesgos | Responsable tecnico | 5-7 paginas | 21, 24 | No requerido | Matriz riesgos | Medio | Riesgos priorizados con mitigacion | 21 |
| 22 | Escalabilidad | Responsable tecnico | 4-6 paginas | 09, 19, 21 | Servicios criticos | Tabla limites | Bajo | Recomendaciones realistas | 22 |
| 23 | Conclusiones | Todos | 2-4 paginas | Manual validado | No requerido | Tabla recomendaciones | Bajo | Cierre coherente con evidencia | 23 |

## Subsecciones planificadas por capitulo

| Cap. | Subsecciones |
| --- | --- |
| 1 | Contexto institucional; proposito del manual; base documental; estado de auditoria |
| 2 | Objetivo general; objetivos especificos; alcance; exclusiones; informacion no confirmada |
| 3 | Vision general; actores; dominios funcionales; flujo operativo resumido |
| 4 | Arquitectura general; patron MTV; aplicaciones Django; dependencias; flujo HTTP |
| 5 | Stack confirmado; dependencias Python; frontend; servicios externos; tecnologias no confirmadas |
| 6 | Requisitos funcionales; requisitos no funcionales; requisitos operativos; restricciones |
| 7 | Raiz y carpetas; configuracion; apps; recursos estaticos; comandos y pruebas |
| 8 | Entorno local; variables; base de datos; static/media; correo; validaciones |
| 9 | `core`; `participants`; `tournament`; `invitations`; `common`; Django Admin |
| 10 | Modelo base; participantes; torneo; comunicaciones; restricciones; JSON dinamico |
| 11 | Rutas raiz; rutas publicas; rutas internas; vistas; formularios; permisos |
| 12 | Participantes; torneo; recomendaciones; invitaciones; contratos criticos |
| 13 | Inicializacion; grupos; eliminatorias; repechaje; correccion manual; podio |
| 14 | Layouts; templates publicos; panel interno; CSS; responsividad |
| 15 | `app.js`; `control.js`; contratos `data-*`; CSRF; guardado AJAX |
| 16 | Configuracion Django; autorizacion; CSRF; datos sensibles; riesgos |
| 17 | Pruebas existentes; gaps; matriz recomendada; validacion manual; criterios de aceptacion |
| 18 | Configuracion soportada; variables; static/media; correo; datos productivos pendientes; riesgos |
| 19 | Tareas recurrentes; comandos; Django Admin; precauciones; deuda tecnica |
| 20 | Situacion actual confirmada; procedimiento recomendado; politica pendiente; restauracion; pruebas |
| 21 | Riesgos tecnicos; riesgos funcionales; riesgos operativos; riesgos documentales; mitigaciones |
| 22 | Limites actuales; cuellos de botella; evolucion tecnica; recomendaciones |
| 23 | Estado final; condiciones de operacion; recomendaciones priorizadas; cierre |
