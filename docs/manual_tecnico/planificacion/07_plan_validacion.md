# 07. Plan de validacion

## Validaciones por capitulo

Cada capitulo redactado debe pasar estas revisiones antes de considerarse listo:

1. Validacion tecnica contra auditoria.
2. Validacion contra codigo si el capitulo nombra clases, funciones, rutas, modelos o comandos.
3. Validacion editorial contra `01_guia_editorial.md`.
4. Revision ortografica y consistencia terminologica.
5. Revision de referencias cruzadas.
6. Revision de tablas desbordadas.
7. Revision de figuras faltantes o de baja resolucion.
8. Revision de enlaces rotos.
9. Revision de etiquetas duplicadas.
10. Revision de referencias no resueltas.
11. Revision de advertencias de compilacion LaTeX.
12. Revision de secretos y datos sensibles.
13. Revision de comandos destructivos o de alto impacto.
14. Revision de versiones y fechas.
15. Aprobacion tecnica final.

## Checklist reusable

| Item | Criterio | Resultado |
| --- | --- | --- |
| Fuente | Cada afirmacion tecnica tiene fuente documental o codigo verificable | PENDIENTE |
| No confirmados | La informacion sin evidencia esta marcada como `NO CONFIRMADO`; datos de produccion como `PENDIENTE DE DEFINICION PARA PRODUCCION` | PENDIENTE |
| Codigo | No se copian archivos completos ni secretos | PENDIENTE |
| Rutas | Las rutas son relativas al proyecto o estan justificadas | PENDIENTE |
| Tablas | No hay tablas ilegibles o desbordadas | PENDIENTE |
| Figuras | Toda figura existe y tiene pie descriptivo | PENDIENTE |
| Diagramas | Todo diagrama tiene fuente editable | PENDIENTE |
| Referencias | `\cref{}` y etiquetas resuelven correctamente | PENDIENTE |
| Glosario | Terminos nuevos se registran si son recurrentes | PENDIENTE |
| Acronimos | Acronimos se definen antes de uso intensivo | PENDIENTE |
| Seguridad | No hay credenciales, tokens ni valores reales de entorno | PENDIENTE |
| Operacion | Comandos riesgosos tienen advertencia | PENDIENTE |
| Compilacion | `latexmk -lualatex manual_tecnico.tex` termina sin errores | PENDIENTE |

## Revision final del manual

- Compilar con `latexmk`.
- Ejecutar limpieza controlada de auxiliares.
- Revisar PDF completo.
- Revisar indice, lista de figuras, lista de tablas y lista de codigo.
- Validar bibliografia y glosario.
- Validar anexos contra cuerpo principal.
- Registrar aprobaciones.
