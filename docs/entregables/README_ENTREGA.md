# Entrega oficial del Manual Tecnico

Proyecto: Plataforma Web Robot Explota Globos
Version del manual: 1.0
Estado: PUBLICADO
Fecha de publicacion: 2026-07-15
Institucion: Universidad Tecnologica de Pereira
Semillero: Semillero de Investigacion Kilby

## Archivos incluidos

- `Manual_Tecnico_Robot_Explota_Globos_v1.0.pdf`: version oficial compilada del Manual Tecnico.
- `Manual_Tecnico_Robot_Explota_Globos_Overleaf_v1.0.zip`: paquete editable para Overleaf con fuentes LaTeX, bibliografia y anexos necesarios.
- `VERSION.txt`: identificacion formal de la version publicada.
- `CHANGELOG.md`: resumen de hitos documentales y cambios de la version 1.0.
- `MANIFIESTO_PUBLICACION.md`: declaracion tecnica de publicacion.
- `CHECKLIST_PUBLICACION.md`: lista de verificacion aplicada antes del cierre.

## Apertura en Overleaf

1. Crear un proyecto nuevo en Overleaf.
2. Subir el archivo `Manual_Tecnico_Robot_Explota_Globos_Overleaf_v1.0.zip`.
3. Confirmar que el archivo principal sea `manual_tecnico.tex`.
4. Seleccionar LuaLaTeX como motor de compilacion.
5. Compilar el proyecto.

## Motor y dependencias

El manual fue preparado para LuaLaTeX por compatibilidad con Unicode, texto en espanol y estructura modular. La bibliografia usa Biber.

Distribucion LaTeX recomendada:

- MiKTeX actualizado en Windows, o
- TeX Live actualizado en Windows, Linux o macOS.

Secuencia de compilacion validada:

```powershell
lualatex -interaction=nonstopmode -file-line-error -synctex=1 -output-directory=build manual_tecnico.tex
biber --input-directory build --output-directory build manual_tecnico
lualatex -interaction=nonstopmode -file-line-error -synctex=1 -output-directory=build manual_tecnico.tex
lualatex -interaction=nonstopmode -file-line-error -synctex=1 -output-directory=build manual_tecnico.tex
```

## Pendientes institucionales

El manual se publica tecnicamente completo. Permanecen como pendientes exclusivamente institucionales los datos que requieren confirmacion formal, como codigo institucional, firmas, aprobaciones administrativas y definicion de infraestructura real de produccion.

No se deben completar esos datos por inferencia.
