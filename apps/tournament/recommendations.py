from collections import Counter

from .models import (
    CompetitionStage,
    MatchStatus,
    ParticipantStatus,
    TeamCompetitionState,
)


ACTIVE_STATUSES = {ParticipantStatus.ACTIVE, ParticipantStatus.QUALIFIED}
REPECHAGE_STATUSES = {ParticipantStatus.REPECHAGE}
ELIMINATED_STATUSES = {ParticipantStatus.ELIMINATED}

STAGE_ORDER = [
    CompetitionStage.GROUPS,
    CompetitionStage.PURGATORY_1,
    CompetitionStage.ROUND_OF_32,
    CompetitionStage.ROUND_OF_16,
    CompetitionStage.PURGATORY_2,
    CompetitionStage.QUARTERFINAL,
    CompetitionStage.SEMIFINAL,
    CompetitionStage.THIRD_PLACE,
    CompetitionStage.FINAL,
]
STAGE_WEIGHT = {stage: index for index, stage in enumerate(STAGE_ORDER)}


def participant_snapshot(competition):
    states = list(
        TeamCompetitionState.objects.filter(competition=competition)
        .select_related("team__institution", "current_battle")
        .order_by("team__robot_name")
    )
    active = [state for state in states if state.current_status in ACTIVE_STATUSES]
    repechable = [state for state in states if state.current_status in REPECHAGE_STATUSES]
    eliminated = [state for state in states if state.current_status in ELIMINATED_STATUSES]
    return {
        "states": states,
        "active": active,
        "repechable": repechable,
        "eliminated": eliminated,
    }


def recent_eliminated_states(competition):
    finished_battles = list(
        competition.battles.filter(status=MatchStatus.FINISHED, winner__isnull=False)
        .prefetch_related("entries__team")
        .order_by("stage", "order")
    )
    if not finished_battles:
        return []

    latest_stage = max(finished_battles, key=lambda battle: STAGE_WEIGHT.get(battle.stage, -1)).stage
    recent_team_ids = {
        entry.team_id
        for battle in finished_battles
        if battle.stage == latest_stage
        for entry in battle.entries.all()
        if entry.team_id != battle.winner_id
    }
    if not recent_team_ids:
        return []
    return list(
        TeamCompetitionState.objects.filter(competition=competition, team_id__in=recent_team_ids)
        .select_related("team__institution", "current_battle")
        .order_by("team__robot_name")
    )


def stage_counts(states):
    return Counter(state.current_stage for state in states)


def base_recommendation(active_count):
    exact_rules = {
        32: {
            "recommended_type": CompetitionStage.ROUND_OF_32,
            "title": "Ronda de 32",
            "suggested_format": "duelos",
            "explanation": "Hay 32 participantes vivos; el cuadro puede continuar con 16 duelos directos.",
        },
        16: {
            "recommended_type": CompetitionStage.ROUND_OF_16,
            "title": "Octavos",
            "suggested_format": "duelos",
            "explanation": "Hay 16 participantes vivos; corresponde una ronda de octavos con 8 duelos.",
        },
        8: {
            "recommended_type": CompetitionStage.QUARTERFINAL,
            "title": "Cuartos",
            "suggested_format": "duelos",
            "explanation": "Hay 8 participantes vivos; corresponde una fase de cuartos con 4 duelos.",
        },
        4: {
            "recommended_type": CompetitionStage.SEMIFINAL,
            "title": "Semifinal",
            "suggested_format": "duelos",
            "explanation": "Hay 4 participantes vivos; corresponde una semifinal con 2 duelos.",
        },
        2: {
            "recommended_type": CompetitionStage.FINAL,
            "title": "Gran final",
            "suggested_format": "duelo final",
            "explanation": "Hay 2 participantes vivos; corresponde generar la gran final.",
        },
        3: {
            "recommended_type": "triangular_final",
            "title": "Triangular final",
            "suggested_format": "triangular",
            "explanation": "Hay 3 participantes vivos; una triangular final evita byes y resuelve el cierre.",
        },
        6: {
            "recommended_type": "two_triangulars",
            "title": "2 triangulares",
            "suggested_format": "2 triangulares de 3",
            "explanation": "Hay 6 participantes vivos; dos triangulares permiten clasificar sin byes.",
        },
    }
    if active_count in exact_rules:
        return exact_rules[active_count]
    if active_count % 2 == 1:
        return {
            "recommended_type": "manual_review",
            "title": "Revision manual",
            "suggested_format": "triangular o ronda previa",
            "explanation": (
                "La cantidad de participantes vivos es impar; conviene revisar si usar triangular, "
                "ronda previa o ajuste manual."
            ),
        }
    if active_count > 32:
        return {
            "recommended_type": "manual_review",
            "title": "Revision manual",
            "suggested_format": "grupos, ronda previa o repechaje",
            "explanation": (
                "Hay mas de 32 participantes vivos; el sistema recomienda revisar una fase previa "
                "antes de entrar al cuadro principal."
            ),
        }
    return {
        "recommended_type": "manual_review",
        "title": "Revision manual",
        "suggested_format": "duelos, triangulares o grupos pequenos",
        "explanation": (
            "La cantidad de participantes vivos no coincide con una ronda estandar; conviene "
            "definir manualmente la siguiente estructura."
        ),
    }


def repechage_alternative(repechable_count, recent_eliminated_count):
    candidate_count = repechable_count or recent_eliminated_count
    if candidate_count < 3:
        return None
    if candidate_count >= 8:
        format_label = "campales o grupos de repechaje"
    elif candidate_count == 6:
        format_label = "2 triangulares de repechaje"
    elif candidate_count == 3:
        format_label = "triangular de repechaje"
    else:
        format_label = "repechaje manual balanceado"
    return {
        "type": "optional_repechage",
        "title": "Repechaje opcional",
        "suggested_format": format_label,
        "participant_count": candidate_count,
        "explanation": "Hay suficientes eliminados o repechables para ofrecer una via de recuperacion.",
    }


def phase_plan_preview(recommendation):
    participant_count = recommendation.get("participant_count") or recommendation.get("active_count") or 0
    recommended_type = recommendation.get("recommended_type")
    title = recommendation.get("title", "Revision manual")
    suggested_format = recommendation.get("suggested_format", "manual")

    if recommended_type in {
        CompetitionStage.ROUND_OF_32,
        CompetitionStage.ROUND_OF_16,
        CompetitionStage.QUARTERFINAL,
        CompetitionStage.SEMIFINAL,
        CompetitionStage.FINAL,
    }:
        duel_count = participant_count // 2
        return {
            "name": title,
            "participant_count": participant_count,
            "format": suggested_format,
            "unit_count": duel_count,
            "unit_label": "duelo" if duel_count == 1 else "duelos",
            "structure_label": f"{duel_count} duelo(s)",
            "explanation": recommendation.get("explanation", ""),
            "can_create": False,
        }

    if recommended_type == "two_triangulars":
        return {
            "name": title,
            "participant_count": participant_count,
            "format": suggested_format,
            "unit_count": 2,
            "unit_label": "triangulares",
            "structure_label": "2 triangulares de 3 participantes",
            "explanation": recommendation.get("explanation", ""),
            "can_create": False,
        }

    if recommended_type == "triangular_final":
        return {
            "name": title,
            "participant_count": participant_count,
            "format": suggested_format,
            "unit_count": 1,
            "unit_label": "triangular",
            "structure_label": "1 triangular final de 3 participantes",
            "explanation": recommendation.get("explanation", ""),
            "can_create": False,
        }

    return {
        "name": title,
        "participant_count": participant_count,
        "format": suggested_format,
        "unit_count": 0,
        "unit_label": "revision manual",
        "structure_label": "Requiere configuracion manual antes de crear fase",
        "explanation": recommendation.get("explanation", ""),
        "can_create": False,
    }


def next_phase_recommendation(competition):
    snapshot = participant_snapshot(competition)
    active = snapshot["active"]
    eliminated = snapshot["eliminated"]
    repechable = snapshot["repechable"]
    recent_eliminated = recent_eliminated_states(competition)

    active_count = len(active)
    recommendation = base_recommendation(active_count)
    alternatives = []
    warnings = []

    repechage = repechage_alternative(len(repechable), len(recent_eliminated))
    if repechage:
        alternatives.append(repechage)

    if active_count == 0:
        warnings.append("No hay participantes activos detectados; revisa resultados o estados manuales.")
    if len(stage_counts(active)) > 1:
        warnings.append("Los participantes vivos aparecen distribuidos en mas de una fase; revisa consistencia.")
    if active_count % 2 == 1 and active_count not in {3}:
        alternatives.append(
            {
                "type": "manual_triangular",
                "title": "Triangular o ronda previa",
                "suggested_format": "manual",
                "participant_count": active_count,
                "explanation": "La cantidad impar puede resolverse con triangulares, ronda previa o ajuste manual.",
            }
        )

    result = {
        **recommendation,
        "participant_count": active_count,
        "active_count": active_count,
        "eliminated_count": len(eliminated),
        "recent_eliminated_count": len(recent_eliminated),
        "repechable_count": len(repechable),
        "alternatives": alternatives,
        "warnings": warnings,
        "can_apply": False,
        "mode": "diagnostic",
    }
    result["preview"] = phase_plan_preview(result)
    return result
