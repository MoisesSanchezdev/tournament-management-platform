# 14. CSS

## Archivo principal

`static/css/app.css`

## Variables de tema

El CSS define variables en `:root` y variantes en `html[data-theme="light"]`.

| Categoria | Ejemplos |
| --- | --- |
| Superficies | `--bg`, `--surface`, `--surface-strong`, `--panel-bg` |
| Texto | `--text`, `--heading`, `--muted` |
| Acentos | `--accent`, `--magenta`, `--success`, `--danger` |
| Header | `--header-bg`, `--header-border`, `--nav-text` |
| Botones | `--button-primary-bg`, `--button-secondary-bg` |
| Estados | `--winner-card-bg`, `--loser-card-bg`, `--pending-card-bg` |
| Modal | `--modal-bg`, `--modal-backdrop` |
| Tipografia | `--title-font`, `--body-font` |

## Bloques de estilo

| Bloque | Selectores confirmados |
| --- | --- |
| Base | `html`, `body`, `a`, `button`, `.container` |
| Header/nav | `.site-header`, `.nav`, `.brand`, `.theme-toggle` |
| Publico | `.hero-shell`, `.showcase-grid`, `.sponsor-grid`, `.rule-banner` |
| Formularios | `.form-layout`, `.form-grid`, `.field`, `.form-actions` |
| Panel interno | `.control-body`, `.division-board`, `.control-panel`, `.phase-nav` |
| Recomendaciones | `.recommendation-panel`, `.phase-decision-modal` |
| Resultados | `.winner-choice-card`, `.result-status-badge`, `.result-save-bar` |
| Modal participante | `.participant-modal-shell`, `.participant-modal`, `.participant-history-list` |
| Comunicaciones/tablas | `.table-shell`, `.button-compact`, `.inline-action-form` |

## Responsividad

Media queries confirmadas: `max-width: 920px`, `hover: none`, `max-width: 800px`, `max-width: 460px`.

## Estados visuales de competencia

| Estado | Clases |
| --- | --- |
| Ganador/clasificado | `.is-winner`, `.entry-card--winner` |
| Perdedor/eliminado | `.is-loser`, `.entry-card--loser` |
| Pendiente | `.is-pending`, `.entry-card--pending` |

## Observaciones

1. Un unico CSS cubre sitio publico y panel interno.
2. El tema claro/oscuro esta basado en variables CSS y activado por JS.
3. Hay uso de `:has(...)`, `color-mix(...)` y gradientes; compatibilidad depende de navegadores modernos.
4. No se detecta preprocesador CSS ni pipeline de build.
