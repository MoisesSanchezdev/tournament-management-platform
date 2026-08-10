# Manual Tecnico - Plataforma Web Robot Explota Globos

Este directorio contiene las fuentes completas y modulares del Manual Tecnico profesional del sistema, publicado como version 1.0.

## Estado de compilacion

COMPILACION VERIFICADA PARA LA VERSION 1.0.

La fuente fue compilada con LuaLaTeX y el PDF final se conserva en `docs/entregables/Manual_Tecnico_Robot_Explota_Globos_v1.0.pdf`. La carpeta `build/` permanece local e ignorada porque contiene auxiliares reproducibles.

## Motor seleccionado

Motor: LuaLaTeX.

Justificacion tecnica:

- Maneja Unicode y espanol sin depender de conversiones manuales.
- Funciona bien en Windows con distribuciones como TeX Live o MiKTeX.
- Permite `fontspec` y fuentes libres incluidas en distribuciones LaTeX, como Latin Modern.
- Evita limitaciones de `pdfLaTeX` con caracteres modernos.
- Es mas reproducible para este proyecto que `XeLaTeX` cuando se usa `latexmk` con configuracion fija.

## Requisitos recomendados

- TeX Live o MiKTeX actualizado.
- `latexmk`.
- `biber` para bibliografia con `biblatex`.
- Motor `lualatex`.

No se requiere `minted` ni `shell-escape`; el codigo se debe representar con `listings` para mantener compilacion reproducible.

## Formato editorial aprobado

- Papel: A4.
- Impresion: preparado para doble cara con margenes interior/exterior.
- Lectura digital: conservada mediante enlaces y referencias cruzadas.
- Clasificacion: Uso institucional, academico y tecnico.
- Datos de produccion no confirmados: marcar como `PENDIENTE DE DEFINICION PARA PRODUCCION`.

## Compilacion

Desde `docs/manual_tecnico/`:

```powershell
latexmk -lualatex manual_tecnico.tex
```

Salida esperada:

```text
build/manual_tecnico.pdf
```

Limpieza de auxiliares:

```powershell
latexmk -c
```

## Estructura

- `manual_tecnico.tex`: archivo principal.
- `configuracion/`: paquetes, estilo, colores, comandos, metadatos e hipervinculos.
- `preliminares/`: portada, aprobaciones, indices, glosario y acronimos.
- `capitulos/`: capitulos editables de forma independiente.
- `anexos/`: material extenso de soporte.
- `figuras/`, `diagramas/`, `tablas/`, `codigo/`: activos documentales.
- `bibliografia/`: referencias BibLaTeX.
- `planificacion/`: arquitectura editorial y plan de redaccion.

## Flujo de edicion

1. Revisar `planificacion/00_indice_maestro.md`.
2. Redactar un capitulo a la vez.
3. Validar cada capitulo con `planificacion/07_plan_validacion.md`.
4. Agregar figuras, tablas y diagramas solo si estan inventariados o se registra una nueva decision.
5. Verificar referencias cruzadas, glosario, acronimos y bibliografia.

## Como agregar capitulos

1. Crear el archivo `.tex` en `capitulos/`.
2. Agregar `\input{capitulos/nombre_archivo}` en `manual_tecnico.tex`.
3. Definir una etiqueta `\label{chap:nombre}`.
4. Registrar el capitulo en `planificacion/00_indice_maestro.md` y `planificacion/03_matriz_fuentes.md`.

## Como agregar figuras

1. Guardar el archivo en `figuras/` o `diagramas/exportados/`.
2. Priorizar PDF o SVG exportado a PDF para salida vectorial.
3. Registrar el elemento en `planificacion/04_inventario_figuras.md` o `06_inventario_diagramas.md`.
4. Usar pie de figura descriptivo y referencia cruzada con `\cref{}`.

## Como agregar bibliografia

1. Incluir solo fuentes verificadas en `bibliografia/referencias.bib`.
2. Preferir documentacion oficial de tecnologias confirmadas.
3. No inventar autor, fecha, URL ni version.

## Como agregar acronimos y glosario

- Acronimos: `preliminares/acronimos.tex`.
- Glosario: `preliminares/glosario.tex`.
- Usar `\gls{}` despues de definir cada termino.

## Errores comunes

- Referencias no resueltas: compilar con `latexmk`, no una sola pasada.
- Bibliografia vacia: verificar `biber` y entradas reales en `referencias.bib`.
- Tablas desbordadas: usar `longtable`, `tabularx` o mover detalle a anexos.
- Figuras faltantes: validar ruta relativa desde `docs/manual_tecnico/`.
