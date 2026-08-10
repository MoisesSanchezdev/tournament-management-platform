# 01. Guia editorial

## Idioma y tono

- Idioma principal: espanol.
- Tono: tecnico profesional, verificable y preciso.
- Audiencia: desarrolladores nuevos, responsables tecnicos, revisores academicos y operadores del sistema.
- Terminos en ingles: conservar nombres tecnicos establecidos (`template`, `endpoint`, `payload`, `fixture`, `rollback`) y explicar la primera aparicion si afecta comprension.

## Convenciones de escritura

- Mayusculas: usar minusculas para conceptos comunes y mayusculas solo para nombres propios, clases, apps o titulos.
- Fechas: formato ISO `AAAA-MM-DD` cuando se documenten eventos verificables.
- Versiones: documentar solo versiones confirmadas por archivos o comandos.
- Hechos confirmados: escribir en modo afirmativo y citar fuente.
- Informacion no confirmada: marcar explicitamente como `NO CONFIRMADO`, salvo datos de produccion, que deben marcarse como `PENDIENTE DE DEFINICION PARA PRODUCCION`.
- Recomendaciones: separarlas de hechos implementados.
- Advertencias: usar solo para riesgos operativos reales.

## Convenciones LaTeX

- Rutas, archivos, comandos, clases, funciones, variables y endpoints: `\texttt{}` mediante macros `\ruta{}`, `\archivo{}`, `\comando{}`, `\clase{}`, `\funcion{}` y `\variable{}`. Los endpoints se documentan con `\ruta{}` porque LaTeX reserva los nombres de control que comienzan por `\end`.
- Referencias cruzadas: usar `\cref{}` de forma preferente y no mezclar estilos sin necesidad.
- Figuras: `Figura X.Y`, con pie descriptivo y fuente.
- Tablas: `Tabla X.Y`, con columnas compactas, encabezados claros y notas si hay supuestos.
- Codigo: usar `listings`; no usar `minted` porque exige `shell-escape` y dependencia externa de Pygments.
- Notas, advertencias y recomendaciones: usar entornos `advertencia` y `recomendacion`.
- Fragmentos de codigo: maximo el fragmento necesario para explicar un contrato; no copiar archivos completos.

## Paquetes seleccionados

- `fontspec`: soporte Unicode y fuentes libres con LuaLaTeX.
- `babel`: idioma espanol y convenciones tipograficas.
- `csquotes`: citas compatibles con `biblatex`.
- `microtype`: mejora tipografica sin cambiar contenido.
- `geometry`: control de margenes.
- `graphicx`, `caption`, `subcaption`: figuras y pies.
- `booktabs`, `longtable`, `tabularx`: tablas tecnicas y extensas.
- `listings`: codigo reproducible sin procesos externos.
- `tcolorbox`: advertencias y recomendaciones reutilizables.
- `glossaries-extra`: glosario y acronimos.
- `biblatex` con `biber`: bibliografia moderna y mantenible.
- `hyperref` y `cleveref`: enlaces y referencias cruzadas.

## Numeracion

- Capitulos: numeracion arabiga.
- Anexos: letras automaticas por `\appendix`.
- Figuras, tablas y codigo: numeracion por capitulo.
- Etiquetas: usar prefijos `chap:`, `sec:`, `fig:`, `tab:`, `lst:` y `anexo:`.

## Longitud recomendada

- Secciones conceptuales: 1 a 3 paginas.
- Secciones tecnicas criticas: 3 a 8 paginas si incluyen tablas o diagramas.
- Tablas extensas: mover a anexos.
- Diagramas: incluir solo si reducen ambiguedad o mejoran trazabilidad.
