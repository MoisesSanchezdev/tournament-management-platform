# Manual de Usuario

Estructura documental del Manual de Usuario de la Plataforma Web Robot Explota Globos.

## Estado

Versión documental: 1.0. Estado: PUBLICADO.

Fecha de publicación: 24 de julio de 2026.

Recomendación editorial: APROBADO PARA PUBLICACIÓN CON PENDIENTES INSTITUCIONALES.

## Compilación prevista

Motor objetivo: LuaLaTeX, sin `shell-escape`.

```powershell
lualatex -interaction=nonstopmode -halt-on-error manual_usuario.tex
```

Si `latexmk` está disponible:

```powershell
latexmk manual_usuario.tex
```

## Banco visual

- Capturas base: `capturas/base/`.
- Capturas finales procesadas: `capturas/finales/`.
- Pruebas POC conservadas: `capturas/prueba/`.
