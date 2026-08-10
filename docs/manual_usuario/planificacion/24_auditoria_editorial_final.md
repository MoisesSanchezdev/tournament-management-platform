# Auditoría editorial, visual y funcional

## 1. Calificación global

Calificación: **94/100**.

El manual está completo, compilado y funcionalmente trazado. La publicación es viable con pendientes institucionales explícitos: URL de producción, contacto de soporte, código institucional, firmas, aprobaciones y políticas no confirmadas.

## 2. Cobertura funcional

- Procedimientos inventariados: 28.
- Procedimientos cubiertos: 28.
- Cobertura funcional: 100 %.
- Capturas finales conservadas: 42.
- Capítulos: 15.
- Anexos: 5.

## 3. Calidad de procedimientos

Los procedimientos tienen punto de inicio, perfil de usuario, pasos ordenados, resultado esperado y advertencias antes de acciones sensibles. Se verificó la separación entre simulación segura, prueba controlada y envío real. Django Admin se presenta como soporte avanzado, no como reemplazo del panel operativo.

## 4. Calidad visual

La revisión visual del PDF no mostró capturas ilegibles, recortes críticos, pies separados de figuras ni contenido fuera del margen. Las capturas usan datos ficticios y se mantienen en el banco final. No se conservaron capturas nuevas.

## 5. Calidad editorial

El tono general es profesional y orientado a usuarios no técnicos. Se normalizaron metadatos de versión y estado, y se retiraron referencias locales del texto publicable. Persisten algunos términos visibles de interfaz sin tildes porque corresponden a textos reales del sistema.

## 6. Calidad LaTeX

- Compilación final: LuaLaTeX, dos pasadas.
- PDF final: 111 páginas.
- `Overfull` iniciales: 2.
- `Overfull` finales: 0.
- `Underfull` iniciales: 192.
- `Underfull` finales: 170.
- Advertencias finales: 17, asociadas principalmente a small caps simuladas y cajas subllenadas no visibles como defecto bloqueante.

## 7. Privacidad

El texto compilado del PDF no contiene rutas locales, OneDrive, `127.0.0.1`, credenciales, tokens, contraseñas, correos personales, teléfonos ni documentos reales. Los archivos auxiliares del entorno demo conservan rutas técnicas fuera del PDF y deben excluirse de un paquete Overleaf/publicación.

## 8. Problemas encontrados

| Clasificación | Problema | Estado |
| --- | --- | --- |
| Importante | Metadatos mostraban versión 0.1 y estado de redacción. | Corregido. |
| Importante | El procedimiento de podio podía ser ambiguo porque la captura MU-031 no muestra el formulario inferior. | Corregido con texto mínimo y diálogo exacto. |
| Importante | El PDF incluía ejemplos locales `127.0.0.1`. | Corregido. |
| Menor | Dos `Overfull` en índice/perfiles. | Corregidos. |
| Menor | Macro de marcador de fase posterior seguía definida aunque ya no se usaba. | Corregida. |
| Cosmético | Small caps simuladas por Latin Modern. | Aceptado; no produce defecto visible. |
| Cosmético | `Underfull` en tablas densas y páginas con figuras. | Aceptado; no produce defecto visible crítico. |

## 9. Correcciones realizadas

- Actualización de versión documental a 0.9.
- Actualización de estado a `AUDITORÍA EDITORIAL FINAL`.
- Ajuste de control de versiones para evitar desbordes.
- Ajuste del ancho de numeración del índice.
- Ajuste de la tabla de perfiles para eliminar desborde.
- Aclaración del procedimiento de podio.
- Inclusión del texto exacto del diálogo de podio.
- Eliminación de ejemplos de URL local en fuentes compiladas.
- Eliminación de macro de marcador pendiente no usada.

## 10. Problemas pendientes

No quedan bloqueantes técnicos para publicación. Persisten únicamente pendientes institucionales: URL final de producción, código institucional, firmas, aprobaciones, contacto de soporte y políticas formales no confirmadas.

## 11. Captura adicional de podio

**No necesaria en la versión final.**

La captura MU-031 no muestra el formulario inferior; se intentó obtener una captura adicional con el entorno demo, pero el entorno local no expuso una evidencia válida y la captura fallida fue retirada. La ambigüedad quedó resuelta mediante texto mínimo: se indica que el formulario está más abajo en la misma pantalla, se nombran los campos y se documenta el diálogo exacto.

## 12. Advertencias de compilación

El log final no contiene errores fatales, referencias indefinidas, archivos faltantes ni `Overfull`. Quedan advertencias por small caps simuladas y `Underfull` no bloqueantes. No se recomienda perseguirlas mecánicamente porque derivan de tablas densas y figuras de página completa.

## 13. Preparación para Overleaf

El paquete publicable debe incluir la estructura LaTeX, capítulos, anexos, configuración, elementos editoriales y `capturas/finales`. Deben excluirse herramientas, entorno demo, bases temporales, perfiles de navegador, metadata de pruebas y cualquier archivo auxiliar con rutas locales.

## 14. Recomendación final

**APROBADO PARA PUBLICACIÓN CON PENDIENTES INSTITUCIONALES.**

La decisión se justifica porque el manual cubre el 100 % de procedimientos, compila sin errores ni desbordes visibles, no expone datos sensibles en el PDF, y las correcciones necesarias para publicación fueron aplicadas. Los pendientes restantes dependen de confirmación institucional, no de redacción ni de implementación documental.
