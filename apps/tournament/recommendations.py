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
SAFE_DUEL_STAGE_COUNTS = {
    CompetitionStage.ROUND_OF_32: 32,
    CompetitionStage.ROUND_OF_16: 16,
    CompetitionStage.QUARTERFINAL: 8,
    CompetitionStage.SEMIFINAL: 4,
    CompetitionStage.FINAL: 2,
}
BRACKET_SIZES = [32, 16, 8, 4, 2]
REPECHAGE_STAGES = {CompetitionStage.PURGATORY_1, CompetitionStage.PURGATORY_2}


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
        .select_related("team__institution", "current_group", "current_battle")
        .order_by("team__robot_name")
    )


def stage_counts(states):
    return Counter(state.current_stage for state in states)


def bracket_stage_for_count(participant_count):
    return {
        32: CompetitionStage.ROUND_OF_32,
        16: CompetitionStage.ROUND_OF_16,
        8: CompetitionStage.QUARTERFINAL,
        4: CompetitionStage.SEMIFINAL,
        2: CompetitionStage.FINAL,
    }.get(participant_count)


def bracket_title_for_count(participant_count):
    return {
        32: "Ronda de 32",
        16: "Octavos",
        8: "Cuartos",
        4: "Semifinal",
        2: "Gran final",
    }.get(participant_count, "Llave eliminatoria")


def lower_bracket_size(participant_count):
    for size in BRACKET_SIZES:
        if participant_count > size:
            return size
    return None


def build_progressive_pool(active):
    recovered = [state for state in active if state.current_stage in REPECHAGE_STAGES]
    direct = [state for state in active if state.current_stage not in REPECHAGE_STAGES]
    return {
        "active": active,
        "direct": direct,
        "recovered": recovered,
        "total": len(active),
        "direct_count": len(direct),
        "recovered_count": len(recovered),
    }


def recommend_integration_plan(competition, active):
    pool = build_progressive_pool(active)
    total = pool["total"]
    has_recovered = pool["recovered_count"] > 0
    has_pending_integration = bool((competition.configuration or {}).get("pending_integration_plan"))
    mixed_active_paths = len(stage_counts(active)) > 1

    if not (has_recovered or has_pending_integration or mixed_active_paths):
        return None

    exact_stage = bracket_stage_for_count(total)
    if exact_stage:
        title = bracket_title_for_count(total)
        return {
            "total_participants": total,
            "target_bracket_size": total,
            "direct_slots": pool["direct_count"],
            "recovered_slots": pool["recovered_count"],
            "integration_needed": False,
            "recommended_type": exact_stage,
            "title": title,
            "suggested_format": "duelos",
            "participants_to_play_preliminary": 0,
            "participants_with_bye": 0,
            "winners_needed": 0,
            "explanation": (
                f"Hay {total} participantes vivos consolidados entre clasificados directos y recuperados. "
                f"La cantidad ya permite crear {title} sin ronda previa."
            ),
            "alternatives": [],
            "warnings": [],
            "can_create": True,
            "creation_strategy": "direct_bracket",
        }

    target = lower_bracket_size(total)
    if not target:
        return None

    excess = total - target
    preliminary_players = excess * 2
    bye_players = total - preliminary_players
    target_stage = bracket_stage_for_count(target)
    can_create = bool(
        target_stage
        and preliminary_players >= 2
        and preliminary_players <= total
        and preliminary_players % 2 == 0
        and bye_players >= 0
    )
    return {
        "total_participants": total,
        "target_bracket_size": target,
        "direct_slots": pool["direct_count"],
        "recovered_slots": pool["recovered_count"],
        "integration_needed": True,
        "recommended_type": "integration_preliminary",
        "title": "Ronda previa de integracion",
        "suggested_format": f"{preliminary_players // 2} duelo(s) de integracion",
        "participants_to_play_preliminary": preliminary_players,
        "participants_with_bye": bye_players,
        "winners_needed": excess,
        "explanation": (
            f"Hay {total} participantes vivos. Para llegar a un cuadro limpio de {target}, "
            f"se propone una ronda previa con {preliminary_players} participantes y {excess} cupo(s). "
            f"Los otros {bye_players} participante(s) esperan con bye para integrarse a la llave."
        ),
        "alternatives": [
            {
                "type": "manual_integration",
                "title": "Integracion manual",
                "suggested_format": "seleccion manual de previa y byes",
                "participant_count": total,
                "explanation": "El organizador puede ajustar manualmente quienes juegan la previa y quienes esperan con bye.",
            }
        ],
        "warnings": [],
        "can_create": can_create,
        "creation_strategy": "preliminary_duels" if can_create else "manual_required",
    }


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


def participant_preview_payload(state):
    return {
        "name": state.team.robot_name,
        "institution": state.team.institution.name if state.team.institution_id else "",
        "stage": state.get_current_stage_display() if hasattr(state, "get_current_stage_display") else state.current_stage,
        "status": state.get_current_status_display() if hasattr(state, "get_current_status_display") else state.current_status,
    }


def repechage_format_for_count(candidate_count):
    if candidate_count == 2:
        return "duelo de repechaje", 1
    if candidate_count == 3:
        return "triangular de repechaje", 1
    if candidate_count == 4:
        return "2 duelos de repechaje", 2
    if candidate_count == 6:
        return "2 triangulares de repechaje", 2
    if candidate_count >= 4:
        return "campales equilibradas de repechaje", min(4, max(1, candidate_count // 2))
    return "repechaje manual balanceado", 1


def repechage_candidates(repechable, recent_eliminated, eliminated):
    candidate_source = recent_eliminated or repechable or eliminated
    seen = set()
    candidates = []
    for state in candidate_source:
        if state.team_id in seen:
            continue
        seen.add(state.team_id)
        candidates.append(state)
    return candidates


def repechage_preview(repechable, recent_eliminated, eliminated):
    candidates = repechage_candidates(repechable, recent_eliminated, eliminated)
    candidate_count = len(candidates)
    can_offer = candidate_count >= 2
    can_create = candidate_count >= 2
    format_label, return_slots = repechage_format_for_count(candidate_count)
    return {
        "can_offer": can_offer,
        "can_create": can_offer and can_create,
        "candidate_count": candidate_count,
        "suggested_format": format_label if can_offer else "sin candidatos suficientes",
        "return_slots": return_slots if can_offer else 0,
        "explanation": (
            "Hay candidatos suficientes para evaluar una via de recuperacion antes de la siguiente fase."
            if can_offer
            else "No hay suficientes candidatos para sugerir repechaje en esta transicion."
        ),
        "message": (
            "Repechaje listo para crear con formato seguro."
            if can_offer and can_create
            else "Requiere configuracion manual para crear repechaje."
        ),
        "candidates": [participant_preview_payload(state) for state in candidates[:12]],
        "overflow_count": max(candidate_count - 12, 0),
    }


def repechage_alternative(preview):
    candidate_count = preview["candidate_count"]
    if not preview["can_offer"]:
        return None
    return {
        "type": "optional_repechage",
        "title": "Repechaje opcional",
        "suggested_format": preview["suggested_format"],
        "participant_count": candidate_count,
        "explanation": "Hay suficientes eliminados o repechables para ofrecer una via de recuperacion.",
    }


def phase_plan_preview(recommendation):
    participant_count = recommendation.get("participant_count") or recommendation.get("active_count") or 0
    recommended_type = recommendation.get("recommended_type")
    title = recommendation.get("title", "Revision manual")
    suggested_format = recommendation.get("suggested_format", "manual")

    if recommended_type == "integration_preliminary":
        duel_count = recommendation.get("participants_to_play_preliminary", 0) // 2
        return {
            "name": title,
            "participant_count": recommendation.get("total_participants", participant_count),
            "format": suggested_format,
            "unit_count": duel_count,
            "unit_label": "duelos",
            "structure_label": f"{duel_count} duelo(s) previos + {recommendation.get('participants_with_bye', 0)} bye(s)",
            "explanation": recommendation.get("explanation", ""),
            "can_create": bool(recommendation.get("can_create")),
            "integration_needed": True,
            "target_bracket_size": recommendation.get("target_bracket_size", 0),
            "participants_to_play_preliminary": recommendation.get("participants_to_play_preliminary", 0),
            "participants_with_bye": recommendation.get("participants_with_bye", 0),
            "winners_needed": recommendation.get("winners_needed", 0),
            "creation_strategy": recommendation.get("creation_strategy", "manual_required"),
        }

    if recommended_type in {
        CompetitionStage.ROUND_OF_32,
        CompetitionStage.ROUND_OF_16,
        CompetitionStage.QUARTERFINAL,
        CompetitionStage.SEMIFINAL,
        CompetitionStage.FINAL,
    }:
        duel_count = participant_count // 2
        can_create = SAFE_DUEL_STAGE_COUNTS.get(recommended_type) == participant_count
        return {
            "name": title,
            "participant_count": participant_count,
            "format": suggested_format,
            "unit_count": duel_count,
            "unit_label": "duelo" if duel_count == 1 else "duelos",
            "structure_label": f"{duel_count} duelo(s)",
            "explanation": recommendation.get("explanation", ""),
            "can_create": can_create,
            "integration_needed": bool(recommendation.get("integration_needed")),
            "target_bracket_size": recommendation.get("target_bracket_size", participant_count),
            "participants_to_play_preliminary": 0,
            "participants_with_bye": 0,
            "winners_needed": 0,
            "creation_strategy": recommendation.get("creation_strategy", "direct_bracket"),
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


def third_place_preview(competition, recommended_type):
    if recommended_type != CompetitionStage.FINAL:
        return {"can_create": False}
    if not (competition.configuration or {}).get("enable_third_place", True):
        return {"can_create": False}
    semifinal_battles = list(
        competition.battles.filter(
            stage=CompetitionStage.SEMIFINAL,
            status=MatchStatus.FINISHED,
            winner__isnull=False,
        ).prefetch_related("entries__team")
    )
    if len(semifinal_battles) != 2:
        return {"can_create": False}
    loser_ids = []
    for battle in semifinal_battles:
        entries = list(battle.entries.all())
        if len(entries) != 2:
            return {"can_create": False}
        loser = next((entry.team for entry in entries if entry.team_id != battle.winner_id), None)
        if loser is None:
            return {"can_create": False}
        loser_ids.append(loser.id)
    return {
        "can_create": len(loser_ids) == 2,
        "title": "Tercer lugar",
        "participant_count": len(loser_ids),
        "suggested_format": "duelo por tercer lugar",
        "explanation": "La semifinal tiene dos perdedores; se puede crear el duelo por tercer lugar junto con la gran final.",
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
    repechage = repechage_preview(repechable, recent_eliminated, eliminated)

    repechage_option = repechage_alternative(repechage)
    if repechage_option:
        alternatives.append(repechage_option)

    integration_plan = recommend_integration_plan(competition, active)
    if integration_plan:
        recommendation = integration_plan
        alternatives.extend(integration_plan.get("alternatives", []))

    if active_count == 0:
        warnings.append("No hay participantes activos detectados; revisa resultados o estados manuales.")
    if len(stage_counts(active)) > 1 and not integration_plan:
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

    preview = phase_plan_preview(
        {
            **recommendation,
            "participant_count": active_count,
            "active_count": active_count,
        }
    )
    if warnings and not preview.get("integration_needed"):
        preview["can_create"] = False
    result = {
        **recommendation,
        "participant_count": active_count,
        "active_count": active_count,
        "eliminated_count": len(eliminated),
        "recent_eliminated_count": len(recent_eliminated),
        "repechable_count": len(repechable),
        "alternatives": alternatives,
        "warnings": warnings,
        "can_apply": preview["can_create"],
        "mode": "diagnostic",
        "preview": preview,
        "repechage_preview": repechage,
        "third_place_preview": third_place_preview(competition, recommendation.get("recommended_type")),
        "integration_plan": integration_plan or {},
    }
    return result
