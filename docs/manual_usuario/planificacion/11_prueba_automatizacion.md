# Prueba de automatizacion

## Navegadores detectados

| Navegador | Ruta | Version | Resultado |
| --- | --- | --- | --- |
| Microsoft Edge | `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` | No se obtuvo por stdout; ejecucion headless validada | Usado para la POC |
| Google Chrome | `C:\Program Files\Google\Chrome\Application\chrome.exe` | No se obtuvo por stdout; ejecutable detectado | Alternativa disponible |

Edge fue seleccionado porque fue el primer ejecutable encontrado por el script.

## Node.js y CDP

Node disponible:

```text
v24.16.0
```

APIs incorporadas verificadas:

- `fetch`: disponible;
- `WebSocket`: disponible;
- `child_process`: disponible.

No se uso `npm install`, no se creo `node_modules` y no se instalaron paquetes.

## Metodo probado

Script:

```text
docs/manual_usuario/herramientas/captura_automatica/cdp_capture_poc.js
```

Flujo:

1. Inicia Edge headless con `--remote-debugging-port=9225` y perfil temporal dentro de `entorno_demo`.
2. Conecta a Chrome DevTools Protocol usando `fetch` y `WebSocket` nativos de Node.
3. Fuerza viewport 1440 x 900 con `Emulation.setDeviceMetricsOverride`.
4. Navega por `localhost`.
5. Captura PNG mediante `Page.captureScreenshot`.
6. Completa login temporal con JavaScript ejecutado por CDP.
7. Navega a panel, comunicaciones y control de torneo.
8. Abre modal de participante desde fase de grupos.
9. Cierra navegador al terminar.

## Servidor Django

Servidor usado:

```text
127.0.0.1:8765
```

Comando:

```powershell
& C:\Projects\pre_explotaglobos\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8765 --noreload --settings=docs.manual_usuario.herramientas.demo_settings
```

El proceso se inicio solo durante la prueba y se cerro al finalizar.

## Resultado operativo

La automatizacion logro:

- abrir pagina publica;
- abrir pantalla de registro;
- autenticar usuario demo;
- capturar panel interno;
- capturar panel de comunicaciones sin SMTP real;
- navegar al control de torneo;
- capturar fase de grupos con estado visual;
- abrir y capturar modal dinamico de participante.

Limitacion observada:

- las capturas de estados muy especificos requieren preparar datos y acciones deterministas adicionales;
- las confirmaciones nativas del navegador deben manejarse caso por caso en el script.
