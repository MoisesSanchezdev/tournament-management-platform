# 08. Forms

## Formularios de participantes

Archivo: `apps/participants/forms.py`

| Funcion | Proposito |
| --- | --- |
| `normalize_robot_name` | Normaliza nombres de robot, remueve acentos/caracteres y variantes numeradas finales |
| `normalize_document_number` | Normaliza documentos dejando caracteres alfanumericos |

### `BaseRegistrationForm`

Campos adicionales:

| Campo | Regla |
| --- | --- |
| `leader_name` | Obligatorio |
| `leader_document_number` | Obligatorio |
| `member_two_name` | Opcional |
| `member_two_document_number` | Opcional, requerido si hay nombre |
| `member_three_name` | Opcional |
| `member_three_document_number` | Opcional, requerido si hay nombre |

Validaciones confirmadas:

1. Debe existir `TournamentEdition` activa.
2. Integrante 2 requiere nombre y documento juntos.
3. Integrante 3 requiere nombre y documento juntos.
4. Nombre de robot no puede duplicarse ni ser variante normalizada en la edicion activa.
5. Correo no puede repetirse en registros escolares o universitarios de la edicion activa.
6. Documentos no pueden repetirse dentro del formulario.
7. Documentos no pueden existir ya en participantes escolares o universitarios de la edicion activa.

Guardado confirmado:

1. Asigna `edition` activa.
2. Define `status=SUBMITTED`.
3. Crea lider obligatorio.
4. Crea integrantes 2 y 3 si fueron diligenciados.

### Formularios concretos

| Form | Modelo | Extra |
| --- | --- | --- |
| `SchoolRegistrationForm` | `SchoolRegistration` | Sin campos extra de categoria |
| `UniversityRegistrationForm` | `UniversityRegistration` | `semester`, maximo validado 4 |

## Formularios de comunicaciones

Archivo: `apps/invitations/forms.py`

| Form | Responsabilidad |
| --- | --- |
| `CommunicationTemplateForm` | Carga DOCX, marcadores requeridos y activacion |
| `CommunicationRecipientForm` | CRUD basico de destinatario |
| `InvitationBatchForm` | Seleccion de plantilla, XLSX y modo de envio |

### Validaciones de plantillas

| Validacion | Regla |
| --- | --- |
| Extension | Solo `.docx` |
| Tamano | Maximo 8 MB |
| Marcadores | Normalizados con `parse_required_markers` |
| Presencia en DOCX | `validate_template_markers` detecta faltantes |

### Validaciones de lotes

| Campo | Regla |
| --- | --- |
| `template` | Activa y del mismo tipo |
| `recipients_file` | `.xlsx`, maximo 4 MB |
| `send_mode` | `dry_run`, `test`, `official` |
| `test_recipient` | Requerido en modo `test` |
| `confirm_real_send` | Requerido para `test` y `official` |

## Riesgos y observaciones

1. La validacion de duplicados de documentos compara documentos normalizados pero guarda el valor original.
2. La validacion de robot hace busquedas en ambas tablas de registro por edicion.
3. Los formularios de comunicaciones bloquean envio real si SMTP no esta configurado.
