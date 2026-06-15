from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.participants.models import SchoolRegistration, UniversityRegistration
from .formats import competition_profile
from .planner import build_division_plan
from .recommendations import next_phase_recommendation
from .models import (
    CompetitionStage,
    DivisionCompetition,
    DivisionType,
    MatchStatus,
    TeamCompetitionState,
    TournamentEdition,
    TournamentPhase,
)
from .services import (
    build_stage_context,
    competition_profile_from_instance,
    competition_stage_navigation,
    initialize_competition,
    ManualCorrectionRequired,
    materialize_manual_duel_stage,
    materialize_recommended_duel_stage,
    materialize_repechage_stage,
    participant_modal_payload,
    reset_competition_state,
    set_battle_winner,
    set_group_qualifiers,
    stage_summary,
    sync_competition,
    update_participant_state,
    update_group_layout,
)


def overview(request):
    edition = TournamentEdition.objects.filter(is_active=True).order_by("-start_date").first()
    phases = TournamentPhase.objects.filter(edition=edition).order_by("order") if edition else []
    return render(request, "tournament/overview.html", {"edition": edition, "phases": phases})


def is_organizer(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def checkbox_to_bool(post_data, field_name):
    return post_data.get(field_name) in {"on", "true", "1", "yes"}


def manual_overrides_from_post(post_data):
    return {
        "mode_source": "manual",
        "group_count": int(post_data.get("group_count", "0")),
        "qualifiers_per_group": int(post_data.get("qualifiers_per_group", "0")),
        "allow_purgatory_one": checkbox_to_bool(post_data, "allow_purgatory_one"),
        "allow_purgatory_two": checkbox_to_bool(post_data, "allow_purgatory_two"),
        "enable_third_place": checkbox_to_bool(post_data, "enable_third_place"),
    }


def modal_payload_error(message, status=400):
    return JsonResponse({"ok": False, "message": message}, status=status)


def wants_json_response(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def manual_override_requested(request):
    return request.POST.get("manual_override") in {"1", "true", "yes", "on"}


def correction_success_message(default_message, result):
    if result.get("manual_correction_applied"):
        return "Corrección aplicada. Revisa las fases posteriores afectadas."
    return default_message


def confirmation_required_response(error):
    return JsonResponse(
        {
            "ok": False,
            "requires_confirmation": True,
            "message": str(error),
        },
        status=409,
    )


def stage_has_visible_activity(competition, stage_key):
    if stage_key == CompetitionStage.GROUPS:
        return competition.groups.exists()
    progressive_created_stages = set((competition.configuration or {}).get("progressive_created_stages", []))
    if stage_key in progressive_created_stages:
        return True
    return (
        competition.battles.filter(stage=stage_key, status__in=[MatchStatus.IN_PROGRESS, MatchStatus.FINISHED])
        .exists()
        or competition.battles.filter(stage=stage_key, winner__isnull=False).exists()
    )


def visible_stage_navigation(competition, current_stage=None):
    visible = []
    for item in competition_stage_navigation(competition):
        stage_key = item["key"]
        if stage_key == CompetitionStage.GROUPS or stage_key == current_stage or stage_has_visible_activity(competition, stage_key):
            visible.append(item)
    return visible


def groups_stage_is_closed(competition):
    profile = competition_profile_from_instance(competition)
    qualifiers_per_group = profile.get("qualifiers_per_group", 0)
    groups = list(competition.groups.prefetch_related("entries"))
    if not groups or qualifiers_per_group < 1:
        return False
    for group in groups:
        entries = list(group.entries.all())
        if len(entries) < qualifiers_per_group:
            return False
        if sum(1 for entry in entries if entry.qualified_from_group) != qualifiers_per_group:
            return False
    return True


def battle_stage_is_closed(competition, stage_key):
    battles = list(competition.battles.filter(stage=stage_key).prefetch_related("entries"))
    active_battles = [battle for battle in battles if battle.entries.exists()]
    if not active_battles:
        return False
    return all(battle.status == MatchStatus.FINISHED and battle.winner_id for battle in active_battles)


def stage_is_closed(competition, stage_key):
    if stage_key == CompetitionStage.GROUPS:
        return groups_stage_is_closed(competition)
    return battle_stage_is_closed(competition, stage_key)


@login_required
@user_passes_test(is_organizer)
def control_dashboard(request):
    edition = TournamentEdition.objects.filter(is_active=True).order_by("-start_date").first()

    if request.method == "POST" and edition:
        action = request.POST.get("action")
        if action == "generate_competition":
            division = request.POST.get("division")
            try:
                competition = initialize_competition(edition, division, preserve_existing_profile=True)
                messages.success(
                    request,
                    f"Se aseguro el tablero base de {competition.get_division_display()} sin borrar progreso existente.",
                )
            except ValueError as error:
                messages.error(request, str(error))
            return redirect("tournament:control_dashboard")

    phases = (
        TournamentPhase.objects.filter(edition=edition)
        .annotate(match_total=Count("matches"))
        .order_by("order")
        if edition
        else []
    )
    school_registrations = (
        SchoolRegistration.objects.filter(edition=edition, status="approved").order_by("robot_name")
        if edition
        else SchoolRegistration.objects.none()
    )
    university_registrations = (
        UniversityRegistration.objects.filter(edition=edition, status="approved").order_by("robot_name")
        if edition
        else UniversityRegistration.objects.none()
    )
    division_plans = (
        [
            build_division_plan(edition, "school", "Colegios", school_registrations, target_slots=50),
            build_division_plan(edition, "university", "Universidades", university_registrations, target_slots=50),
        ]
        if edition
        else []
    )
    competition_lookup = {
        competition.division: competition
        for competition in DivisionCompetition.objects.filter(edition=edition)
    } if edition else {}
    for division in division_plans:
        division["competition"] = competition_lookup.get(division["key"])
        if division["competition"]:
            active_profile = competition_profile_from_instance(division["competition"])
            division["mode_label"] = active_profile["label"]
            division["mode_summary"] = active_profile["summary"]
            division["quick_stats"] = [
                {
                    "label": "Modo",
                    "value": "Manual" if active_profile.get("mode_source") == "manual" else active_profile["label"],
                },
                {"label": "Grupos", "value": str(active_profile["group_count"]) if active_profile["group_count"] else "-"},
                {"label": "Clasifican", "value": str(active_profile["qualifier_count"]) if active_profile["qualifier_count"] else "-"},
                {"label": "P2", "value": "Si" if active_profile["allow_purgatory_two"] else "No"},
                {"label": "Tercer lugar", "value": "Si" if active_profile["enable_third_place"] else "No"},
            ]

    context = {
        "edition": edition,
        "phases": phases,
        "school_total": SchoolRegistration.objects.filter(edition=edition).count() if edition else 0,
        "university_total": UniversityRegistration.objects.filter(edition=edition).count() if edition else 0,
        "phase_total": len(phases) if edition else 0,
        "match_total": sum(phase.match_total for phase in phases) if edition else 0,
        "division_plans": division_plans,
    }
    return render(request, "tournament/control_dashboard.html", context)


@login_required
@user_passes_test(is_organizer)
def control_division(request, competition_id):
    competition = get_object_or_404(
        DivisionCompetition.objects.select_related("edition"),
        pk=competition_id,
    )

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "save_group_qualifiers":
            group = get_object_or_404(competition.groups.prefetch_related("entries__team"), pk=request.POST.get("group_id"))
            try:
                selected_entry_ids = request.POST.getlist("qualified_entry_ids")
                result = set_group_qualifiers(
                    group,
                    selected_entry_ids,
                    manual_override=manual_override_requested(request),
                )
                messages.success(
                    request,
                    correction_success_message(f"Se guardaron los clasificados del Grupo {group.label}.", result),
                )
            except ManualCorrectionRequired as error:
                if wants_json_response(request):
                    return confirmation_required_response(error)
                messages.warning(request, str(error))
            except ValueError as error:
                messages.error(request, str(error))
            return redirect("tournament:control_division", competition_id=competition.id)

        if action == "save_battle_winner":
            battle = get_object_or_404(competition.battles.prefetch_related("entries__team"), pk=request.POST.get("battle_id"))
            try:
                winner_team_id = int(request.POST.get("winner_team_id", "0"))
                result = set_battle_winner(
                    battle,
                    winner_team_id,
                    manual_override=manual_override_requested(request),
                )
                messages.success(
                    request,
                    correction_success_message(f"Se registro el ganador de {battle.name}.", result),
                )
            except ManualCorrectionRequired as error:
                if wants_json_response(request):
                    return confirmation_required_response(error)
                messages.warning(request, str(error))
            except ValueError as error:
                messages.error(request, str(error))
            return redirect("tournament:control_division", competition_id=competition.id)

        if action == "apply_auto_configuration":
            try:
                competition = initialize_competition(competition.edition, competition.division)
                messages.success(
                    request,
                    f"Se aplico el modo sugerido automatico sin borrar progreso existente.",
                )
            except ValueError as error:
                messages.error(request, str(error))
            return redirect("tournament:control_division", competition_id=competition.id)

        if action == "apply_manual_configuration":
            try:
                overrides = manual_overrides_from_post(request.POST)
                competition = initialize_competition(competition.edition, competition.division, overrides=overrides)
                messages.success(
                    request,
                    f"Se aplico una configuracion manual para {competition.get_division_display()}.",
                )
            except ValueError as error:
                messages.error(request, str(error))
            return redirect("tournament:control_division", competition_id=competition.id)

        if action == "save_group_layout":
            try:
                assignments_by_entry_id = {
                    int(key.removeprefix("target_group_")): int(value)
                    for key, value in request.POST.items()
                    if key.startswith("target_group_")
                }
                update_group_layout(competition, assignments_by_entry_id)
                messages.success(request, "Se actualizo la distribucion manual de grupos.")
            except ValueError as error:
                messages.error(request, str(error))
            return redirect("tournament:control_division", competition_id=competition.id)

        if action == "regenerate_competition":
            try:
                competition = initialize_competition(
                    competition.edition,
                    competition.division,
                    preserve_existing_profile=True,
                )
                messages.success(
                    request,
                    f"Se aseguro el tablero de {competition.get_division_display()} manteniendo la configuracion actual.",
                )
            except ValueError as error:
                messages.error(request, str(error))
            return redirect("tournament:control_division", competition_id=competition.id)

        if action == "reset_competition":
            if request.POST.get("confirm_reset") != "yes":
                messages.error(request, "Debes confirmar explicitamente el reinicio destructivo del torneo.")
                return redirect("tournament:control_division", competition_id=competition.id)
            competition = reset_competition_state(competition)
            messages.success(
                request,
                f"Se reinicio el torneo de {competition.get_division_display()} y el flujo volvio a grupos.",
            )
            return redirect("tournament:control_division_stage", competition_id=competition.id, stage_key=CompetitionStage.GROUPS)

    competition = (
        DivisionCompetition.objects.select_related("edition")
        .prefetch_related(
            "groups__entries__team__institution",
            "battles__entries__team__institution",
        )
        .get(pk=competition.id)
    )
    sync_competition(competition)
    groups = competition.groups.all().order_by("order")
    stages = stage_summary(competition)
    profile = competition_profile_from_instance(competition)
    system_recommendation = next_phase_recommendation(competition)
    auto_suggestion = competition_profile(profile.get("team_count", 0))
    navigation = visible_stage_navigation(competition)
    current_stage_key = navigation[-1]["key"] if navigation else CompetitionStage.GROUPS
    recommendation_ready = stage_is_closed(competition, current_stage_key)
    layout_entries = (
        competition.groups.all()
        .prefetch_related("entries__team__institution")
        .order_by("order")
    )
    return render(
        request,
        "tournament/control_division.html",
        {
            "competition": competition,
            "profile": profile,
            "system_recommendation": system_recommendation,
            "recommendation_ready": recommendation_ready,
            "recommendation_stage_key": current_stage_key,
            "auto_suggestion": auto_suggestion,
            "edition": competition.edition,
            "groups": groups,
            "stages": stages,
            "stage_navigation": navigation,
            "layout_groups": competition.groups.all().order_by("order"),
            "layout_entries": [
                entry
                for group in layout_entries
                for entry in group.entries.all()
            ],
        },
    )


@login_required
@user_passes_test(is_organizer)
def control_division_stage(request, competition_id, stage_key):
    competition = get_object_or_404(
        DivisionCompetition.objects.select_related("edition"),
        pk=competition_id,
    )
    valid_stages = {item["key"] for item in competition_stage_navigation(competition)}
    if stage_key not in valid_stages:
        return redirect("tournament:control_division", competition_id=competition.id)
    post_action = request.POST.get("action") if request.method == "POST" else ""
    if post_action not in {"create_recommended_phase", "create_repechage_phase", "create_manual_duel_phase"}:
        sync_competition(competition)

    if request.method == "POST":
        action = post_action
        if action == "save_group_qualifiers" and stage_key == CompetitionStage.GROUPS:
            group = get_object_or_404(competition.groups.prefetch_related("entries__team"), pk=request.POST.get("group_id"))
            try:
                selected_entry_ids = request.POST.getlist("qualified_entry_ids")
                result = set_group_qualifiers(
                    group,
                    selected_entry_ids,
                    manual_override=manual_override_requested(request),
                )
                message = correction_success_message(f"Se guardaron los clasificados del Grupo {group.label}.", result)
                if wants_json_response(request):
                    return JsonResponse({"ok": True, "message": message})
                messages.success(request, message)
            except ManualCorrectionRequired as error:
                if wants_json_response(request):
                    return confirmation_required_response(error)
                messages.warning(request, str(error))
            except ValueError as error:
                message = str(error)
                if wants_json_response(request):
                    return JsonResponse({"ok": False, "message": message}, status=400)
                messages.error(request, message)
            return redirect("tournament:control_division_stage", competition_id=competition.id, stage_key=stage_key)

        if action == "save_battle_winner" and stage_key != CompetitionStage.GROUPS:
            battle = get_object_or_404(competition.battles.prefetch_related("entries__team"), pk=request.POST.get("battle_id"))
            try:
                winner_team_id = int(request.POST.get("winner_team_id", "0"))
                result = set_battle_winner(
                    battle,
                    winner_team_id,
                    manual_override=manual_override_requested(request),
                )
                message = correction_success_message(f"Se registro el ganador de {battle.name}.", result)
                if wants_json_response(request):
                    return JsonResponse({"ok": True, "message": message})
                messages.success(request, message)
            except ManualCorrectionRequired as error:
                if wants_json_response(request):
                    return confirmation_required_response(error)
                messages.warning(request, str(error))
            except ValueError as error:
                message = str(error)
                if wants_json_response(request):
                    return JsonResponse({"ok": False, "message": message}, status=400)
                messages.error(request, message)
            return redirect("tournament:control_division_stage", competition_id=competition.id, stage_key=stage_key)

        if action == "reset_competition":
            if request.POST.get("confirm_reset") != "yes":
                messages.error(request, "Debes confirmar explicitamente el reinicio destructivo del torneo.")
                return redirect("tournament:control_division_stage", competition_id=competition.id, stage_key=stage_key)
            competition = reset_competition_state(competition)
            messages.success(
                request,
                f"Se reinicio el torneo de {competition.get_division_display()} y el flujo volvio a grupos.",
            )
            return redirect("tournament:control_division_stage", competition_id=competition.id, stage_key=CompetitionStage.GROUPS)

        if action == "create_recommended_phase":
            if not stage_is_closed(competition, stage_key):
                messages.error(request, "Completa y guarda todos los resultados antes de pasar a la siguiente fase.")
                return redirect("tournament:control_division_stage", competition_id=competition.id, stage_key=stage_key)
            try:
                result = materialize_recommended_duel_stage(competition)
            except ValueError as error:
                messages.error(request, str(error))
                return redirect("tournament:control_division_stage", competition_id=competition.id, stage_key=stage_key)
            if result.get("existing"):
                messages.info(request, result["message"])
            else:
                messages.success(request, result["message"])
            return redirect(
                "tournament:control_division_stage",
                competition_id=competition.id,
                stage_key=result["stage"],
            )

        if action == "create_repechage_phase":
            if not stage_is_closed(competition, stage_key):
                messages.error(request, "Completa y guarda todos los resultados antes de abrir repechaje.")
                return redirect("tournament:control_division_stage", competition_id=competition.id, stage_key=stage_key)
            try:
                result = materialize_repechage_stage(competition)
            except ValueError as error:
                messages.error(request, str(error))
                return redirect("tournament:control_division_stage", competition_id=competition.id, stage_key=stage_key)
            messages.info(request, result["message"]) if result.get("existing") else messages.success(request, result["message"])
            return redirect(
                "tournament:control_division_stage",
                competition_id=competition.id,
                stage_key=result["stage"],
            )

        if action == "create_manual_duel_phase":
            if not stage_is_closed(competition, stage_key):
                messages.error(request, "Completa y guarda todos los resultados antes de crear una fase manual.")
                return redirect("tournament:control_division_stage", competition_id=competition.id, stage_key=stage_key)
            try:
                participant_count = int(request.POST.get("manual_participant_count", "0"))
                result = materialize_manual_duel_stage(
                    competition,
                    name=request.POST.get("manual_phase_name", ""),
                    participant_count=participant_count,
                )
            except (TypeError, ValueError) as error:
                messages.error(request, str(error))
                return redirect("tournament:control_division_stage", competition_id=competition.id, stage_key=stage_key)
            messages.success(request, result["message"])
            return redirect(
                "tournament:control_division_stage",
                competition_id=competition.id,
                stage_key=result["stage"],
            )

    context = build_stage_context(competition, stage_key)
    context["edition"] = competition.edition
    context["navigation"] = visible_stage_navigation(competition, current_stage=stage_key)
    context["system_recommendation"] = next_phase_recommendation(competition)
    context["recommendation_ready"] = stage_is_closed(competition, stage_key)
    context["recommendation_wait_message"] = "Finaliza esta fase para calcular la recomendacion de avance."
    context["recommendation_stage_key"] = stage_key
    return render(request, "tournament/control_stage.html", context)


@login_required
@user_passes_test(is_organizer)
def participant_modal_detail(request, competition_id, state_id):
    competition = get_object_or_404(DivisionCompetition, pk=competition_id)
    state = get_object_or_404(
        TeamCompetitionState.objects.select_related(
            "competition",
            "team__institution",
            "current_group",
            "current_battle",
        ),
        pk=state_id,
        competition=competition,
    )
    return JsonResponse({"ok": True, "participant": participant_modal_payload(state)})


@login_required
@user_passes_test(is_organizer)
def participant_modal_update(request, competition_id, state_id):
    if request.method != "POST":
        return modal_payload_error("Metodo no permitido.", status=405)

    competition = get_object_or_404(DivisionCompetition, pk=competition_id)
    state = get_object_or_404(
        TeamCompetitionState.objects.select_related(
            "competition",
            "team__institution",
            "current_group",
            "current_battle",
        ),
        pk=state_id,
        competition=competition,
    )

    target_stage = request.POST.get("target_stage") or state.current_stage
    target_status_override = request.POST.get("target_status_override", "")
    target_group_id = request.POST.get("target_group_id") or None
    target_battle_id = request.POST.get("target_battle_id") or None
    note = request.POST.get("note", "").strip()

    try:
        updated_state = update_participant_state(
            state,
            target_stage=target_stage,
            target_status_override=target_status_override,
            target_group_id=target_group_id,
            target_battle_id=target_battle_id,
            note=note,
        )
    except ValueError as error:
        return modal_payload_error(str(error))

    return JsonResponse(
        {
            "ok": True,
            "message": f"Se actualizo {updated_state.team.robot_name}.",
            "participant": participant_modal_payload(updated_state),
        }
    )


@login_required
@user_passes_test(is_organizer)
def control_phase_detail(request, phase_id):
    phase = get_object_or_404(TournamentPhase, pk=phase_id)
    matches = phase.matches.select_related("team_a", "team_b", "winner").order_by("scheduled_at", "id")
    return render(
        request,
        "tournament/control_phase_detail.html",
        {
            "phase": phase,
            "edition": phase.edition,
            "matches": matches,
        },
    )


def seed_demo_phases(edition):
    defaults = [
        ("Clasificatoria general", "qualifiers", 1, False, {"clasifican": 8, "formato": "puntos"}),
        ("Semifinal", "semifinal", 2, False, {"llaves": 2}),
        ("Final", "final", 3, False, {"tercer_puesto": True}),
    ]
    for name, phase_type, order, is_public, configuration in defaults:
        TournamentPhase.objects.get_or_create(
            edition=edition,
            order=order,
            defaults={
                "name": name,
                "phase_type": phase_type,
                "is_public": is_public,
                "configuration": configuration,
            },
        )
