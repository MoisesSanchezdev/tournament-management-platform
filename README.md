# Torneo Robot Explota Globos

Aplicación web desarrollada con Django para apoyar la gestión del torneo Robot Explota Globos UTP. El sistema centraliza información pública del evento, registro de participantes y herramientas operativas para organizar ediciones, fases y enfrentamientos.

Este repositorio se presenta como proyecto de portafolio y como base técnica para digitalizar procesos del torneo, manteniendo una separación clara entre configuración local, datos sensibles y código versionado.

## Contexto

Robot Explota Globos es una competencia de robótica en la que equipos de colegios y universidades participan con robots diseñados para cumplir las reglas oficiales del evento. Este proyecto fue desarrollado para apoyar la gestión del torneo Robot Explota Globos UTP, especialmente en el registro de robots, publicación de reglas y organización inicial de la competencia.

El archivo `static/docs/ExplotaGlobos.pdf` se conserva en el repositorio porque contiene las reglas oficiales del torneo.

## Funcionalidades principales

- Página pública de inicio y consulta de reglas del torneo.
- Registro diferenciado para robots de colegios y universidades.
- Validación de inscripciones por edición activa.
- Prevención de duplicados por robot, correo y documento del líder.
- Envío configurable de correos de confirmación.
- Modelado de ediciones, fases y enfrentamientos.
- Panel interno para gestión operativa del torneo.
- Configuración por variables de entorno para desarrollo y producción.
- Soporte para SQLite en desarrollo local y PostgreSQL en entornos productivos.

## Stack tecnológico

- Python
- Django 5.2 LTS
- PostgreSQL
- SQLite para desarrollo local
- HTML, CSS y JavaScript
- python-dotenv
- psycopg

## Estructura del proyecto

- `config/`: configuración central de Django, rutas principales, WSGI y ASGI.
- `apps/core/`: páginas públicas, inicio, reglas y patrocinadores.
- `apps/participants/`: formularios, modelos, vistas y servicios de inscripción.
- `apps/tournament/`: modelos y vistas para ediciones, fases, enfrentamientos y panel interno.
- `apps/common/`: componentes reutilizables del dominio.
- `static/css/`: estilos públicos del sitio.
- `static/js/`: scripts del sistema.
- `static/docs/`: documentos públicos del torneo, incluyendo el reglamento oficial.
- `static/sponsors/`: recursos visuales de patrocinadores y contexto del evento.
- `logos_patrocinadores/`: logos usados como referencia visual del torneo.

## Instalación local

1. Clona el repositorio.
2. Crea y activa un entorno virtual de Python.
3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

4. Copia el archivo de ejemplo de variables de entorno:

```bash
cp .env.example .env
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

5. Ajusta los valores de `.env` según tu entorno local.

Para desarrollo rápido puedes usar SQLite con:

```env
DJANGO_DEBUG=True
DJANGO_DATABASE=sqlite
```

Para un entorno más cercano a producción, configura PostgreSQL con las variables `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` y `POSTGRES_PORT`.

## Variables de entorno

El archivo `.env.example` documenta las variables necesarias para levantar el proyecto localmente:

- `DJANGO_SECRET_KEY`: clave secreta local o de producción.
- `DJANGO_DEBUG`: activa o desactiva el modo debug.
- `DJANGO_ALLOWED_HOSTS`: hosts permitidos por Django.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: orígenes confiables para protección CSRF.
- `DJANGO_DATABASE`: motor esperado para desarrollo local, por ejemplo `sqlite`.
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`: configuración de PostgreSQL.
- `DJANGO_EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, `DEFAULT_FROM_EMAIL`: configuración de correo.

No subas archivos `.env` reales al repositorio. El archivo `.env.example` debe contener solo placeholders seguros.

## Comandos principales

Crear migraciones:

```bash
python manage.py makemigrations
```

Aplicar migraciones:

```bash
python manage.py migrate
```

Crear usuario administrador:

```bash
python manage.py createsuperuser
```

Ejecutar servidor local:

```bash
python manage.py runserver
```

Verificar configuración de despliegue:

```bash
python manage.py check --deploy
```

## Seguridad y privacidad

Este proyecto está preparado para mantener fuera del repositorio archivos sensibles o locales:

- `.env` está ignorado y no debe publicarse.
- `db.sqlite3` y archivos `*.sqlite3` están ignorados.
- Entornos virtuales, cachés, logs y archivos temporales están ignorados.
- Las credenciales reales de correo, base de datos y claves secretas deben configurarse mediante variables de entorno.

No uses datos reales de estudiantes, colegios, universidades, documentos, correos o participantes en una base de datos que vaya a publicarse. Para demos o portafolio, usa datos ficticios o semillas controladas.

## Logos y recursos visuales

Los logos incluidos corresponden al contexto visual del torneo, semillero, institución o patrocinadores. Deben usarse respetando los permisos institucionales o de las organizaciones correspondientes.

Si el repositorio se reutiliza fuera del contexto del torneo Robot Explota Globos UTP, revisa primero si esos recursos pueden mantenerse, reemplazarse o retirarse.

## Estado actual

El proyecto cuenta con una base funcional para registro público y administración inicial del torneo. Incluye modelos de inscripción, participantes, ediciones, reglas, fases y enfrentamientos, además de configuración por variables de entorno y medidas básicas de seguridad para despliegue.

Estado recomendado para portafolio:

- Código funcional como demostración técnica.
- README orientado a instalación y revisión del proyecto.
- Variables sensibles documentadas mediante `.env.example`.
- Archivos locales y secretos excluidos mediante `.gitignore`.
- Reglamento oficial disponible en `static/docs/ExplotaGlobos.pdf`.

## Roadmap

1. Diseñar la conversión de inscripciones aprobadas a equipos oficiales del torneo.
2. Definir el formato final de fases, clasificación y playoffs.
3. Crear flujos operativos para aprobación, check-in y resultados.
4. Incorporar pruebas automáticas para modelos, formularios y vistas críticas.
5. Añadir datos demo seguros para presentación pública.
6. Documentar una guía de despliegue con PostgreSQL, archivos estáticos y servidor WSGI/ASGI.
7. Revisar permisos de uso de logos y recursos visuales antes de reutilizar el proyecto en otro contexto.

## Nota para portafolio

Este repositorio muestra una solución Django aplicada a un caso real de gestión de torneo: registro de participantes, estructura de dominio, configuración por entorno y primeras medidas de seguridad para publicación. Antes de usarlo en producción, se recomienda completar pruebas, despliegue controlado, política de privacidad y revisión final de datos sensibles.
