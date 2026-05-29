from hashlib import sha256

from .formats import GROUP_LABELS, balanced_group_sizes, competition_profile


def stable_sort_key(edition_id: int, division_key: str, registration) -> str:
    raw = f"{edition_id}:{division_key}:{registration.robot_name.lower()}:{registration.id}"
    return sha256(raw.encode("utf-8")).hexdigest()


def registration_slot(registration):
    leader = next((participant for participant in registration.participants.all() if participant.is_team_lead), None)
    return {
        "robot_name": registration.robot_name,
        "institution_name": registration.institution_name,
        "responsible_name": registration.responsible_name,
        "leader_name": leader.full_name if leader else "Pendiente",
        "is_placeholder": False,
    }


def placeholder_slot(index: int):
    return {
        "robot_name": f"Cupo disponible {index}",
        "institution_name": "Pendiente",
        "responsible_name": "Pendiente",
        "leader_name": "Pendiente",
        "is_placeholder": True,
    }


def summarize_group_sizes(group_sizes: list[int]) -> str:
    parts = []
    for size in sorted(set(group_sizes), reverse=True):
        count = group_sizes.count(size)
        label = "grupo" if count == 1 else "grupos"
        parts.append(f"{count} {label} de {size}")
    return " y ".join(parts)


def build_division_plan(edition, division_key: str, division_name: str, registrations, target_slots: int = 50):
    real_entries = list(registrations.prefetch_related("participants"))
    profile = competition_profile(len(real_entries))
    group_count = profile["group_count"] or 2
    group_labels = GROUP_LABELS[:group_count]
    total_slots = len(real_entries)
    group_sizes = balanced_group_sizes(total_slots, group_count) if total_slots else [0] * group_count
    campal_sizes = balanced_group_sizes(max(total_slots - profile.get("qualifier_count", 0), 0), 4) if profile["uses_revival"] else []
    ordered_entries = sorted(real_entries, key=lambda entry: stable_sort_key(edition.id, division_key, entry))

    groups = []
    entry_index = 0
    placeholder_index = 1

    for order, (label, size) in enumerate(zip(group_labels, group_sizes), start=1):
        slots = []
        real_count = 0
        for _ in range(size):
            if entry_index < len(ordered_entries):
                slots.append(registration_slot(ordered_entries[entry_index]))
                entry_index += 1
                real_count += 1
            else:
                slots.append(placeholder_slot(placeholder_index))
                placeholder_index += 1

        groups.append(
            {
                "label": label,
                "order": order,
                "size": size,
                "real_count": real_count,
                "projected_qualifiers": min(profile["qualifiers_per_group"], size),
                "projected_purgatory": max(size - profile["qualifiers_per_group"], 0),
                "slots": slots,
            }
        )

    phase_cards = [
        {
            "code": "Modo",
            "title": profile["label"],
            "format": profile["summary"],
            "participants": f"{total_slots} carros reales en esta categoria",
            "result": "El sistema escoge este modo automaticamente para evitar byes y mantener un cuadro limpio.",
            "battles": [f"Grupo {group['label']} ({group['size']} carros)" for group in groups] if groups else ["Pendiente de mas inscritos"],
        }
    ]

    if groups:
        phase_cards.append(
            {
                "code": "Fase 1",
                "title": "Los grupos",
                "format": f"{group_count} grupos aleatorios y equilibrados",
                "participants": f"{total_slots} carros",
                "result": (
                    f"Clasifican {profile['qualifier_count']} carros al cuadro principal."
                    if profile["qualifier_count"]
                    else "Aun no hay suficientes carros para activar el cuadro."
                ),
                "battles": [f"Grupo {group['label']} ({group['size']} carros)" for group in groups],
            }
        )

    if profile["allow_purgatory_one"]:
        phase_cards.extend(
            [
                {
                    "code": "Fase 2",
                    "title": "Purgatorio 1",
                    "format": "Campales balanceadas",
                    "participants": f"{max(total_slots - profile['qualifier_count'], 0)} carros",
                    "result": "Se escogen 4 sobrevivientes para el repechaje.",
                    "battles": [f"Campal {index}: {size} carros" for index, size in enumerate(campal_sizes, start=1)],
                },
                {
                    "code": "Fase 3",
                    "title": "Cuadro principal",
                    "format": (
                        "Ronda de 32 y luego octavos"
                        if profile["qualifier_count"] == 32
                        else "Octavos de final"
                    ),
                    "participants": f"{profile['qualifier_count']} carros",
                    "result": (
                        "Los perdedores de octavos todavia tienen una via de regreso."
                        if profile["allow_purgatory_two"]
                        else "Los ganadores de Purgatorio 1 esperan cupo para cuartos triangulares."
                    ),
                    "battles": ["Cruces generados automaticamente al cerrar grupos."],
                },
            ]
        )
        if profile["allow_purgatory_two"]:
            phase_cards.append(
                {
                    "code": "Fase 4",
                    "title": "Purgatorio 2 y cierre",
                    "format": "Triangulares + cierre clasico",
                    "participants": "Resucitados y ganadores elite",
                    "result": "El flujo desemboca en semifinal, tercer lugar y gran final.",
                    "battles": ["Purgatorio 2", "Cuartos", "Semifinal", "Bronce", "Final"],
                }
            )
        else:
            phase_cards.append(
                {
                    "code": "Fase 4",
                    "title": "Cierre con repechaje unico",
                    "format": "Cuartos triangulares + cierre clasico",
                    "participants": "Ganadores de octavos y Purgatorio 1",
                    "result": "El flujo desemboca en semifinal, tercer lugar y gran final.",
                    "battles": ["Cuartos", "Semifinal", "Bronce", "Final"],
                }
            )
    elif profile["qualifier_count"] == 8:
        phase_cards.append(
            {
                "code": "Fase 2",
                "title": "Cuadro final",
                "format": "Cuartos, semifinales y final",
                "participants": "8 clasificados",
                "result": "El torneo entra directo al cuadro corto sin byes.",
                "battles": ["4 cuartos", "2 semifinales", "Tercer lugar", "Gran final"],
            }
        )
    elif profile["qualifier_count"] == 4:
        phase_cards.append(
            {
                "code": "Fase 2",
                "title": "Cierre directo",
                "format": "Semifinales y final",
                "participants": "4 clasificados",
                "result": "El torneo se resuelve en un cuadro corto y limpio.",
                "battles": ["2 semifinales", "Tercer lugar", "Gran final"],
            }
        )

    return {
        "key": division_key,
        "name": division_name,
        "anchor": f"division-{division_key}",
        "target_slots": total_slots,
        "registered_count": len(real_entries),
        "pending_slots": 0,
        "mode_label": profile["label"],
        "mode_summary": profile["summary"],
        "group_summary": summarize_group_sizes(group_sizes),
        "quick_stats": [
            {"label": "Modo", "value": profile["label"]},
            {"label": "Grupos", "value": str(profile["group_count"]) if profile["group_count"] else "-"},
            {"label": "Clasifican", "value": str(profile["qualifier_count"]) if profile["qualifier_count"] else "-"},
            {"label": "Revancha", "value": "Si" if profile["uses_revival"] else "No"},
            {"label": "Sin byes", "value": "Si"},
        ],
        "groups": groups,
        "phase_cards": phase_cards,
    }
