import random
from collections import defaultdict

from django.db import transaction
from django.db.models import Q

from apps.participants.models import Team

from .formats import GROUP_LABELS, balanced_group_sizes, competition_profile
from .models import (
    BattleFormat,
    CompetitionBattle,
    CompetitionBattleEntry,
    CompetitionHistoryEntry,
    CompetitionStage,
    CompetitionStatus,
    DivisionCompetition,
    DivisionGroup,
    DivisionGroupEntry,
    DivisionType,
    HistoryActionType,
    MatchStatus,
    ParticipantStatus,
    TeamCompetitionState,
)


STAGE_TITLES = {
    CompetitionStage.GROUPS: "Grupos",
    CompetitionStage.PURGATORY_1: "Repechaje 1",
    CompetitionStage.ROUND_OF_32: "Ronda de 32",
    CompetitionStage.ROUND_OF_16: "Octavos",
    CompetitionStage.PURGATORY_2: "Repechaje 2",
    CompetitionStage.QUARTERFINAL: "Cuartos",
    CompetitionStage.SEMIFINAL: "Semifinal",
    CompetitionStage.THIRD_PLACE: "Tercer lugar",
    CompetitionStage.FINAL: "Gran final",
}

STAGE_LABELS = {
    CompetitionStage.PURGATORY_1: "Repechaje",
    CompetitionStage.ROUND_OF_32: "Ronda 32",
    CompetitionStage.ROUND_OF_16: "Octavo",
    CompetitionStage.PURGATORY_2: "Repechaje",
    CompetitionStage.QUARTERFINAL: "Cuarto",
    CompetitionStage.SEMIFINAL: "Semifinal",
    CompetitionStage.THIRD_PLACE: "Bronce",
    CompetitionStage.FINAL: "Final",
}

STAGE_FORMATS = {
    CompetitionStage.PURGATORY_1: BattleFormat.BATTLE_ROYALE,
    CompetitionStage.ROUND_OF_32: BattleFormat.DUEL,
    CompetitionStage.ROUND_OF_16: BattleFormat.DUEL,
    CompetitionStage.PURGATORY_2: BattleFormat.TRIANGULAR,
    CompetitionStage.QUARTERFINAL: BattleFormat.DUEL,
    CompetitionStage.SEMIFINAL: BattleFormat.DUEL,
    CompetitionStage.THIRD_PLACE: BattleFormat.DUEL,
    CompetitionStage.FINAL: BattleFormat.DUEL,
}

STAGE_STATUS_DEFAULTS = {
    CompetitionStage.GROUPS: ParticipantStatus.ACTIVE,
    CompetitionStage.PURGATORY_1: ParticipantStatus.REPECHAGE,
    CompetitionStage.ROUND_OF_32: ParticipantStatus.ACTIVE,
    CompetitionStage.ROUND_OF_16: ParticipantStatus.ACTIVE,
    CompetitionStage.PURGATORY_2: ParticipantStatus.REPECHAGE,
    CompetitionStage.QUARTERFINAL: ParticipantStatus.ACTIVE,
    CompetitionStage.SEMIFINAL: ParticipantStatus.ACTIVE,
    CompetitionStage.THIRD_PLACE: ParticipantStatus.ACTIVE,
    CompetitionStage.FINAL: ParticipantStatus.ACTIVE,
}

BATTLE_CAPACITY = {
    BattleFormat.DUEL: 2,
    BattleFormat.TRIANGULAR: 3,
}

SAFE_PROGRESSIVE_DUEL_STAGES = {
    32: CompetitionStage.ROUND_OF_32,
    16: CompetitionStage.ROUND_OF_16,
    8: CompetitionStage.QUARTERFINAL,
    4: CompetitionStage.SEMIFINAL,
    2: CompetitionStage.FINAL,
}
BRACKET_SIZES = [32, 16, 8, 4, 2]

REPECHAGE_STAGES = [CompetitionStage.PURGATORY_1, CompetitionStage.PURGATORY_2]
INTEGRATION_STAGE_POOL = [
    CompetitionStage.PURGATORY_2,
    CompetitionStage.ROUND_OF_32,
    CompetitionStage.ROUND_OF_16,
    CompetitionStage.QUARTERFINAL,
    CompetitionStage.SEMIFINAL,
]
MANUAL_STAGE_POOL = [
    CompetitionStage.ROUND_OF_32,
    CompetitionStage.ROUND_OF_16,
    CompetitionStage.QUARTERFINAL,
    CompetitionStage.SEMIFINAL,
    CompetitionStage.FINAL,
    CompetitionStage.PURGATORY_1,
    CompetitionStage.PURGATORY_2,
]


class ManualCorrectionRequired(ValueError):
    def __init__(self, message=None):
        super().__init__(
            message
            or "Este cambio puede afectar fases posteriores ya iniciadas. ¿Deseas aplicar la corrección manual?"
        )


def division_category_label(division: str) -> str:
    return "Colegios" if division == DivisionType.SCHOOL else "Universidades"


def stage_sequence(profile: dict):
    return [CompetitionStage.GROUPS, *[stage["stage"] for stage in profile.get("stages", [])]]


def stage_order_map(profile: dict):
    return {stage: index for index, stage in enumerate(stage_sequence(profile))}


def battle_format_capacity(battle):
    return BATTLE_CAPACITY.get(battle.format_type)


def participant_status_badge(status: str) -> str:
    badges = {
        ParticipantStatus.ACTIVE: "Activo",
        ParticipantStatus.ELIMINATED: "Eliminado",
        ParticipantStatus.REPECHAGE: "En repechaje",
        ParticipantStatus.QUALIFIED: "Clasificado",
        ParticipantStatus.WITHDRAWN: "Retirado",
    }
    return badges.get(status, status)


def randomized_teams(edition, division: str):
    category_label = division_category_label(division)
    return list(
        Team.objects.filter(
            edition=edition,
            category_label=category_label,
            status="approved",
        ).select_related("institution")
    )


def stage_battles(competition, stage):
    return list(
        competition.battles.filter(stage=stage)
        .prefetch_related("entries__team__institution")
        .order_by("order")
    )


def manual_overrides_from_profile(profile: dict) -> dict:
    if profile.get("mode_source") != "manual":
        return {}
    return {
        "mode_source": "manual",
        "group_count": profile.get("group_count", 0),
        "qualifiers_per_group": profile.get("qualifiers_per_group", 0),
        "allow_purgatory_one": profile.get("allow_purgatory_one", False),
        "allow_purgatory_two": profile.get("allow_purgatory_two", False),
        "enable_third_place": profile.get("enable_third_place", True),
    }


def competition_profile_from_instance(competition):
    configuration = competition.configuration or {}
    team_count = configuration.get("team_count")
    if team_count is None:
        team_count = len(randomized_teams(competition.edition, competition.division))
    if {"group_count", "qualifiers_per_group", "stages"}.issubset(configuration.keys()):
        profile = {**configuration}
        profile.setdefault("mode_source", "auto")
        profile.setdefault("team_count", team_count)
        profile.setdefault("group_labels", GROUP_LABELS[:profile.get("group_count", 0)])
        profile.setdefault("allow_purgatory_one", bool(profile.get("uses_revival")))
        profile.setdefault("allow_purgatory_two", False)
        profile.setdefault("uses_revival", bool(profile.get("allow_purgatory_one")))
        profile.setdefault("enable_third_place", True)
        return profile
    profile = competition_profile(team_count, manual_overrides_from_profile(configuration))
    profile["group_labels"] = configuration.get("group_labels", GROUP_LABELS[:profile.get("group_count", 0)])
    return profile


def progressive_flow_enabled(competition):
    return bool((competition.configuration or {}).get("progressive_flow"))


def ensure_team_states(competition):
    team_ids = set(DivisionGroupEntry.objects.filter(group__competition=competition).values_list("team_id", flat=True))
    team_ids.update(
        CompetitionBattleEntry.objects.filter(battle__competition=competition).values_list("team_id", flat=True)
    )
    existing = {
        state.team_id: state
        for state in TeamCompetitionState.objects.filter(competition=competition).select_related(
            "current_group",
            "current_battle",
            "team__institution",
        )
    }
    missing = [
        TeamCompetitionState(competition=competition, team_id=team_id)
        for team_id in team_ids
        if team_id not in existing
    ]
    if missing:
        TeamCompetitionState.objects.bulk_create(missing)
    TeamCompetitionState.objects.filter(competition=competition).exclude(team_id__in=team_ids).delete()


def record_history(
    *,
    competition,
    team,
    action_type,
    title,
    description="",
    stage="",
    status="",
    previous_stage="",
    new_stage="",
    previous_status="",
    new_status="",
    previous_group=None,
    new_group=None,
    battle=None,
    metadata=None,
):
    CompetitionHistoryEntry.objects.create(
        competition=competition,
        team=team,
        action_type=action_type,
        title=title,
        description=description,
        stage=stage or "",
        status=status or "",
        previous_stage=previous_stage or "",
        new_stage=new_stage or "",
        previous_status=previous_status or "",
        new_status=new_status or "",
        previous_group=previous_group,
        new_group=new_group,
        battle=battle,
        metadata=metadata or {},
    )


def participant_row_payload(state):
    return {
        "state_id": state.id,
        "team_id": state.team_id,
        "robot_name": state.team.robot_name,
        "institution_name": state.team.institution.name if state.team.institution_id else "",
        "group_label": state.current_group.label if state.current_group_id else "Sin grupo",
        "stage_label": STAGE_TITLES.get(state.current_stage, state.current_stage),
        "status_label": participant_status_badge(state.current_status),
        "status_key": state.current_status,
        "is_clickable": True,
    }


def battle_map(competition):
    grouped = defaultdict(list)
    for battle in competition.battles.prefetch_related("entries__team").order_by("stage", "order"):
        grouped[battle.stage].append(battle)
    return grouped


def qualifier_pairings(group_labels: list[str], qualifiers_per_group: int) -> list[tuple[str, str]]:
    pairings = []
    for index in range(0, len(group_labels), 2):
        left = group_labels[index]
        right = group_labels[index + 1]
        left_slots = [f"{rank}{left}" for rank in range(1, qualifiers_per_group + 1)]
        right_slots = [f"{rank}{right}" for rank in range(1, qualifiers_per_group + 1)]
        pairings.extend(zip(left_slots, reversed(right_slots)))
    return pairings


def battle_is_locked(battle) -> bool:
    return battle.winner_id is not None or battle.status in {MatchStatus.IN_PROGRESS, MatchStatus.FINISHED}


def competition_has_started_flow(competition) -> bool:
    group_results_exist = DivisionGroupEntry.objects.filter(group__competition=competition).filter(
        Q(qualified_from_group=True) | Q(final_rank__isnull=False)
    ).exists()
    battle_entries_exist = CompetitionBattleEntry.objects.filter(battle__competition=competition).exists()
    battle_results_exist = competition.battles.filter(
        Q(winner__isnull=False) | ~Q(status=MatchStatus.PENDING)
    ).exists()
    return group_results_exist or battle_entries_exist or battle_results_exist


def competition_has_rebuild_blockers(competition) -> bool:
    return competition_has_started_flow(competition) or CompetitionHistoryEntry.objects.filter(
        competition=competition
    ).exists()


def stage_has_started(competition, stage) -> bool:
    return competition.battles.filter(stage=stage).filter(
        Q(entries__isnull=False) | Q(winner__isnull=False) | ~Q(status=MatchStatus.PENDING)
    ).distinct().exists()


def later_stages_have_started(competition, stage) -> bool:
    profile = competition_profile_from_instance(competition)
    stages = stage_sequence(profile)
    if stage not in stages:
        return False
    stage_index = stages.index(stage)
    return any(stage_has_started(competition, later_stage) for later_stage in stages[stage_index + 1:])


def validate_profile_change(competition, current_profile: dict, new_profile: dict):
    has_started_flow = competition_has_started_flow(competition)
    has_history = CompetitionHistoryEntry.objects.filter(competition=competition).exists()
    if not has_started_flow and not has_history:
        return

    if current_profile.get("group_count") != new_profile.get("group_count"):
        raise ValueError("No puedes cambiar la cantidad de grupos cuando el torneo ya tiene progreso guardado.")
    if current_profile.get("qualifiers_per_group") != new_profile.get("qualifiers_per_group"):
        raise ValueError("No puedes cambiar los clasificados por grupo cuando el torneo ya tiene progreso guardado.")
    if not has_started_flow:
        return

    current_stages = stage_sequence(current_profile)[1:]
    new_stages = stage_sequence(new_profile)[1:]
    new_stage_set = set(new_stages)
    for stage in current_stages:
        if stage not in new_stage_set and stage_has_started(competition, stage):
            title = STAGE_TITLES.get(stage, stage)
            raise ValueError(f"No puedes quitar {title} porque esa fase ya fue iniciada.")

    if current_profile.get("allow_purgatory_one") != new_profile.get("allow_purgatory_one"):
        active_stages = set(current_stages) | set(new_stages)
        if any(stage_has_started(competition, stage) for stage in active_stages):
            raise ValueError("No puedes cambiar el Purgatorio 1 cuando ya hay fases iniciadas.")

    if current_profile.get("allow_purgatory_two") != new_profile.get("allow_purgatory_two"):
        downstream_stages = [
            CompetitionStage.QUARTERFINAL,
            CompetitionStage.SEMIFINAL,
            CompetitionStage.THIRD_PLACE,
            CompetitionStage.FINAL,
        ]
        if any(stage_has_started(competition, stage) for stage in downstream_stages):
            raise ValueError("No puedes cambiar el Purgatorio 2 cuando el cierre del torneo ya fue iniciado.")


def profile_configuration(competition, profile: dict, team_count: int, reset_progressive_state: bool = False) -> dict:
    existing_labels = (competition.configuration or {}).get("group_labels") or []
    existing_progressive_flow = (competition.configuration or {}).get("progressive_flow", True)
    group_count = profile.get("group_count", 0)
    group_labels = existing_labels if len(existing_labels) == group_count else GROUP_LABELS[:group_count]
    configuration = {**profile}
    if reset_progressive_state:
        configuration.pop("pending_integration_plan", None)
        progressive_metadata_keys = {
            "progressive_created",
            "title",
            "kind",
            "target_stage",
            "target_bracket_size",
            "bye_count",
            "preliminary_players",
            "winners_needed",
        }
        configuration["stages"] = [
            {key: value for key, value in stage_config.items() if key not in progressive_metadata_keys}
            for stage_config in configuration.get("stages", [])
        ]
    return {
        **configuration,
        "team_count": team_count,
        "group_labels": group_labels,
        "progressive_flow": True if reset_progressive_state else existing_progressive_flow,
        "progressive_created_stages": []
        if reset_progressive_state
        else list((competition.configuration or {}).get("progressive_created_stages", [])),
    }


def stage_format_for_profile(stage, profile):
    format_type = STAGE_FORMATS[stage]
    if stage == CompetitionStage.QUARTERFINAL and profile.get("uses_revival"):
        format_type = BattleFormat.TRIANGULAR
    return format_type


def ensure_stage_battles(competition, profile: dict):
    existing = {
        (battle.stage, battle.order): battle
        for battle in competition.battles.prefetch_related("entries").all()
    }
    for stage_config in profile.get("stages", []):
        stage = stage_config["stage"]
        for order in range(1, stage_config["count"] + 1):
            format_type = stage_format_for_profile(stage, profile)
            name = f"{STAGE_LABELS[stage]} {order}"
            battle = existing.get((stage, order))
            if battle is None:
                CompetitionBattle.objects.create(
                    competition=competition,
                    stage=stage,
                    format_type=format_type,
                    order=order,
                    name=name,
                )
                continue
            if battle_is_locked(battle) or battle.entries.exists():
                continue
            if battle.format_type != format_type or battle.name != name:
                battle.format_type = format_type
                battle.name = name
                battle.save(update_fields=["format_type", "name", "updated_at"])


def rebuild_competition_scaffold(competition, teams, profile, reset_progressive_state: bool = False):
    competition.name = f"{competition.edition.name} - {division_category_label(competition.division)}"
    competition.format_key = profile["key"]
    competition.configuration = profile_configuration(
        competition,
        profile,
        len(teams),
        reset_progressive_state=reset_progressive_state,
    )
    competition.shuffle_seed = random.randint(1000, 999999)
    competition.status = CompetitionStatus.DRAFT
    competition.save(update_fields=["name", "format_key", "configuration", "shuffle_seed", "status"])

    competition.groups.all().delete()
    competition.battles.all().delete()
    TeamCompetitionState.objects.filter(competition=competition).delete()
    CompetitionHistoryEntry.objects.filter(competition=competition).delete()

    if profile["group_count"] == 0:
        return competition

    rng = random.Random(competition.shuffle_seed)
    rng.shuffle(teams)

    group_labels = GROUP_LABELS[:profile["group_count"]]
    group_sizes = balanced_group_sizes(len(teams), len(group_labels))
    index = 0
    for order, (label, expected_size) in enumerate(zip(group_labels, group_sizes), start=1):
        group = DivisionGroup.objects.create(
            competition=competition,
            label=label,
            order=order,
            expected_size=expected_size,
        )
        for slot_order in range(1, expected_size + 1):
            team = teams[index]
            index += 1
            DivisionGroupEntry.objects.create(group=group, team=team, slot_order=slot_order)

    if not progressive_flow_enabled(competition):
        for stage_config in profile["stages"]:
            stage = stage_config["stage"]
            for order in range(1, stage_config["count"] + 1):
                CompetitionBattle.objects.create(
                    competition=competition,
                    stage=stage,
                    format_type=stage_format_for_profile(stage, profile),
                    order=order,
                    name=f"{STAGE_LABELS[stage]} {order}",
                )

    ensure_team_states(competition)
    sync_competition(competition)
    return competition


@transaction.atomic
def initialize_competition(
    edition,
    division: str,
    overrides: dict | None = None,
    preserve_existing_profile: bool = False,
):
    teams = randomized_teams(edition, division)
    requested_profile = competition_profile(len(teams), overrides)
    competition, created = DivisionCompetition.objects.get_or_create(
        edition=edition,
        division=division,
        defaults={
            "name": f"{edition.name} - {division_category_label(division)}",
            "format_key": requested_profile["key"],
            "configuration": requested_profile,
            "shuffle_seed": random.randint(1000, 999999),
            "status": CompetitionStatus.DRAFT,
        },
    )
    if preserve_existing_profile and not created and overrides is None:
        requested_profile = competition_profile_from_instance(competition)

    if created or not competition_has_rebuild_blockers(competition):
        return rebuild_competition_scaffold(competition, teams, requested_profile)

    current_profile = competition_profile_from_instance(competition)
    validate_profile_change(competition, current_profile, requested_profile)

    competition.name = f"{edition.name} - {division_category_label(division)}"
    competition.format_key = requested_profile["key"]
    competition.configuration = profile_configuration(competition, requested_profile, len(teams))
    competition.save(update_fields=["name", "format_key", "configuration", "updated_at"])
    if not progressive_flow_enabled(competition):
        ensure_stage_battles(competition, requested_profile)
    ensure_team_states(competition)
    sync_competition(competition)
    return competition


@transaction.atomic
def reset_competition_state(competition):
    profile = competition_profile_from_instance(competition)
    teams = randomized_teams(competition.edition, competition.division)
    return rebuild_competition_scaffold(competition, teams, profile, reset_progressive_state=True)


def attach_group_payload(competition):
    groups_payload = []
    for group in competition.groups.prefetch_related("entries__team__institution").order_by("order"):
        entries = []
        for entry in group.entries.order_by("slot_order"):
            state = TeamCompetitionState.objects.filter(competition=competition, team=entry.team).select_related(
                "team__institution",
                "current_group",
                "current_battle",
            ).first()
            entries.append(
                {
                    "entry": entry,
                    "state": state,
                    "participant": participant_row_payload(state) if state else None,
                }
            )
        groups_payload.append({"group": group, "entries": entries})
    return groups_payload


@transaction.atomic
def set_group_qualifiers(group, selected_entry_ids: list[int], manual_override: bool = False):
    competition = group.competition
    profile = competition_profile_from_instance(competition)
    qualifiers_per_group = profile["qualifiers_per_group"]
    entries = list(group.entries.select_related("team").order_by("slot_order"))
    if qualifiers_per_group > len(entries):
        raise ValueError("Este grupo no tiene suficientes carros para la cantidad de clasificados definida.")

    submitted_ids = {int(entry_id) for entry_id in selected_entry_ids}
    valid_ids = {entry.id for entry in entries}
    if not submitted_ids.issubset(valid_ids):
        raise ValueError("Se enviaron carros que no pertenecen al grupo.")
    if len(submitted_ids) != qualifiers_per_group:
        raise ValueError(f"Debes seleccionar exactamente {qualifiers_per_group} clasificado(s) en este grupo.")
    current_qualified_ids = {entry.id for entry in entries if entry.qualified_from_group}
    manual_correction_applied = False
    if submitted_ids != current_qualified_ids and later_stages_have_started(competition, CompetitionStage.GROUPS):
        if not manual_override:
            raise ManualCorrectionRequired()
        manual_correction_applied = True

    qualifier_rank = 1
    for entry in entries:
        previous_rank = entry.final_rank
        was_qualified = entry.qualified_from_group
        entry.qualified_from_group = entry.id in submitted_ids
        if entry.qualified_from_group:
            entry.final_rank = qualifier_rank
            qualifier_rank += 1
        else:
            entry.final_rank = None
        if was_qualified != entry.qualified_from_group or previous_rank != entry.final_rank:
            title = "Clasifico desde grupos" if entry.qualified_from_group else "No clasifico desde grupos"
            status = ParticipantStatus.QUALIFIED if entry.qualified_from_group else ParticipantStatus.ELIMINATED
            record_history(
                competition=competition,
                team=entry.team,
                action_type=HistoryActionType.GROUP_RESULT,
                title=title,
                description=f"Grupo {group.label}",
                stage=CompetitionStage.GROUPS,
                status=status,
                previous_stage=CompetitionStage.GROUPS,
                new_stage=CompetitionStage.GROUPS,
                previous_group=group,
                new_group=group,
                metadata={"qualified": entry.qualified_from_group, "rank": entry.final_rank},
            )
    DivisionGroupEntry.objects.bulk_update(entries, ["qualified_from_group", "final_rank"])
    sync_competition(competition)
    return {"manual_correction_applied": manual_correction_applied}


def _resequence_group_entries(group):
    entries = list(group.entries.order_by("slot_order", "id"))
    for index, entry in enumerate(entries, start=1):
        entry.slot_order = index
    if entries:
        DivisionGroupEntry.objects.bulk_update(entries, ["slot_order"])
    group.expected_size = len(entries)
    group.save(update_fields=["expected_size", "updated_at"])


def _clear_team_from_battles(competition, team):
    battle_entries = list(
        CompetitionBattleEntry.objects.filter(battle__competition=competition, team=team).select_related("battle")
    )
    affected_battles = {entry.battle for entry in battle_entries}
    if not battle_entries:
        return
    locked_battles = [battle for battle in affected_battles if battle_is_locked(battle)]
    if locked_battles:
        locked_names = ", ".join(battle.name for battle in locked_battles)
        raise ValueError(f"No puedes mover este participante porque ya tiene resultado en: {locked_names}.")
    CompetitionBattleEntry.objects.filter(pk__in=[entry.pk for entry in battle_entries]).delete()
    for battle in affected_battles:
        if battle.winner_id == team.id:
            battle.winner = None
            battle.status = MatchStatus.PENDING
            battle.save(update_fields=["winner", "status", "updated_at"])


def _pick_battle_for_stage(competition, stage, battle_id=None):
    battles = list(competition.battles.filter(stage=stage).prefetch_related("entries").order_by("order"))
    if not battles:
        raise ValueError("La fase seleccionada no tiene batallas configuradas.")
    if battle_id:
        battle = next((battle for battle in battles if battle.id == int(battle_id)), None)
        if battle is None:
            raise ValueError("La batalla seleccionada no pertenece a esta fase.")
        return battle
    for battle in battles:
        capacity = battle_format_capacity(battle)
        current_count = battle.entries.count()
        if capacity is None or current_count < capacity:
            return battle
    return battles[0]


@transaction.atomic
def update_group_layout(competition, assignments_by_entry_id: dict[int, int]):
    if competition_has_started_flow(competition):
        raise ValueError("No puedes reorganizar grupos cuando ya hay clasificados, batallas o resultados guardados.")
    profile = competition_profile_from_instance(competition)
    entries = list(
        DivisionGroupEntry.objects.filter(group__competition=competition)
        .select_related("group", "team")
        .order_by("group__order", "slot_order", "team__robot_name")
    )
    groups = list(competition.groups.order_by("order"))
    valid_group_ids = {group.id for group in groups}
    valid_entry_ids = {entry.id for entry in entries}
    submitted_entry_ids = {int(entry_id) for entry_id in assignments_by_entry_id.keys()}
    if submitted_entry_ids != valid_entry_ids:
        raise ValueError("La distribucion enviada no coincide con los carros actuales del torneo.")

    grouped_entries = defaultdict(list)
    for entry in entries:
        target_group_id = int(assignments_by_entry_id[entry.id])
        if target_group_id not in valid_group_ids:
            raise ValueError("Se intento mover un carro a un grupo invalido.")
        grouped_entries[target_group_id].append(entry)

    for group in groups:
        entry_count = len(grouped_entries[group.id])
        if entry_count == 0:
            raise ValueError("No puedes dejar grupos vacios.")
        if entry_count < profile["qualifiers_per_group"]:
            raise ValueError(
                f"El Grupo {group.label} quedaria con menos carros que los clasificados requeridos."
            )
        group.expected_size = entry_count
    DivisionGroup.objects.bulk_update(groups, ["expected_size"])

    updated_entries = []
    for group in groups:
        bucket = grouped_entries[group.id]
        for slot_order, entry in enumerate(bucket, start=1):
            if entry.group_id != group.id:
                record_history(
                    competition=competition,
                    team=entry.team,
                    action_type=HistoryActionType.MANUAL_MOVE,
                    title="Cambio manual de grupo",
                    description=f"Movido al Grupo {group.label}",
                    stage=CompetitionStage.GROUPS,
                    status=ParticipantStatus.ACTIVE,
                    previous_stage=CompetitionStage.GROUPS,
                    new_stage=CompetitionStage.GROUPS,
                    previous_group=entry.group,
                    new_group=group,
                )
            entry.group = group
            entry.slot_order = slot_order
            entry.qualified_from_group = False
            entry.final_rank = None
            updated_entries.append(entry)

    for temporary_order, entry in enumerate(entries, start=1000):
        entry.slot_order = temporary_order
    DivisionGroupEntry.objects.bulk_update(entries, ["slot_order"])

    DivisionGroupEntry.objects.bulk_update(
        updated_entries,
        ["group", "slot_order", "qualified_from_group", "final_rank"],
    )
    sync_competition(competition)


@transaction.atomic
def set_battle_winner(battle, winner_team_id: int, manual_override: bool = False):
    team_ids = list(battle.entries.values_list("team_id", flat=True))
    if winner_team_id not in team_ids:
        raise ValueError("El ganador debe pertenecer a la batalla.")
    if battle.winner_id and battle.winner_id != winner_team_id and later_stages_have_started(
        battle.competition,
        battle.stage,
    ):
        if not manual_override:
            raise ManualCorrectionRequired()
        manual_correction_applied = True
    else:
        manual_correction_applied = False
    battle.winner_id = winner_team_id
    battle.status = MatchStatus.FINISHED
    battle.save(update_fields=["winner", "status", "updated_at"])

    for entry in battle.entries.select_related("team"):
        won = entry.team_id == winner_team_id
        record_history(
            competition=battle.competition,
            team=entry.team,
            action_type=HistoryActionType.BATTLE_RESULT,
            title="Gano batalla" if won else "Perdio batalla",
            description=battle.name,
            stage=battle.stage,
            status=ParticipantStatus.ACTIVE if won else ParticipantStatus.ELIMINATED,
            battle=battle,
            metadata={"winner": won},
        )
    sync_competition(battle.competition)
    return {"manual_correction_applied": manual_correction_applied}


def clear_battles(battles):
    for battle in battles:
        if battle_is_locked(battle):
            continue
        battle.entries.all().delete()
        if battle.winner_id or battle.status != MatchStatus.PENDING:
            battle.winner = None
            battle.status = MatchStatus.PENDING
            battle.save(update_fields=["winner", "status", "updated_at"])


def set_battle_entries(battle, entry_specs):
    current_entries = list(battle.entries.order_by("slot_order").values_list("team_id", "origin_label"))
    desired_entries = [(team.id, origin_label) for team, origin_label in entry_specs]
    if current_entries == desired_entries:
        return
    if battle_is_locked(battle):
        return

    battle.entries.all().delete()
    CompetitionBattleEntry.objects.bulk_create(
        [
            CompetitionBattleEntry(
                battle=battle,
                team=team,
                slot_order=slot_order,
                origin_label=origin_label,
            )
            for slot_order, (team, origin_label) in enumerate(entry_specs, start=1)
        ]
    )
    battle.winner = None
    battle.status = MatchStatus.READY if entry_specs else MatchStatus.PENDING
    battle.save(update_fields=["winner", "status", "updated_at"])


def _ensure_stage_in_configuration(competition, stage, battle_count, **metadata):
    configuration = {**(competition.configuration or {})}
    configuration["progressive_flow"] = True
    stages = [dict(item) for item in configuration.get("stages", [])]
    found = False
    for stage_config in stages:
        if stage_config.get("stage") != stage:
            continue
        found = True
        stage_config["count"] = max(int(stage_config.get("count") or 0), battle_count)
        stage_config["progressive_created"] = True
        stage_config.update(metadata)
        break
    if not found:
        stages.append({
            "stage": stage,
            "count": battle_count,
            "progressive_created": True,
            **metadata,
        })
    created_stages = list(configuration.get("progressive_created_stages", []))
    if stage not in created_stages:
        created_stages.append(stage)
    configuration["stages"] = stages
    configuration["progressive_created_stages"] = created_stages
    competition.configuration = configuration
    competition.save(update_fields=["configuration", "updated_at"])


def _stage_config(competition, stage):
    for stage_config in (competition.configuration or {}).get("stages", []):
        if stage_config.get("stage") == stage:
            return stage_config
    return {}


def _progressive_active_states(competition):
    return list(
        TeamCompetitionState.objects.filter(
            competition=competition,
            current_status__in=[ParticipantStatus.ACTIVE, ParticipantStatus.QUALIFIED],
        )
        .select_related("team__institution", "current_group", "current_battle")
        .order_by("team__robot_name", "team_id")
    )


def _recent_eliminated_states(competition):
    finished_battles = list(
        competition.battles.filter(status=MatchStatus.FINISHED, winner__isnull=False)
        .prefetch_related("entries__team__institution")
        .order_by("stage", "order")
    )
    if not finished_battles:
        return []
    order_map = stage_order_map(competition_profile_from_instance(competition))
    latest_stage = max(finished_battles, key=lambda battle: order_map.get(battle.stage, 0)).stage
    team_ids = {
        entry.team_id
        for battle in finished_battles
        if battle.stage == latest_stage
        for entry in battle.entries.all()
        if entry.team_id != battle.winner_id
    }
    if not team_ids:
        return []
    return list(
        TeamCompetitionState.objects.filter(competition=competition, team_id__in=team_ids)
        .select_related("team__institution", "current_group", "current_battle")
        .order_by("team__robot_name", "team_id")
    )


def _repechage_candidate_states(competition):
    recent = _recent_eliminated_states(competition)
    repechable = list(
        TeamCompetitionState.objects.filter(competition=competition, current_status=ParticipantStatus.REPECHAGE)
        .select_related("team__institution", "current_group", "current_battle")
        .order_by("team__robot_name", "team_id")
    )
    eliminated = list(
        TeamCompetitionState.objects.filter(competition=competition, current_status=ParticipantStatus.ELIMINATED)
        .select_related("team__institution", "current_group", "current_battle")
        .order_by("team__robot_name", "team_id")
    )
    source = recent or repechable or eliminated
    candidates = []
    seen = set()
    for state in source:
        if state.team_id in seen:
            continue
        seen.add(state.team_id)
        candidates.append(state)
    return candidates


def _next_available_stage(competition, stage_pool):
    created = set((competition.configuration or {}).get("progressive_created_stages", []))
    for stage in stage_pool:
        has_entries = CompetitionBattleEntry.objects.filter(battle__competition=competition, battle__stage=stage).exists()
        if stage not in created and not has_entries:
            return stage
    return None


def _ensure_progressive_battles(competition, stage, battle_count, *, format_type=BattleFormat.DUEL, name_prefix=None):
    battles = {
        battle.order: battle
        for battle in competition.battles.filter(stage=stage).prefetch_related("entries").order_by("order")
    }
    ensured = []
    for order in range(1, battle_count + 1):
        battle = battles.get(order)
        name = f"{name_prefix or STAGE_LABELS[stage]} {order}"
        if battle is None:
            battle = CompetitionBattle.objects.create(
                competition=competition,
                stage=stage,
                format_type=format_type,
                order=order,
                name=name,
            )
        elif not battle_is_locked(battle) and not battle.entries.exists():
            changed_fields = []
            if battle.format_type != format_type:
                battle.format_type = format_type
                changed_fields.append("format_type")
            if battle.name != name:
                battle.name = name
                changed_fields.append("name")
            if changed_fields:
                battle.save(update_fields=[*changed_fields, "updated_at"])
        ensured.append(battle)
    return ensured


def _ensure_progressive_duel_battles(competition, stage, battle_count):
    return _ensure_progressive_battles(competition, stage, battle_count, format_type=BattleFormat.DUEL)


def _stage_has_entries(competition, stage):
    return CompetitionBattleEntry.objects.filter(battle__competition=competition, battle__stage=stage).exists()


def _clear_pending_integration_plan(competition):
    configuration = {**(competition.configuration or {})}
    if "pending_integration_plan" not in configuration:
        return
    configuration.pop("pending_integration_plan", None)
    competition.configuration = configuration
    competition.save(update_fields=["configuration", "updated_at"])


def _existing_open_repechage_stage(competition):
    for stage in REPECHAGE_STAGES:
        if _stage_config(competition, stage).get("kind") == "integration_preliminary":
            continue
        has_open_entries = CompetitionBattleEntry.objects.filter(
            battle__competition=competition,
            battle__stage=stage,
        ).exclude(battle__status=MatchStatus.FINISHED).exists()
        if has_open_entries:
            return stage
    return None


def _safe_repechage_plan(candidate_count):
    if candidate_count == 2:
        return BattleFormat.DUEL, 1, [2]
    if candidate_count == 3:
        return BattleFormat.TRIANGULAR, 1, [3]
    if candidate_count == 4:
        return BattleFormat.DUEL, 2, [2, 2]
    if candidate_count == 6:
        return BattleFormat.TRIANGULAR, 2, [3, 3]
    if candidate_count >= 4:
        battle_count = min(4, max(1, candidate_count // 2))
        base_size = candidate_count // battle_count
        remainder = candidate_count % battle_count
        sizes = [base_size + (1 if index < remainder else 0) for index in range(battle_count)]
        return BattleFormat.BATTLE_ROYALE, battle_count, sizes
    return None, 0, []


def _lower_bracket_size(participant_count):
    for size in BRACKET_SIZES:
        if participant_count > size:
            return size
    return None


def _integration_plan_for_active_states(competition, active_states):
    total = len(active_states)
    if total in SAFE_PROGRESSIVE_DUEL_STAGES:
        return {
            "type": "direct_bracket",
            "target_stage": SAFE_PROGRESSIVE_DUEL_STAGES[total],
            "target_bracket_size": total,
        }
    target = _lower_bracket_size(total)
    if not target:
        return None
    excess = total - target
    preliminary_players = excess * 2
    bye_players = total - preliminary_players
    if preliminary_players < 2 or preliminary_players > total or preliminary_players % 2 != 0 or bye_players < 0:
        return None
    target_stage = SAFE_PROGRESSIVE_DUEL_STAGES.get(target)
    if not target_stage:
        return None
    return {
        "type": "preliminary_duels",
        "target_stage": target_stage,
        "target_bracket_size": target,
        "excess": excess,
        "preliminary_players": preliminary_players,
        "preliminary_battles": preliminary_players // 2,
        "bye_players": bye_players,
    }


def _active_states_need_integration(competition, active_states):
    pending = (competition.configuration or {}).get("pending_integration_plan")
    if pending:
        return True
    stages = {state.current_stage for state in active_states}
    has_recovered = any(state.current_stage in REPECHAGE_STAGES for state in active_states)
    return has_recovered or len(stages) > 1


def _next_available_integration_stage(competition, target_stage):
    pool = [stage for stage in INTEGRATION_STAGE_POOL if stage != target_stage]
    return _next_available_stage(competition, pool)


def _ordered_integration_states(competition, active_states):
    rng = random.Random(f"{competition.shuffle_seed}:integration:{len(active_states)}")
    recovered = [state for state in active_states if state.current_stage in REPECHAGE_STAGES]
    direct = [state for state in active_states if state.current_stage not in REPECHAGE_STAGES]
    rng.shuffle(recovered)
    rng.shuffle(direct)
    return [*recovered, *direct]


def _record_phase_assignment(competition, state, stage, status, battle, title, metadata):
    record_history(
        competition=competition,
        team=state.team,
        action_type=HistoryActionType.AUTO_SYNC,
        title=title,
        description=battle.name,
        stage=stage,
        status=status,
        previous_stage=state.current_stage,
        new_stage=stage,
        previous_status=state.current_status,
        new_status=status,
        battle=battle,
        metadata=metadata,
    )


@transaction.atomic
def materialize_repechage_stage(competition):
    sync_team_states(competition)
    candidates = _repechage_candidate_states(competition)
    format_type, battle_count, sizes = _safe_repechage_plan(len(candidates))
    if not battle_count:
        raise ValueError("Requiere configuracion manual para crear repechaje.")

    open_stage = _existing_open_repechage_stage(competition)
    if open_stage:
        existing_count = competition.battles.filter(stage=open_stage).count()
        _ensure_stage_in_configuration(competition, open_stage, existing_count, title=STAGE_TITLES[open_stage])
        return {
            "created": False,
            "existing": True,
            "stage": open_stage,
            "message": f"{STAGE_TITLES[open_stage]} ya existe. Se abrio la fase existente.",
        }

    stage = _next_available_stage(competition, REPECHAGE_STAGES)
    if stage is None:
        existing_stage = next((candidate.current_stage for candidate in candidates if candidate.current_stage in REPECHAGE_STAGES), None)
        if existing_stage and _stage_has_entries(competition, existing_stage):
            _ensure_stage_in_configuration(competition, existing_stage, battle_count, title=STAGE_TITLES[existing_stage])
            return {
                "created": False,
                "existing": True,
                "stage": existing_stage,
                "message": f"{STAGE_TITLES[existing_stage]} ya existe. Se abrio la fase existente.",
            }
        raise ValueError("Ya existen los repechajes disponibles. Revisa fases creadas antes de abrir otro.")

    title = STAGE_TITLES[stage]
    _ensure_stage_in_configuration(competition, stage, battle_count, title=title, kind="repechage")
    battles = _ensure_progressive_battles(
        competition,
        stage,
        battle_count,
        format_type=format_type,
        name_prefix=title,
    )
    if any(battle_is_locked(battle) or battle.entries.exists() for battle in battles):
        raise ValueError("El repechaje recomendado ya tiene progreso o entradas. Abre la fase existente para revisarlo.")

    cursor = 0
    for battle, size in zip(battles, sizes):
        selected = candidates[cursor: cursor + size]
        cursor += size
        set_battle_entries(
            battle,
            [(state.team, "Candidato a repechaje") for state in selected],
        )
        for state in selected:
            _record_phase_assignment(
                competition=competition,
                stage=stage,
                status=ParticipantStatus.REPECHAGE,
                battle=battle,
                state=state,
                title=f"Asignado a {title}",
                metadata={"progressive_repechage_creation": True},
            )

    competition.status = CompetitionStatus.IN_PROGRESS
    competition.save(update_fields=["status", "updated_at"])
    sync_team_states(competition)
    return {
        "created": True,
        "existing": False,
        "stage": stage,
        "message": f"Se creo {title} con {battle_count} batalla(s).",
    }


def _semifinal_losers_for_third_place(competition):
    semifinal_battles = stage_battles(competition, CompetitionStage.SEMIFINAL)
    if len(semifinal_battles) != 2:
        return []
    return duel_losers(semifinal_battles)


def _materialize_final_and_optional_third_place(competition, active_states):
    profile = competition_profile_from_instance(competition)
    final_stage = CompetitionStage.FINAL
    final_title = STAGE_TITLES[final_stage]
    final_exists = _stage_has_entries(competition, final_stage)
    third_stage = CompetitionStage.THIRD_PLACE
    third_losers = _semifinal_losers_for_third_place(competition)
    should_create_third = bool(profile.get("enable_third_place", True) and len(third_losers) == 2)

    if final_exists:
        _ensure_stage_in_configuration(competition, final_stage, 1, title=final_title)
        if should_create_third and not _stage_has_entries(competition, third_stage):
            _create_single_duel_from_teams(
                competition,
                third_stage,
                third_losers,
                STAGE_TITLES[third_stage],
                "progressive_third_place_creation",
            )
            sync_team_states(competition)
        return {
            "created": False,
            "existing": True,
            "stage": final_stage,
            "message": f"{final_title} ya existe. Se abrio la fase existente.",
        }

    _ensure_stage_in_configuration(competition, final_stage, 1, title=final_title)
    final_battle = _ensure_progressive_duel_battles(competition, final_stage, 1)[0]
    if battle_is_locked(final_battle) or final_battle.entries.exists():
        raise ValueError("La gran final ya tiene progreso o entradas. Abre la fase existente para revisarla.")
    set_battle_entries(final_battle, [(state.team, "Ganador semifinal") for state in active_states])
    for state in active_states:
        _record_phase_assignment(
            competition=competition,
            state=state,
            stage=final_stage,
            status=ParticipantStatus.ACTIVE,
            battle=final_battle,
            title=f"Asignado a {final_title}",
            metadata={"progressive_phase_creation": True},
        )

    message = "Se creo Gran final."
    if should_create_third:
        _create_single_duel_from_teams(
            competition,
            third_stage,
            third_losers,
            STAGE_TITLES[third_stage],
            "progressive_third_place_creation",
        )
        message = "Se crearon Gran final y Tercer lugar."

    competition.status = CompetitionStatus.IN_PROGRESS
    competition.save(update_fields=["status", "updated_at"])
    sync_team_states(competition)
    return {
        "created": True,
        "existing": False,
        "stage": final_stage,
        "message": message,
    }


def _create_single_duel_from_teams(competition, stage, teams, title, metadata_key):
    _ensure_stage_in_configuration(competition, stage, 1, title=title)
    battle = _ensure_progressive_duel_battles(competition, stage, 1)[0]
    if battle_is_locked(battle) or battle.entries.exists():
        return battle
    set_battle_entries(battle, [(team, title) for team in teams])
    states = {
        state.team_id: state
        for state in TeamCompetitionState.objects.filter(competition=competition, team__in=teams).select_related("team")
    }
    for team in teams:
        state = states.get(team.id)
        if state:
            _record_phase_assignment(
                competition=competition,
                state=state,
                stage=stage,
                status=ParticipantStatus.ACTIVE,
                battle=battle,
                title=f"Asignado a {title}",
                metadata={metadata_key: True},
            )
    return battle


def _materialize_integration_preliminary(competition, active_states, plan):
    stage = _next_available_integration_stage(competition, plan["target_stage"])
    if stage is None:
        raise ValueError("No hay una etapa tecnica disponible para crear la ronda previa de integracion sin migracion.")

    ordered_states = _ordered_integration_states(competition, active_states)
    preliminary_states = ordered_states[:plan["preliminary_players"]]
    bye_states = ordered_states[plan["preliminary_players"]:]
    title = "Ronda previa de integracion"
    _ensure_stage_in_configuration(
        competition,
        stage,
        plan["preliminary_battles"],
        title=title,
        kind="integration_preliminary",
        target_stage=plan["target_stage"],
        target_bracket_size=plan["target_bracket_size"],
        bye_count=len(bye_states),
        preliminary_players=len(preliminary_states),
        winners_needed=plan["excess"],
    )
    battles = _ensure_progressive_battles(
        competition,
        stage,
        plan["preliminary_battles"],
        format_type=BattleFormat.DUEL,
        name_prefix=title,
    )
    if any(battle_is_locked(battle) or battle.entries.exists() for battle in battles):
        raise ValueError("La ronda previa de integracion ya tiene progreso o entradas. Abre la fase existente para revisarla.")

    configuration = {**(competition.configuration or {})}
    configuration["pending_integration_plan"] = {
        "stage": stage,
        "target_stage": plan["target_stage"],
        "target_bracket_size": plan["target_bracket_size"],
        "bye_team_ids": [state.team_id for state in bye_states],
        "preliminary_team_ids": [state.team_id for state in preliminary_states],
        "winners_needed": plan["excess"],
        "source_total": len(active_states),
    }
    competition.configuration = configuration
    competition.save(update_fields=["configuration", "updated_at"])

    for battle_index, battle in enumerate(battles):
        left = preliminary_states[battle_index * 2]
        right = preliminary_states[battle_index * 2 + 1]
        set_battle_entries(
            battle,
            [
                (left.team, "Integracion previa"),
                (right.team, "Integracion previa"),
            ],
        )
        for state in (left, right):
            _record_phase_assignment(
                competition=competition,
                stage=stage,
                status=ParticipantStatus.ACTIVE,
                battle=battle,
                state=state,
                title=f"Asignado a {title}",
                metadata={"progressive_integration_preliminary": True},
            )

    for state in bye_states:
        record_history(
            competition=competition,
            team=state.team,
            action_type=HistoryActionType.AUTO_SYNC,
            title="Bye de integracion",
            description=f"Espera la llave limpia de {plan['target_bracket_size']} participantes.",
            stage=stage,
            status=ParticipantStatus.ACTIVE,
            previous_stage=state.current_stage,
            new_stage=state.current_stage,
            previous_status=state.current_status,
            new_status=ParticipantStatus.ACTIVE,
            metadata={"progressive_integration_bye": True, "target_stage": plan["target_stage"]},
        )

    competition.status = CompetitionStatus.IN_PROGRESS
    competition.save(update_fields=["status", "updated_at"])
    sync_team_states(competition)
    return {
        "created": True,
        "existing": False,
        "stage": stage,
        "message": (
            f"Se creo {title} con {plan['preliminary_battles']} duelo(s). "
            f"{len(bye_states)} participante(s) esperan con bye."
        ),
    }


@transaction.atomic
def materialize_recommended_duel_stage(competition):
    sync_team_states(competition)
    active_states = _progressive_active_states(competition)
    active_count = len(active_states)
    plan = _integration_plan_for_active_states(competition, active_states)
    needs_integration = _active_states_need_integration(competition, active_states)

    if needs_integration and plan and plan["type"] == "preliminary_duels":
        pending = (competition.configuration or {}).get("pending_integration_plan") or {}
        pending_stage = pending.get("stage")
        if pending_stage and _stage_has_entries(competition, pending_stage):
            open_entries = CompetitionBattleEntry.objects.filter(
                battle__competition=competition,
                battle__stage=pending_stage,
            ).exclude(battle__status=MatchStatus.FINISHED).exists()
            if open_entries:
                _ensure_stage_in_configuration(competition, pending_stage, plan["preliminary_battles"], title="Ronda previa de integracion")
                return {
                    "created": False,
                    "existing": True,
                    "stage": pending_stage,
                    "message": "La ronda previa de integracion ya existe. Se abrio la fase existente.",
                }
        return _materialize_integration_preliminary(competition, active_states, plan)

    target_stage = SAFE_PROGRESSIVE_DUEL_STAGES.get(active_count)
    if needs_integration and plan and plan["type"] == "direct_bracket":
        target_stage = plan["target_stage"]
    if target_stage is None:
        raise ValueError("Requiere configuracion manual proximamente.")
    active_stage_keys = {state.current_stage for state in active_states}
    if len(active_stage_keys) > 1 and not needs_integration:
        raise ValueError("Los participantes activos aparecen en mas de una fase. Revisa la consistencia antes de crear otra fase.")

    battle_count = active_count // 2
    if target_stage == CompetitionStage.FINAL:
        result = _materialize_final_and_optional_third_place(competition, active_states)
        if result.get("created") or result.get("existing"):
            _clear_pending_integration_plan(competition)
        return result

    existing_stage_entries = CompetitionBattleEntry.objects.filter(
        battle__competition=competition,
        battle__stage=target_stage,
    ).exists()
    if existing_stage_entries:
        _ensure_stage_in_configuration(competition, target_stage, battle_count)
        _clear_pending_integration_plan(competition)
        return {
            "created": False,
            "existing": True,
            "stage": target_stage,
            "message": f"{STAGE_TITLES[target_stage]} ya existe. Se abrio la fase existente.",
        }

    _ensure_stage_in_configuration(competition, target_stage, battle_count)
    battles = _ensure_progressive_duel_battles(competition, target_stage, battle_count)
    if any(battle_is_locked(battle) or battle.entries.exists() for battle in battles):
        raise ValueError("La fase recomendada ya tiene progreso o entradas. Abre la fase existente para revisarla.")

    rng = random.Random(f"{competition.shuffle_seed}:{target_stage}:{active_count}")
    rng.shuffle(active_states)
    for battle_index, battle in enumerate(battles):
        left = active_states[battle_index * 2]
        right = active_states[battle_index * 2 + 1]
        set_battle_entries(
            battle,
            [
                (left.team, f"Activo {battle_index * 2 + 1}"),
                (right.team, f"Activo {battle_index * 2 + 2}"),
            ],
        )
        for state in (left, right):
            _record_phase_assignment(
                competition=competition,
                stage=target_stage,
                status=ParticipantStatus.ACTIVE,
                battle=battle,
                state=state,
                title=f"Asignado a {STAGE_TITLES[target_stage]}",
                metadata={"progressive_phase_creation": True},
            )

    competition.status = CompetitionStatus.IN_PROGRESS
    competition.save(update_fields=["status", "updated_at"])
    _clear_pending_integration_plan(competition)
    sync_team_states(competition)
    return {
        "created": True,
        "existing": False,
        "stage": target_stage,
        "message": f"Se creo {STAGE_TITLES[target_stage]} con {battle_count} duelo(s).",
    }


@transaction.atomic
def materialize_manual_duel_stage(competition, *, name, participant_count):
    sync_team_states(competition)
    name = (name or "Fase manual").strip()[:80]
    if participant_count < 2 or participant_count % 2 != 0:
        raise ValueError("La fase manual segura requiere una cantidad par de participantes.")
    active_states = _progressive_active_states(competition)
    if participant_count > len(active_states):
        raise ValueError("No hay suficientes participantes activos para crear esta fase manual.")

    for stage_config in (competition.configuration or {}).get("stages", []):
        if stage_config.get("progressive_created") and stage_config.get("title", "").strip().lower() == name.lower():
            raise ValueError("Ya existe una fase progresiva con ese nombre.")

    stage = _next_available_stage(competition, MANUAL_STAGE_POOL)
    if stage is None:
        raise ValueError("No hay una etapa tecnica disponible para crear otra fase manual sin migracion.")

    selected = active_states[:participant_count]
    battle_count = participant_count // 2
    _ensure_stage_in_configuration(competition, stage, battle_count, title=name, kind="manual")
    battles = _ensure_progressive_battles(
        competition,
        stage,
        battle_count,
        format_type=BattleFormat.DUEL,
        name_prefix=name,
    )
    if any(battle_is_locked(battle) or battle.entries.exists() for battle in battles):
        raise ValueError("La fase manual seleccionada ya tiene progreso o entradas.")

    for index, battle in enumerate(battles):
        left = selected[index * 2]
        right = selected[index * 2 + 1]
        set_battle_entries(
            battle,
            [
                (left.team, "Seleccion manual"),
                (right.team, "Seleccion manual"),
            ],
        )
        for state in (left, right):
            _record_phase_assignment(
                competition=competition,
                state=state,
                stage=stage,
                status=ParticipantStatus.ACTIVE,
                battle=battle,
                title=f"Asignado a {name}",
                metadata={"progressive_manual_creation": True},
            )

    competition.status = CompetitionStatus.IN_PROGRESS
    competition.save(update_fields=["status", "updated_at"])
    sync_team_states(competition)
    return {
        "created": True,
        "existing": False,
        "stage": stage,
        "message": f"Se creo {name} con {battle_count} duelo(s).",
    }


def group_entries_by_group(competition):
    groups = list(competition.groups.prefetch_related("entries__team__institution").order_by("order"))
    return [(group, list(group.entries.order_by("slot_order"))) for group in groups]


def groups_are_complete(competition, qualifiers_per_group):
    for group in competition.groups.prefetch_related("entries").all():
        entries = list(group.entries.all())
        if len(entries) < qualifiers_per_group:
            return False
        if sum(1 for entry in entries if entry.qualified_from_group) != qualifiers_per_group:
            return False
    return True


def battle_winners(battles):
    winners = []
    for battle in battles:
        if battle.status != MatchStatus.FINISHED or battle.winner_id is None:
            return []
        winners.append(battle.winner)
    return winners


def duel_losers(battles):
    losers = []
    for battle in battles:
        entries = list(battle.entries.select_related("team").order_by("slot_order"))
        if battle.status != MatchStatus.FINISHED or battle.winner_id is None or len(entries) != 2:
            return []
        loser = next((entry.team for entry in entries if entry.team_id != battle.winner_id), None)
        if loser is None:
            return []
        losers.append(loser)
    return losers


def seed_duel_stage(battles, pairings, qualifier_lookup):
    for battle, (left_slot, right_slot) in zip(battles, pairings):
        left_team = qualifier_lookup.get(left_slot)
        right_team = qualifier_lookup.get(right_slot)
        if left_team and right_team:
            set_battle_entries(
                battle,
                [
                    (left_team, left_slot),
                    (right_team, right_slot),
                ],
            )
        else:
            set_battle_entries(battle, [])


def seed_next_duel_stage(battles, source_winners, prefix):
    if len(source_winners) != len(battles) * 2:
        clear_battles(battles)
        return
    for index, battle in enumerate(battles):
        set_battle_entries(
            battle,
            [
                (source_winners[index * 2], f"{prefix} {index * 2 + 1}"),
                (source_winners[index * 2 + 1], f"{prefix} {index * 2 + 2}"),
            ],
        )


def wire_final_stages(semifinal_battles, third_place_battles, final_battles, enable_third_place):
    semifinal_winners = battle_winners(semifinal_battles)
    semifinal_losers = duel_losers(semifinal_battles)

    if len(semifinal_winners) == 2:
        set_battle_entries(
            final_battles[0],
            [
                (semifinal_winners[0], "Ganador S1"),
                (semifinal_winners[1], "Ganador S2"),
            ],
        )
    else:
        clear_battles(final_battles)

    if not enable_third_place or not third_place_battles:
        clear_battles(third_place_battles)
        return

    if len(semifinal_losers) == 2:
        set_battle_entries(
            third_place_battles[0],
            [
                (semifinal_losers[0], "Perdedor S1"),
                (semifinal_losers[1], "Perdedor S2"),
            ],
        )
    else:
        clear_battles(third_place_battles)


def setup_basic_profile(competition, profile, qualifier_lookup):
    group_labels = competition.configuration.get("group_labels", [])
    pairings = qualifier_pairings(group_labels, profile["qualifiers_per_group"])
    round_32_battles = stage_battles(competition, CompetitionStage.ROUND_OF_32)
    round_16_battles = stage_battles(competition, CompetitionStage.ROUND_OF_16)
    quarter_battles = stage_battles(competition, CompetitionStage.QUARTERFINAL)
    semifinal_battles = stage_battles(competition, CompetitionStage.SEMIFINAL)
    third_place_battles = stage_battles(competition, CompetitionStage.THIRD_PLACE)
    final_battles = stage_battles(competition, CompetitionStage.FINAL)

    direct_total = profile["qualifier_count"]
    if direct_total == 32:
        seed_duel_stage(round_32_battles, pairings, qualifier_lookup)
        seed_next_duel_stage(round_16_battles, battle_winners(round_32_battles), "Ganador R32")
        seed_next_duel_stage(quarter_battles, battle_winners(round_16_battles), "Ganador O")
    elif direct_total == 16:
        seed_duel_stage(round_16_battles, pairings, qualifier_lookup)
        seed_next_duel_stage(quarter_battles, battle_winners(round_16_battles), "Ganador O")
    elif direct_total == 8:
        seed_duel_stage(quarter_battles, pairings, qualifier_lookup)
    elif direct_total == 4:
        seed_duel_stage(semifinal_battles, pairings, qualifier_lookup)

    if direct_total >= 8:
        seed_next_duel_stage(semifinal_battles, battle_winners(quarter_battles), "Ganador C")

    wire_final_stages(
        semifinal_battles,
        third_place_battles,
        final_battles,
        profile.get("enable_third_place", True),
    )


def setup_revival_profile(competition, profile, qualifier_lookup, elimination_pool):
    group_labels = competition.configuration.get("group_labels", [])
    pairings = qualifier_pairings(group_labels, profile["qualifiers_per_group"])
    purgatory_one_battles = stage_battles(competition, CompetitionStage.PURGATORY_1)
    round_32_battles = stage_battles(competition, CompetitionStage.ROUND_OF_32)
    round_16_battles = stage_battles(competition, CompetitionStage.ROUND_OF_16)
    purgatory_two_battles = stage_battles(competition, CompetitionStage.PURGATORY_2)
    quarter_battles = stage_battles(competition, CompetitionStage.QUARTERFINAL)
    semifinal_battles = stage_battles(competition, CompetitionStage.SEMIFINAL)
    third_place_battles = stage_battles(competition, CompetitionStage.THIRD_PLACE)
    final_battles = stage_battles(competition, CompetitionStage.FINAL)

    purgatory_sizes = balanced_group_sizes(len(elimination_pool), len(purgatory_one_battles))
    cursor = 0
    for battle, size in zip(purgatory_one_battles, purgatory_sizes):
        selected_entries = elimination_pool[cursor: cursor + size]
        cursor += size
        set_battle_entries(
            battle,
            [(entry.team, f"Grupo {entry.group.label}") for entry in selected_entries],
        )

    if profile["qualifier_count"] == 32:
        seed_duel_stage(round_32_battles, pairings, qualifier_lookup)
        seed_next_duel_stage(round_16_battles, battle_winners(round_32_battles), "Ganador R32")
    else:
        seed_duel_stage(round_16_battles, pairings, qualifier_lookup)

    purgatory_one_winners = battle_winners(purgatory_one_battles)
    round_16_winners = battle_winners(round_16_battles)
    round_16_losers = duel_losers(round_16_battles)

    if profile.get("allow_purgatory_two"):
        if len(purgatory_one_winners) == 4 and len(round_16_losers) == 8:
            for index, battle in enumerate(purgatory_two_battles):
                set_battle_entries(
                    battle,
                    [
                        (round_16_losers[index * 2], f"Perdedor O{index * 2 + 1}"),
                        (round_16_losers[index * 2 + 1], f"Perdedor O{index * 2 + 2}"),
                        (purgatory_one_winners[index], f"Campal {index + 1}"),
                    ],
                )
        else:
            clear_battles(purgatory_two_battles)

        purgatory_two_winners = battle_winners(purgatory_two_battles)
        revival_winners = purgatory_two_winners
        revival_label = "Resucitado"
    else:
        clear_battles(purgatory_two_battles)
        revival_winners = purgatory_one_winners
        revival_label = "Campal"

    if len(round_16_winners) == 8 and len(revival_winners) == 4:
        for index, battle in enumerate(quarter_battles):
            set_battle_entries(
                battle,
                [
                    (round_16_winners[index * 2], f"Ganador O{index * 2 + 1}"),
                    (round_16_winners[index * 2 + 1], f"Ganador O{index * 2 + 2}"),
                    (revival_winners[index], f"{revival_label} {index + 1}"),
                ],
            )
    else:
        clear_battles(quarter_battles)

    seed_next_duel_stage(semifinal_battles, battle_winners(quarter_battles), "Ganador C")
    wire_final_stages(
        semifinal_battles,
        third_place_battles,
        final_battles,
        profile.get("enable_third_place", True),
    )


def sync_team_states(competition):
    ensure_team_states(competition)
    profile = competition_profile_from_instance(competition)
    order_map = stage_order_map(profile)
    progressive_flow = progressive_flow_enabled(competition)
    states = {
        state.team_id: state
        for state in TeamCompetitionState.objects.filter(competition=competition).select_related(
            "team",
            "current_group",
            "current_battle",
        )
    }
    group_entries = list(
        DivisionGroupEntry.objects.filter(group__competition=competition)
        .select_related("group", "team")
        .order_by("group__order", "slot_order")
    )
    active_stages = set(stage_sequence(profile)[1:])
    battle_entries = list(
        CompetitionBattleEntry.objects.filter(battle__competition=competition, battle__stage__in=active_stages)
        .select_related("battle", "team")
        .order_by("battle__order")
    )

    entry_by_team = {entry.team_id: entry for entry in group_entries}
    battle_entries_by_team = defaultdict(list)
    for battle_entry in battle_entries:
        battle_entries_by_team[battle_entry.team_id].append(battle_entry)

    updated = []
    for team_id, state in states.items():
        group_entry = entry_by_team.get(team_id)
        state.current_group = group_entry.group if group_entry else None
        state.current_stage = CompetitionStage.GROUPS
        state.current_battle = None
        state.current_status = ParticipantStatus.ACTIVE

        latest_battle_entry = None
        latest_weight = -1
        for battle_entry in battle_entries_by_team.get(team_id, []):
            weight = order_map.get(battle_entry.battle.stage, 0) * 100 + battle_entry.battle.order
            if weight >= latest_weight:
                latest_weight = weight
                latest_battle_entry = battle_entry

        if latest_battle_entry:
            battle = latest_battle_entry.battle
            state.current_group = None
            state.current_battle = battle
            state.current_stage = battle.stage
            stage_config = _stage_config(competition, battle.stage)
            inferred_status = (
                ParticipantStatus.ACTIVE
                if progressive_flow and stage_config.get("kind") == "integration_preliminary"
                else STAGE_STATUS_DEFAULTS.get(battle.stage, ParticipantStatus.ACTIVE)
            )
            if battle.status == MatchStatus.FINISHED:
                if battle.winner_id == team_id:
                    if progressive_flow and battle.stage in REPECHAGE_STAGES:
                        inferred_status = ParticipantStatus.ACTIVE
                    else:
                        inferred_status = (
                            ParticipantStatus.QUALIFIED
                            if battle.stage == CompetitionStage.FINAL
                            else STAGE_STATUS_DEFAULTS.get(battle.stage, ParticipantStatus.ACTIVE)
                        )
                else:
                    inferred_status = ParticipantStatus.ELIMINATED
            state.current_status = inferred_status
        elif group_entry and group_entry.qualified_from_group and groups_are_complete(competition, profile["qualifiers_per_group"]):
            state.current_status = ParticipantStatus.QUALIFIED
        elif group_entry and groups_are_complete(competition, profile["qualifiers_per_group"]) and not group_entry.qualified_from_group:
            state.current_status = (
                ParticipantStatus.REPECHAGE if profile.get("allow_purgatory_one") else ParticipantStatus.ELIMINATED
            )

        if state.manual_status_override:
            state.current_status = state.manual_status_override

        updated.append(state)

    if updated:
        TeamCompetitionState.objects.bulk_update(
            updated,
            ["current_stage", "current_status", "current_group", "current_battle"],
        )


def sync_competition(competition):
    profile = competition_profile_from_instance(competition)
    grouped_battles = battle_map(competition)
    progressive_flow = progressive_flow_enabled(competition)

    if profile["group_count"] == 0:
        competition.status = CompetitionStatus.DRAFT
        competition.save(update_fields=["status", "updated_at"])
        sync_team_states(competition)
        return

    if not groups_are_complete(competition, profile["qualifiers_per_group"]):
        if not progressive_flow:
            for stage in stage_sequence(profile)[1:]:
                clear_battles(grouped_battles.get(stage, []))
        competition.status = CompetitionStatus.DRAFT
        competition.save(update_fields=["status", "updated_at"])
        sync_team_states(competition)
        return

    if progressive_flow:
        final_battles = stage_battles(competition, CompetitionStage.FINAL)
        completed = (
            final_battles
            and final_battles[0].status == MatchStatus.FINISHED
            and final_battles[0].winner_id is not None
        )
        any_finished_battles = competition.battles.filter(status=MatchStatus.FINISHED).exists()
        competition.status = (
            CompetitionStatus.COMPLETED
            if completed
            else CompetitionStatus.IN_PROGRESS
            if any_finished_battles
            else CompetitionStatus.READY
        )
        competition.save(update_fields=["status", "updated_at"])
        sync_team_states(competition)
        return

    groups = group_entries_by_group(competition)
    qualifier_lookup = {}
    elimination_pool = []
    for group, entries in groups:
        qualified_entries = [entry for entry in entries if entry.qualified_from_group]
        for qualifier_position, entry in enumerate(qualified_entries, start=1):
            qualifier_lookup[f"{qualifier_position}{group.label}"] = entry.team
        elimination_pool.extend(entry for entry in entries if not entry.qualified_from_group)

    if profile["uses_revival"]:
        setup_revival_profile(competition, profile, qualifier_lookup, elimination_pool)
    else:
        setup_basic_profile(competition, profile, qualifier_lookup)

    final_battles = stage_battles(competition, CompetitionStage.FINAL)
    completed = (
        final_battles
        and final_battles[0].status == MatchStatus.FINISHED
        and final_battles[0].winner_id is not None
    )
    any_finished_battles = competition.battles.filter(status=MatchStatus.FINISHED).exists()
    competition.status = (
        CompetitionStatus.COMPLETED
        if completed
        else CompetitionStatus.IN_PROGRESS
        if any_finished_battles
        else CompetitionStatus.READY
    )
    competition.save(update_fields=["status", "updated_at"])
    sync_team_states(competition)


def stage_summary(competition):
    profile = competition_profile_from_instance(competition)
    grouped = []
    for stage in stage_sequence(profile)[1:]:
        battles = stage_battles(competition, stage)
        if not battles:
            continue
        grouped.append(
            {
                "stage": stage,
                "title": _stage_config(competition, stage).get("title") or STAGE_TITLES[stage],
                "battles": battles,
                "finished": sum(1 for battle in battles if battle.status == MatchStatus.FINISHED),
                "total": len(battles),
                "url_stage": stage,
            }
        )
    return grouped


def competition_stage_navigation(competition):
    profile = competition_profile_from_instance(competition)
    items = [{"key": CompetitionStage.GROUPS, "title": STAGE_TITLES[CompetitionStage.GROUPS]}]
    for stage in stage_sequence(profile)[1:]:
        items.append({"key": stage, "title": _stage_config(competition, stage).get("title") or STAGE_TITLES[stage]})
    return items


def states_for_stage(competition, stage):
    queryset = TeamCompetitionState.objects.filter(competition=competition).select_related(
        "team__institution",
        "current_group",
        "current_battle",
    )
    if stage == CompetitionStage.GROUPS:
        return list(queryset.filter(current_group__isnull=False).order_by("current_group__order", "team__robot_name"))
    return list(queryset.filter(current_stage=stage).order_by("team__robot_name"))


def participants_for_stage(competition, stage):
    return [participant_row_payload(state) for state in states_for_stage(competition, stage)]


def winners_for_stage(competition, stage):
    winners = []
    for battle in stage_battles(competition, stage):
        if not battle.winner_id:
            continue
        state = TeamCompetitionState.objects.filter(
            competition=competition,
            team_id=battle.winner_id,
        ).select_related("team__institution", "current_group", "current_battle").first()
        if state:
            winners.append(participant_row_payload(state))
    return winners


def build_stage_context(competition, stage):
    navigation = competition_stage_navigation(competition)
    profile = competition_profile_from_instance(competition)
    base_context = {
        "competition": competition,
        "profile": profile,
        "stage_key": stage,
        "stage_title": _stage_config(competition, stage).get("title") or STAGE_TITLES.get(stage, stage),
        "navigation": navigation,
    }

    if stage == CompetitionStage.GROUPS:
        groups = []
        classified = []
        non_classified = []
        for group in competition.groups.prefetch_related("entries__team__institution").order_by("order"):
            payload_entries = []
            for entry in group.entries.order_by("slot_order"):
                state = TeamCompetitionState.objects.filter(competition=competition, team=entry.team).select_related(
                    "team__institution",
                    "current_group",
                    "current_battle",
                ).first()
                participant = participant_row_payload(state) if state else None
                payload_entries.append({"entry": entry, "participant": participant, "state": state})
                if entry.qualified_from_group:
                    classified.append(participant)
                else:
                    non_classified.append(participant)
            groups.append({"group": group, "entries": payload_entries})
        base_context.update(
            {
                "groups_payload": groups,
                "classified_participants": classified,
                "secondary_participants": non_classified,
                "secondary_title": "Pendientes, eliminados o candidatos a repechaje",
            }
        )
        return base_context

    battles_payload = []
    for battle in stage_battles(competition, stage):
        battle_entries = []
        for battle_entry in battle.entries.order_by("slot_order"):
            state = TeamCompetitionState.objects.filter(competition=competition, team=battle_entry.team).select_related(
                "team__institution",
                "current_group",
                "current_battle",
            ).first()
            battle_entries.append(
                {
                    "battle_entry": battle_entry,
                    "state": state,
                    "participant": participant_row_payload(state) if state else None,
                }
            )
        battles_payload.append({"battle": battle, "entries": battle_entries})

    active_states = participants_for_stage(competition, stage)
    eliminated_states = [
        participant_row_payload(state)
        for state in TeamCompetitionState.objects.filter(
            competition=competition,
            current_stage=stage,
            current_status=ParticipantStatus.ELIMINATED,
        ).select_related("team__institution", "current_group", "current_battle")
    ]
    base_context.update(
        {
            "battles_payload": battles_payload,
            "stage_participants": active_states,
            "winner_participants": winners_for_stage(competition, stage),
            "eliminated_participants": eliminated_states,
        }
    )
    return base_context


def participant_modal_payload(state):
    competition = state.competition
    history = list(
        CompetitionHistoryEntry.objects.filter(competition=competition, team=state.team)
        .select_related("previous_group", "new_group", "battle")
        .order_by("-created_at")[:18]
    )
    profile = competition_profile_from_instance(competition)
    stages = [{"value": item["key"], "label": item["title"]} for item in competition_stage_navigation(competition)]
    groups = [{"value": group.id, "label": f"Grupo {group.label}"} for group in competition.groups.order_by("order")]
    battles = [
        {
            "value": battle.id,
            "label": f"{STAGE_TITLES[battle.stage]} · {battle.name}",
            "stage": battle.stage,
        }
        for battle in competition.battles.order_by("stage", "order")
    ]
    return {
        "state_id": state.id,
        "team_id": state.team_id,
        "robot_name": state.team.robot_name,
        "institution_name": state.team.institution.name if state.team.institution_id else "",
        "group_label": state.current_group.label if state.current_group_id else "Sin grupo",
        "phase_label": STAGE_TITLES.get(state.current_stage, state.current_stage),
        "status_label": participant_status_badge(state.current_status),
        "current_stage": state.current_stage,
        "current_status": state.manual_status_override or state.current_status,
        "current_group_id": state.current_group_id,
        "current_battle_id": state.current_battle_id,
        "notes": state.notes,
        "stages": stages,
        "groups": groups,
        "battles": battles,
        "statuses": [
            {"value": "", "label": "Automatico del sistema"},
            *[
                {"value": choice[0], "label": choice[1]}
                for choice in ParticipantStatus.choices
            ],
        ],
        "history": [
            {
                "title": item.title,
                "description": item.description,
                "stage": STAGE_TITLES.get(item.stage, item.stage) if item.stage else "",
                "status": participant_status_badge(item.status) if item.status else "",
                "created_at": item.created_at.strftime("%d/%m/%Y %H:%M"),
            }
            for item in history
        ],
    }


@transaction.atomic
def update_participant_state(
    state,
    *,
    target_stage,
    target_status_override="",
    target_group_id=None,
    target_battle_id=None,
    note="",
):
    competition = state.competition
    team = state.team
    previous_stage = state.current_stage
    previous_status = state.current_status
    previous_group = state.current_group

    group_entry = DivisionGroupEntry.objects.filter(group__competition=competition, team=team).select_related("group").first()

    if target_stage == CompetitionStage.GROUPS:
        if not target_group_id:
            raise ValueError("Para mover un participante a grupos debes escoger un grupo destino.")
        target_group = DivisionGroup.objects.filter(competition=competition, pk=target_group_id).first()
        if target_group is None:
            raise ValueError("El grupo destino no pertenece a esta categoria.")
        _clear_team_from_battles(competition, team)
        if group_entry:
            original_group_id = group_entry.group_id
            stays_in_same_group = original_group_id == target_group.id
            group_entry.group = target_group
            group_entry.qualified_from_group = False
            group_entry.final_rank = None
            if stays_in_same_group:
                group_entry.save(update_fields=["group", "qualified_from_group", "final_rank", "updated_at"])
            else:
                group_entry.slot_order = target_group.entries.count() + 1
                group_entry.save(update_fields=["group", "slot_order", "qualified_from_group", "final_rank", "updated_at"])
        else:
            DivisionGroupEntry.objects.create(
                group=target_group,
                team=team,
                slot_order=target_group.entries.count() + 1,
            )
        _resequence_group_entries(target_group)
        if previous_group and previous_group.id != target_group.id:
            _resequence_group_entries(previous_group)
    else:
        if group_entry:
            old_group = group_entry.group
            group_entry.delete()
            _resequence_group_entries(old_group)
        _clear_team_from_battles(competition, team)
        battle = _pick_battle_for_stage(competition, target_stage, target_battle_id)
        capacity = battle_format_capacity(battle)
        existing_count = battle.entries.count()
        if capacity is not None and existing_count >= capacity:
            raise ValueError("La batalla destino ya esta llena.")
        CompetitionBattleEntry.objects.create(
            battle=battle,
            team=team,
            slot_order=existing_count + 1,
            origin_label="Movimiento manual",
        )

    sync_team_states(competition)
    state = TeamCompetitionState.objects.get(competition=competition, team=team)
    state.manual_status_override = target_status_override
    if note:
        state.notes = note
    state.save(update_fields=["manual_status_override", "notes", "updated_at"])
    sync_team_states(competition)
    state = TeamCompetitionState.objects.get(competition=competition, team=team)

    action_type = HistoryActionType.REINTEGRATED if previous_status == ParticipantStatus.ELIMINATED else HistoryActionType.MANUAL_MOVE
    record_history(
        competition=competition,
        team=team,
        action_type=action_type,
        title="Edicion manual de participante",
        description=note or f"Movido a {STAGE_TITLES.get(target_stage, target_stage)}",
        stage=target_stage,
        status=state.current_status,
        previous_stage=previous_stage,
        new_stage=state.current_stage,
        previous_status=previous_status,
        new_status=state.current_status,
        previous_group=previous_group,
        new_group=state.current_group,
        battle=state.current_battle,
    )
    return state
