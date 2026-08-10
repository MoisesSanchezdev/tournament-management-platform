# 08. Decisiones editoriales

| Decision | Alternativas consideradas | Justificacion | Impacto | Estado |
| --- | --- | --- | --- | --- |
| Papel A4 | A4, carta | Decision aprobada para entrega profesional e interoperabilidad documental | Afecta margenes y paginacion | APROBADA |
| Margenes 3 cm / 2.5 cm | Margenes simetricos, margenes estrechos | Facilita lectura, revision e impresion | PDF mas estable | APROBADA |
| Motor LuaLaTeX | pdfLaTeX, XeLaTeX | Unicode, espanol, `fontspec`, buena reproducibilidad con `latexmk` | Requiere distribucion moderna | APROBADA |
| Fuente Latin Modern | Fuentes del sistema, fuentes privadas | Libre, incluida en distribuciones LaTeX, no requiere copiar archivos | Apariencia academica estable | APROBADA |
| `listings` para codigo | `minted`, verbatim | Evita `shell-escape` y dependencias externas | Menos resaltado, mas reproducible | APROBADA |
| `biblatex` + `biber` | BibTeX clasico | Manejo moderno de bibliografia | Requiere `biber` | APROBADA |
| Glosario y acronimos | Lista manual | Mantiene consistencia y referencias | Requiere compilacion multiple | APROBADA |
| Tablas extensas en anexos | Tablas completas en capitulos | Reduce ruido y evita desbordes | Requiere referencias cruzadas | APROBADA |
| Diagramas vectoriales | Capturas raster | Mejor calidad en PDF | Exige exportacion controlada | APROBADA |
| Resumen y abstract | Omitir abstract, solo resumen | Se conservaran ambos; el abstract sera traduccion tecnica equivalente cuando exista redaccion final | Requiere traduccion posterior | APROBADA |
| Impresion a doble cara | Una cara, doble cara | Decision aprobada; se mantiene buena lectura digital y se evita forzar paginas blancas innecesarias | Cambia geometria a margenes interior/exterior | APROBADA |
| Portada institucional preparada | Portada grafica, portada minima | No se inventan logos, responsables, cargos ni codigos; se usan metadatos y marcadores | Permite ajuste posterior con plantilla oficial | APROBADA |
| Clasificacion documental | Publico, interno, reservado | Se adopta "Uso institucional, academico y tecnico"; no se asigna una reserva especial sin aprobacion expresa | Reduce afirmaciones institucionales no confirmadas | APROBADA |
| Datos de produccion pendientes | Inventar dominio/hosting, omitir dato | Los datos productivos sin evidencia se marcaran como `PENDIENTE DE DEFINICION PARA PRODUCCION` | Evita informacion falsa | APROBADA |
| Politica de respaldos | Afirmar politica formal, omitir backups | Se separa situacion actual, procedimiento recomendado y politica pendiente de aprobacion | Ordena redaccion operativa | APROBADA |
| Privacidad y datos personales | Afirmar cumplimiento normativo, omitir riesgo | Solo se documenta lo comprobable y se marcan pendientes | Evita sobredeclaraciones legales | APROBADA |
| Metadatos PDF | Minimos, completos | Se incluyen minimos sin datos sensibles | Mejora trazabilidad | APROBADA |
| Compatibilidad Windows | Linux-only, multiplataforma | El proyecto se trabaja en Windows | Comandos README en PowerShell | APROBADA |
| Bibliografia | Entradas inventadas, fuentes oficiales | No inventar referencias | Bib queda con marcadores hasta verificar | APROBADA |
