# 06. Inventario de diagramas

Prioridad: formatos vectoriales compatibles con LaTeX. Mermaid se recomienda para flujos y dependencias; Graphviz para grafos; PlantUML para secuencias; TikZ solo para diagramas que deban mantenerse nativos en LaTeX.

| ID | Capitulo | Titulo | Proposito | Fuente | Formato | Orientacion | Ubicacion prevista | Metodo de generacion | Estado | Dependencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DIA-01 | 4 | Arquitectura general del sistema | Mostrar capas y modulos | 01, 04 | Mermaid -> PDF/SVG | Horizontal | Cap. 4 | Mermaid | PENDIENTE | Auditoria arquitectura |
| DIA-02 | 4 | Patron MTV aplicado | Explicar request-template-model-view | 04, 06, 07 | Mermaid -> PDF/SVG | Horizontal | Cap. 4 | Mermaid | PENDIENTE | URLs/vistas |
| DIA-03 | 4 | Dependencias entre aplicaciones | Visualizar acoplamientos | 04, 23 | Graphviz -> PDF | Horizontal | Cap. 4 | Graphviz | PENDIENTE | Apps confirmadas |
| DIA-04 | 10 | Modelo entidad-relacion | Entender persistencia | 05, 16 | Graphviz/PlantUML -> PDF | Horizontal | Cap. 10 | Graphviz o PlantUML | PENDIENTE | Modelos revisados |
| DIA-05 | 11 | Flujo de peticion HTTP | Conectar URL, vista, template y respuesta | 06, 07, 11 | Mermaid -> PDF/SVG | Horizontal | Cap. 11 | Mermaid | PENDIENTE | Rutas finales |
| DIA-06 | 11 | Flujo de registro de participantes | Explicar registro publico | 07, 08, 09 | Mermaid -> PDF/SVG | Vertical | Cap. 11 | Mermaid | PENDIENTE | Forms y services |
| DIA-07 | 12 | Flujo de formacion de equipos | Trazar registro confirmado a equipo | 09, 10 | Mermaid -> PDF/SVG | Vertical | Cap. 12 | Mermaid | PENDIENTE | Servicios participants |
| DIA-08 | 13 | Flujo completo de competencia | Resumir ciclo principal | 10 | Mermaid -> PDF/SVG | Horizontal | Cap. 13 | Mermaid | PENDIENTE | Logica torneo |
| DIA-09 | 13 | Flujo de fase de grupos | Explicar clasificacion inicial | 10, 09 | Mermaid -> PDF/SVG | Vertical | Cap. 13 | Mermaid | PENDIENTE | Servicios grupos |
| DIA-10 | 13 | Flujo de eliminatorias | Mostrar avance por fases | 10, 09 | Mermaid -> PDF/SVG | Horizontal | Cap. 13 | Mermaid | PENDIENTE | Servicios eliminatorias |
| DIA-11 | 13 | Flujo de repechaje | Explicar recuperacion de eliminados | 10, 09, 24 | Mermaid -> PDF/SVG | Vertical | Cap. 13 | Mermaid | PENDIENTE | Escenarios alternos |
| DIA-12 | 13 | Flujo de correccion manual | Documentar propuesta y confirmacion | 10, 13, 24 | Mermaid -> PDF/SVG | Vertical | Cap. 13 | Mermaid | PENDIENTE | Servicios manuales |
| DIA-13 | 15 | Flujo AJAX de guardado | Conectar JS, CSRF, vista y respuesta | 13, 07 | PlantUML secuencia -> PDF | Horizontal | Cap. 15 | PlantUML | PENDIENTE | Endpoints AJAX |
| DIA-14 | 18 | Flujo de despliegue | Ordenar pasos productivos | 19, 03 | Mermaid -> PDF/SVG | Vertical | Cap. 18 | Mermaid | PENDIENTE | Confirmacion produccion |
| DIA-15 | 20 | Flujo de respaldo y restauracion | Preparar continuidad | 16, 19, 24 | Mermaid -> PDF/SVG | Vertical | Cap. 20 | Mermaid | PENDIENTE | Politica backup |
| DIA-16 | 19 | Flujo de mantenimiento correctivo | Guiar diagnostico y correccion | 20, 21 | Mermaid -> PDF/SVG | Vertical | Cap. 19 | Mermaid | PENDIENTE | Procedimientos operativos |
