# Perfiles de usuario

## Matriz de perfiles

| Perfil | Implementacion | Proposito | Forma de acceso | Nivel tecnico |
| --- | --- | --- | --- | --- |
| Visitante publico | Real, sin autenticacion | Consultar informacion del torneo | Navegacion publica | Bajo |
| Participante o responsable de registro | Real, sin cuenta | Registrar robot y confirmar asistencia por token | `/registro/` y enlace `confirmar-asistencia/<token>` | Bajo |
| Administrador/organizador | Real, `is_staff` o `is_superuser` | Operar panel interno de torneo y comunicaciones | Login Django en `/torneo/control/login/` | Medio |
| Operador del torneo | Funcion operativa, no rol separado | Gestionar divisiones, grupos, resultados, fases y podio | Usuario organizador | Medio-alto |
| Operador de invitaciones y comunicaciones | Funcion operativa, no rol separado | Gestionar plantillas, destinatarios, envios y confirmaciones | Usuario organizador | Medio |
| Superusuario Django Admin | Real, `is_superuser` | Administrar modelos y acciones sensibles | `/admin/` | Alto |

## Detalle por perfil

### Visitante publico

- Pantallas disponibles: inicio, reglas, patrocinadores, vista publica de fases, seleccion de registro.
- Acciones permitidas: navegar, abrir PDF de reglas, ir a registro, cambiar tema.
- Acciones restringidas: panel de torneo, comunicaciones, admin y operaciones POST internas.
- Riesgos operativos: ver informacion desactualizada si no existe edicion activa o reglas publicadas.

### Participante o responsable de registro

- Pantallas disponibles: seleccion de categoria, formulario escolar, formulario universitario, exito de registro, confirmacion por token, token invalido.
- Acciones permitidas: enviar datos de robot e integrantes, confirmar asistencia si el token existe.
- Acciones restringidas: editar registros ya enviados desde interfaz publica, ver otros participantes, operar torneo.
- Riesgos operativos: datos duplicados, semestre universitario mayor a 4, correo ya usado, documento repetido, token filtrado.

### Administrador/organizador

- Pantallas disponibles: panel de organizacion, division, etapa, comunicaciones, plantillas, invitaciones, confirmaciones, historial.
- Acciones permitidas: generar competencia, configurar perfil, registrar resultados, gestionar comunicaciones.
- Acciones restringidas: dependen de permisos Django; el codigo exige `is_staff` o `is_superuser`.
- Riesgos operativos: errores de seleccion, envios reales sin datos verificados, acciones de reinicio, uso incorrecto de correcciones manuales.

### Operador del torneo

- Naturaleza: funcion operativa dentro del perfil organizador.
- Pantallas disponibles: dashboard de torneo, division, etapa, modales de participante y decision de fase.
- Acciones permitidas: grupos, clasificados, ganadores, repechaje, fases manuales, podio, movimientos manuales de participante.
- Acciones restringidas: no es un permiso propio; cualquier usuario staff con acceso podria operar.
- Riesgos operativos: afectar fases posteriores, guardar todos los cambios sin revisar, mover participantes a estados incompatibles.

### Operador de invitaciones y comunicaciones

- Naturaleza: funcion operativa dentro del perfil organizador.
- Pantallas disponibles: dashboard de comunicaciones, plantillas, previsualizacion, invitaciones, confirmaciones, historial.
- Acciones permitidas: cargar plantillas DOCX, registrar destinatarios, procesar lotes, simular, enviar prueba controlada o envio real si SMTP esta configurado.
- Acciones restringidas: acceso publico bloqueado por login y `is_staff`/`is_superuser`.
- Riesgos operativos: exponer correos, enviar a destinatarios reales, usar plantilla incorrecta, cargar Excel con columnas incompletas.

### Superusuario Django Admin

- Pantallas disponibles: Django Admin y todos los modelos registrados.
- Acciones permitidas: CRUD de ediciones, reglas, registros, equipos, competencias, estados, batallas, plantillas, destinatarios, lotes y logs; acciones admin de asistencia y sincronizacion.
- Acciones restringidas: ninguna restriccion funcional adicional observada en el codigo mas alla de Django Admin.
- Riesgos operativos: cambios directos sin validaciones de interfaz, acciones masivas, exposicion de PII, inconsistencias entre Admin y panel.
