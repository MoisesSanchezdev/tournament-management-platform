# Entorno demo del Manual de Usuario

Esta carpeta contiene una base SQLite temporal, archivos media demo, outbox local y credenciales ficticias ignoradas por Git.

No contiene datos reales ni debe usarse como entorno operativo del sistema.

Archivos esperados:

- `datos/db_demo.sqlite3`: base temporal creada con migraciones existentes.
- `media/`: archivos ficticios usados por pantallas de comunicacion.
- `mail_outbox/`: salida local de correo si se ejecutan flujos de correo en modo demo.
- `credenciales_demo.local.json`: credenciales ficticias del usuario temporal, ignoradas por Git.
- `evidencia_entorno_demo.json`: resumen tecnico de configuracion efectiva.
