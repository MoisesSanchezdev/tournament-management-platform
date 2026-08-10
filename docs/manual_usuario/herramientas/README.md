# Herramientas documentales temporales

Estos scripts pertenecen a la preparacion del Manual de Usuario. No son funcionalidad del sistema.

Uso esperado desde `C:\Projects\pre_explotaglobos`:

```powershell
& .\.venv\Scripts\python.exe docs\manual_usuario\herramientas\preparar_entorno_demo.py
& .\.venv\Scripts\python.exe manage.py migrate --settings=docs.manual_usuario.herramientas.demo_settings
& .\.venv\Scripts\python.exe docs\manual_usuario\herramientas\poblar_datos_demo.py
& .\.venv\Scripts\python.exe docs\manual_usuario\herramientas\verificar_entorno_demo.py
node docs\manual_usuario\herramientas\captura_automatica\cdp_capture_poc.js
```

Restricciones:

- no instalar dependencias;
- no usar la base oficial;
- no enviar correos reales;
- no copiar datos reales;
- no modificar codigo funcional del proyecto.
