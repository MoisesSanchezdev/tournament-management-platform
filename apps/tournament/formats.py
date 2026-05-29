from .models import CompetitionStage


GROUP_LABELS = [chr(letter) for letter in range(ord("A"), ord("Z") + 1)]
VALID_DIRECT_TOTALS = {4, 8, 16, 32}


def balanced_group_sizes(total_slots: int, group_count: int) -> list[int]:
    base_size = total_slots // group_count
    remainder = total_slots % group_count
    return [base_size + (1 if index < remainder else 0) for index in range(group_count)]


def pairing_labels(group_labels: list[str]) -> list[tuple[str, str]]:
    pairings = []
    for index in range(0, len(group_labels), 2):
        left = group_labels[index]
        right = group_labels[index + 1]
        pairings.append((f"1{left}", f"2{right}"))
        pairings.append((f"1{right}", f"2{left}"))
    return pairings


def build_profile(
    *,
    team_count: int,
    group_count: int,
    qualifiers_per_group: int,
    mode_key: str,
    mode_label: str,
    summary: str,
    allow_purgatory_one: bool,
    allow_purgatory_two: bool,
    enable_third_place: bool,
):
    if group_count < 1:
        raise ValueError("Debes definir al menos un grupo.")
    if group_count > len(GROUP_LABELS):
        raise ValueError("La cantidad de grupos supera el limite soportado por el sistema.")
    if group_count % 2 != 0:
        raise ValueError("La cantidad de grupos debe ser par para armar llaves equilibradas sin byes.")
    if qualifiers_per_group < 1:
        raise ValueError("Debes clasificar al menos un carro por grupo.")

    direct_total = group_count * qualifiers_per_group
    if direct_total not in VALID_DIRECT_TOTALS:
        raise ValueError("La combinacion elegida produciria llaves invalidas sin byes.")
    if direct_total > team_count:
        raise ValueError("No puedes clasificar mas carros de los que realmente tienes inscritos.")
    if allow_purgatory_two and not allow_purgatory_one:
        raise ValueError("El Purgatorio 2 requiere tener activo el Purgatorio 1.")
    if allow_purgatory_one and direct_total >= team_count:
        raise ValueError("Para usar purgatorios debe quedar al menos un carro fuera del cuadro principal.")

    allow_purgatory_one = bool(allow_purgatory_one) and direct_total >= 16
    allow_purgatory_two = bool(allow_purgatory_two) and allow_purgatory_one

    stages = []
    uses_revival = allow_purgatory_one
    if allow_purgatory_one:
        stages.append({"stage": CompetitionStage.PURGATORY_1, "count": 4})

    if direct_total == 32:
        stages.append({"stage": CompetitionStage.ROUND_OF_32, "count": 16})
        stages.append({"stage": CompetitionStage.ROUND_OF_16, "count": 8})
    elif direct_total == 16:
        stages.append({"stage": CompetitionStage.ROUND_OF_16, "count": 8})
    elif direct_total == 8:
        stages.append({"stage": CompetitionStage.QUARTERFINAL, "count": 4})
    elif direct_total == 4:
        stages.append({"stage": CompetitionStage.SEMIFINAL, "count": 2})

    if allow_purgatory_two:
        stages.append({"stage": CompetitionStage.PURGATORY_2, "count": 4})
        stages.append({"stage": CompetitionStage.QUARTERFINAL, "count": 4})
    elif direct_total >= 16:
        stages.append({"stage": CompetitionStage.QUARTERFINAL, "count": 4})

    if direct_total >= 8:
        stages.append({"stage": CompetitionStage.SEMIFINAL, "count": 2})

    if enable_third_place:
        stages.append({"stage": CompetitionStage.THIRD_PLACE, "count": 1})
    stages.append({"stage": CompetitionStage.FINAL, "count": 1})

    return {
        "key": mode_key,
        "label": mode_label,
        "summary": summary,
        "group_count": group_count,
        "qualifiers_per_group": qualifiers_per_group,
        "qualifier_count": direct_total,
        "uses_revival": uses_revival,
        "allow_purgatory_one": allow_purgatory_one,
        "allow_purgatory_two": allow_purgatory_two,
        "enable_third_place": enable_third_place,
        "stages": stages,
        "team_count": team_count,
    }


def profile_summary(profile: dict) -> str:
    pieces = [
        f"{profile['group_count']} grupos",
        f"{profile['qualifiers_per_group']} clasifica(n) por grupo",
        f"{profile['qualifier_count']} carros al cuadro principal",
    ]
    if profile.get("allow_purgatory_two"):
        pieces.append("con Purgatorio 1 y 2")
    elif profile.get("allow_purgatory_one"):
        pieces.append("con Purgatorio 1")
    else:
        pieces.append("sin repechajes")
    if profile.get("enable_third_place"):
        pieces.append("y tercer lugar")
    return ", ".join(pieces) + "."


def auto_profile(team_count: int) -> dict:
    if team_count < 4:
        return {
            "key": "minimum_pending",
            "label": "Modo minimo pendiente",
            "summary": "Se requieren al menos 4 carros para activar el torneo automatico sin byes.",
            "group_count": 0,
            "qualifiers_per_group": 0,
            "qualifier_count": 0,
            "uses_revival": False,
            "allow_purgatory_one": False,
            "allow_purgatory_two": False,
            "enable_third_place": False,
            "stages": [],
            "team_count": team_count,
            "mode_source": "auto",
        }

    if team_count < 16:
        profile = build_profile(
            team_count=team_count,
            group_count=2,
            qualifiers_per_group=2,
            mode_key="sprint_final4",
            mode_label="Modo Sprint",
            summary="2 grupos, 2 clasificados por grupo y cierre corto sin byes.",
            allow_purgatory_one=False,
            allow_purgatory_two=False,
            enable_third_place=True,
        )
    elif team_count < 32:
        profile = build_profile(
            team_count=team_count,
            group_count=4,
            qualifiers_per_group=2,
            mode_key="classic_final8",
            mode_label="Modo Clasico Corto",
            summary="4 grupos, 2 clasificados por grupo y cuadro limpio desde cuartos de final.",
            allow_purgatory_one=False,
            allow_purgatory_two=False,
            enable_third_place=True,
        )
    elif team_count < 64:
        profile = build_profile(
            team_count=team_count,
            group_count=8,
            qualifiers_per_group=2,
            mode_key="explosion_standard",
            mode_label="Modo Explosion",
            summary="8 grupos, 2 clasificados por grupo y repechaje unico con Purgatorio 1.",
            allow_purgatory_one=True,
            allow_purgatory_two=False,
            enable_third_place=True,
        )
    else:
        profile = build_profile(
            team_count=team_count,
            group_count=16,
            qualifiers_per_group=2,
            mode_key="explosion_extended",
            mode_label="Modo Explosion Extendido",
            summary="16 grupos, ronda de 32 y repechaje unico manteniendo el cuadro sin byes.",
            allow_purgatory_one=True,
            allow_purgatory_two=False,
            enable_third_place=True,
        )

    profile["mode_source"] = "auto"
    return profile


def competition_profile(team_count: int, overrides: dict | None = None) -> dict:
    overrides = overrides or {}
    if overrides.get("mode_source") == "manual":
        profile = build_profile(
            team_count=team_count,
            group_count=int(overrides["group_count"]),
            qualifiers_per_group=int(overrides["qualifiers_per_group"]),
            mode_key="manual_override",
            mode_label="Modo Manual",
            summary="Configuracion armada por organizacion con control manual de grupos y fases.",
            allow_purgatory_one=bool(overrides.get("allow_purgatory_one")),
            allow_purgatory_two=bool(overrides.get("allow_purgatory_two")),
            enable_third_place=bool(overrides.get("enable_third_place", True)),
        )
        profile["mode_source"] = "manual"
        profile["summary"] = profile_summary(profile)
        return profile
    return auto_profile(team_count)
