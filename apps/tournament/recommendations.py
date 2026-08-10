from collections import Counter

from .models import (
    CompetitionBattleEntry,
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
        TeamCompetitionState.objects.filter(
            competition=competition,
            team_id__in=recent_team_ids,
            current_status=ParticipantStatus.ELIMINATED,
        )
        .select_related("team__institution", "current_group", "current_battle")
        .order_by("team__robot_name")
    )


def stage_counts(states):
    return Counter(state.current_stage for state in states)


def bracket_stage_for_count(participant_count):
    return {
        4: CompetitionStage.SEMIFINAL,
        2: CompetitionStage.FINAL,
    }.get(participant_count)


def bracket_title_for_count(participant_count):
    return {
        4: "Semifinal",
        2: "Gran final",
    }.get(participant_count, "Llave eliminatoria")


def balanced_group_count(participant_count):
    if participant_count <= 6:
        return 1
    if participant_count <= 12:
        return max(2, (participant_count + 3) // 4)
    return max(2, (participant_count + 5) // 6)


def balanced_group_sizes_for_count(participant_count, group_count):
    base_size = participant_count // group_count
    remainder = participant_count % group_count
    return [base_size + (1 if index < remainder else 0) for index in range(group_count)]


def qualifier_targets_for_group_sizes(participant_count, group_sizes):
    if not group_sizes:
        return []
    target_total = max(1, round(participant_count * 0.5))
    if participant_count == 5:
        target_total = 3
    if participant_count == 8:
        target_total = 4
    target_total = min(target_total, participant_count)
    base = target_total // len(group_sizes)
    remainder = target_total % len(group_sizes)
    targets = []
    for index, size in enumerate(group_sizes):
        target = base + (1 if index < remainder else 0)
        targets.append(max(1, min(size, target)))
    return targets


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


def recommend_group_round_plan(active):
    pool = build_progressive_pool(active)
    total = pool["total"]
    if total <= 4:
        return None
    group_count = balanced_group_count(total)
    group_sizes = balanced_group_sizes_for_count(total, group_count)
    qualifier_targets = qualifier_targets_for_group_sizes(total, group_sizes)
    total_qualifiers = sum(qualifier_targets)
    return {
        "total_participants": total,
        "direct_slots": pool["direct_count"],
        "recovered_slots": pool["recovered_count"],
        "recommended_type": "balanced_group_round",
        "title": "Nueva ronda grupal",
        "suggested_format": f"{group_count} grupo(s)/campal(es) balanceado(s)",
        "group_count": group_count,
        "group_sizes": group_sizes,
        "qualifier_targets": qualifier_targets,
        "total_qualifiers": total_qualifiers,
        "explanation": (
            "Despues de consolidar los participantes vivos, se generara una nueva fase grupal. "
            f"Todos jugaran y clasificaran {total_qualifiers} participante(s). "
            "El sistema no usara byes ni pases directos."
        ),
        "alternatives": [
            {
                "type": "manual_group_round",
                "title": "Configurar grupos manualmente",
                "suggested_format": "ajuste manual de grupos/campales",
                "participant_count": total,
                "explanation": "El administrador puede ajustar cantidad de grupos o mover participantes antes de operar la fase.",
            }
        ],
        "warnings": [],
        "can_create": True,
        "creation_strategy": "balanced_group_round",
    }


def base_recommendation(active_count):
    exact_rules = {
        4: {
            "recommended_type": CompetitionStage.SEMIFINAL,
            "title": "Semifinal",
            "suggested_format": "2 duelos",
            "explanation": "Hay 4 participantes vivos; corresponde crear semifinal con 2 batallas de 2.",
        },
        2: {
            "recommended_type": CompetitionStage.FINAL,
            "title": "Gran final",
            "suggested_format": "duelo final",
            "explanation": "Hay 2 participantes vivos; corresponde generar la gran final.",
        },
        3: {
            "recommended_type": CompetitionStage.FINAL,
            "title": "Final de 3",
            "suggested_format": "triangular",
            "explanation": "Hay 3 participantes vivos; una final triangular permite definir primero, segundo y tercero.",
        },
    }
    if active_count in exact_rules:
        return exact_rules[active_count]
    if active_count > 4:
        group_count = balanced_group_count(active_count)
        group_sizes = balanced_group_sizes_for_count(active_count, group_count)
        qualifier_targets = qualifier_targets_for_group_sizes(active_count, group_sizes)
        total_qualifiers = sum(qualifier_targets)
        return {
            "recommended_type": "balanced_group_round",
            "title": "Nueva ronda grupal",
            "suggested_format": f"{group_count} grupo(s)/campal(es) balanceado(s)",
            "group_count": group_count,
            "group_sizes": group_sizes,
            "qualifier_targets": qualifier_targets,
            "total_qualifiers": total_qualifiers,
            "can_create": True,
            "creation_strategy": "balanced_group_round",
            "explanation": (
                "Despues de consolidar los participantes vivos, se generara una nueva fase grupal. "
                f"Todos jugaran y clasificaran {total_qualifiers} participante(s). "
                "El sistema no usara byes ni pases directos."
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

    if recommended_type == "balanced_group_round":
        group_count = recommendation.get("group_count") or balanced_group_count(participant_count)
        qualifier_targets = recommendation.get("qualifier_targets") or []
        total_qualifiers = recommendation.get("total_qualifiers") or sum(qualifier_targets)
        return {
            "name": title,
            "participant_count": recommendation.get("total_participants", participant_count),
            "format": suggested_format,
            "unit_count": group_count,
            "unit_label": "grupos",
            "structure_label": f"{group_count} grupo(s)/campal(es), clasifican {total_qualifiers}",
            "explanation": recommendation.get("explanation", ""),
            "can_create": bool(recommendation.get("can_create")),
            "group_round_needed": True,
            "group_count": group_count,
            "qualifier_targets": qualifier_targets,
            "total_qualifiers": total_qualifiers,
            "all_alive_play": True,
            "creation_strategy": recommendation.get("creation_strategy", "balanced_group_round"),
        }

    if recommended_type == CompetitionStage.FINAL and participant_count == 3:
        return {
            "name": title,
            "participant_count": participant_count,
            "format": "triangular final",
            "unit_count": 1,
            "unit_label": "final",
            "structure_label": "1 final triangular de 3 participante(s)",
            "explanation": recommendation.get("explanation", ""),
            "can_create": True,
            "creation_strategy": recommendation.get("creation_strategy", "final_ranking"),
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
            "creation_strategy": recommendation.get("creation_strategy", "direct_bracket"),
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
    previous_repechage_team_ids = set(
        CompetitionBattleEntry.objects.filter(
            battle__competition=competition,
            battle__stage__in=REPECHAGE_STAGES,
        ).values_list("team_id", flat=True)
    )
    repechable = [
        state for state in repechable
        if state.team_id not in previous_repechage_team_ids
    ]
    eliminated = [
        state for state in eliminated
        if state.team_id not in previous_repechage_team_ids
    ]
    recent_eliminated = [
        state for state in recent_eliminated
        if state.team_id not in previous_repechage_team_ids
    ]

    active_count = len(active)
    recommendation = base_recommendation(active_count)
    alternatives = []
    warnings = []
    repechage = repechage_preview(repechable, recent_eliminated, eliminated)

    repechage_option = repechage_alternative(repechage)
    if repechage_option:
        alternatives.append(repechage_option)

    if active_count == 0:
        warnings.append("No hay participantes activos detectados; revisa resultados o estados manuales.")
    if len(stage_counts(active)) > 1 and active_count <= 4:
        warnings.append("Los participantes vivos aparecen distribuidos en mas de una fase; revisa consistencia.")
    if active_count % 2 == 1 and active_count > 4:
        alternatives.append(
            {
                "type": "manual_group_round",
                "title": "Ajustar ronda grupal",
                "suggested_format": "manual",
                "participant_count": active_count,
                "explanation": "La cantidad impar se puede organizar en grupos/campales balanceados sin dejar participantes descansando.",
            }
        )

    preview = phase_plan_preview(
        {
            **recommendation,
            "participant_count": active_count,
            "active_count": active_count,
        }
    )
    if warnings:
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
    }
    return result
