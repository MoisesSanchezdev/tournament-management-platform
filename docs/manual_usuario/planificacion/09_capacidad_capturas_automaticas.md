# Capacidad de capturas automaticas

## Clasificacion final Fase 2

**AUTOMATIZACION MAYORITARIA VIABLE.**

La Fase 2 demostro que no es necesario instalar Playwright ni Selenium para una automatizacion base de capturas. El entorno actual puede usar un navegador instalado en Windows, Node.js moderno y Chrome DevTools Protocol para abrir paginas, autenticar un usuario demo, navegar por `localhost`, capturar PNG y cerrar procesos.

No se declara automatizacion completa porque las 42 capturas definitivas todavia requieren curaduria visual, preparacion especifica de estados para fases avanzadas, control humano de riesgos y revision de datos sensibles antes de aprobar el banco final.

## Evidencia verificada

| Capacidad | Resultado | Evidencia |
| --- | --- | --- |
| Ejecutar Django normal | Disponible | `C:\Projects\pre_explotaglobos\.venv\Scripts\python.exe manage.py check` retorno sin errores al ejecutarse fuera del sandbox. |
| Base temporal aislada | Disponible | SQLite en `docs/manual_usuario/entorno_demo/datos/db_demo.sqlite3`. |
| Settings temporal | Disponible | `docs.manual_usuario.herramientas.demo_settings`, hereda de `config.settings` y solo reemplaza valores de demo. |
| Correo seguro | Disponible | `django.core.mail.backends.filebased.EmailBackend` con salida en `entorno_demo/mail_outbox`; SMTP vacio. |
| Media demo | Disponible | `docs/manual_usuario/entorno_demo/media`. |
| Node.js | Disponible | Node `v24.16.0`; `fetch`, `WebSocket` y `child_process` disponibles. |
| Microsoft Edge | Disponible | Detectado en `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`. Capturas CDP realizadas en modo headless. |
| Google Chrome | Disponible | Detectado en `C:\Program Files\Google\Chrome\Application\chrome.exe`. Edge fue usado como navegador primario por estar primero en rutas candidatas. |
| CDP | Disponible | Script sin dependencias externas conecto a `--remote-debugging-port=9225`. |
| `--screenshot` | No usado | La prueba uso `Page.captureScreenshot` por CDP para controlar sesion y autenticacion. |
| Interaccion autenticada | Disponible | El script completo login en `/torneo/control/login/` con usuario temporal. |
| Modal dinamico | Disponible | El script abrio modal de participante desde fase de grupos y capturo `POC-005-modal.png`. |
| Comunicaciones sin envio real | Disponible | Captura `POC-007-comunicaciones.png` muestra SMTP bloqueado y datos simulados. |

## Capturas POC obtenidas

Todas las capturas se guardaron en `docs/manual_usuario/capturas/prueba/` con 1440 x 900 px:

- `POC-001-inicio-publico.png`
- `POC-002-registro.png`
- `POC-003-panel-autenticado.png`
- `POC-004-control-torneo.png`
- `POC-005-modal.png`
- `POC-006-estado-visual.png`
- `POC-007-comunicaciones.png`

## Alcance automatizable estimado

Estimacion sobre las 42 capturas previstas en Fase 1: **36 capturas automatizables** con ampliacion del script CDP y datos demo preparados.

Automatizables con alta confianza:

- pantallas publicas;
- seleccion y formularios de registro en estados basicos;
- login interno;
- dashboard de torneo;
- division y fase de grupos;
- estado visual de tarjetas;
- modal de participante;
- dashboard de comunicaciones;
- listados de plantillas, invitaciones, confirmaciones e historial;
- varias pantallas Admin, si se agregan rutas al script y se controla el scroll.

Requieren intervencion humana o preparacion especial:

- capturas de errores especificos de formularios;
- confirmaciones nativas del navegador (`window.confirm`) para correcciones o reinicios;
- fases avanzadas que exigen estados competitivos muy precisos;
- validacion final de privacidad;
- recortes y anotaciones pedagogicas.

## Trabajo manual minimo restante

1. Aprobar el conjunto de datos demo definitivo para las 42 capturas.
2. Extender el script CDP con rutas y acciones por captura.
3. Revisar visualmente cada PNG antes de usarlo en el manual.
4. Hacer recortes y anotaciones despues de aprobar el banco base.
5. Evitar capturar operaciones destructivas o envios reales.
