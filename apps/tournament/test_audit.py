from io import StringIO
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.db.models import Count
from django.test import Client
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from apps.participants.models import (
    Institution,
    InstitutionType,
    RegistrationStatus,
    SchoolRegistration,
    Team,
)
from apps.participants.services import confirm_attendance, sync_registration_to_team

from .formats import auto_profile
from .models import (
    CompetitionBattleEntry,
    CompetitionHistoryEntry,
    CompetitionStage,
    DivisionGroupEntry,
    DivisionType,
    ParticipantStatus,
    TeamCompetitionState,
    TournamentEdition,
)
from .recommendations import next_phase_recommendation
from .services import (
    _battle_qualifier_target,
    ManualCorrectionRequired,
    competition_profile_from_instance,
    final_podium_payload,
    initialize_competition,
    materialize_recommended_duel_stage,
    materialize_repechage_stage,
    save_final_podium,
    set_battle_winner,
    set_battle_qualifiers,
    set_group_qualifiers,
)


class TournamentAuditTestCase(TestCase):
    def setUp(self):
        self.edition = TournamentEdition.objects.create(name="AUDIT-EDITION", is_active=True)

    def create_teams(self, count, division=DivisionType.SCHOOL, start=1):
        category_label = "Colegios" if division == DivisionType.SCHOOL else "Universidades"
        institution_type = (
            InstitutionType.SCHOOL if division == DivisionType.SCHOOL else InstitutionType.UNIVERSITY
        )
        teams = []
        for index in range(start, start + count):
            institution = Institution.objects.create(
                name=f"AUDIT-{self.edition.id}-{division}-INSTITUTION-{index}",
                institution_type=institution_type,
            )
            teams.append(
                Team.objects.create(
                    edition=self.edition,
                    name=f"AUDIT-{self.edition.id}-{division}-TEAM-{index}",
                    institution=institution,
                    category_label=category_label,
                    robot_name=f"AUDIT-{self.edition.id}-{division}-ROBOT-{index}",
                    coach_name="Audit Coach",
                    coach_email=f"audit-{division}-{index}@example.test",
                    coach_phone="3000000000",
                    status=RegistrationStatus.APPROVED,
                )
            )
        return teams

    def complete_groups(self, competition):
        qualifier_count = competition.configuration["qualifiers_per_group"]
        for group in competition.groups.prefetch_related("entries").order_by("order"):
            selected = list(group.entries.order_by("slot_order").values_list("id", flat=True)[:qualifier_count])
            set_group_qualifiers(group, selected)

    def create_standard_final(self, competition):
        self.complete_groups(competition)
        semifinal_result = materialize_recommended_duel_stage(competition)
        self.assertEqual(semifinal_result["stage"], CompetitionStage.SEMIFINAL)
        semifinals = list(
            competition.battles.filter(stage=CompetitionStage.SEMIFINAL)
            .prefetch_related("entries")
            .order_by("order")
        )
        for battle in semifinals:
            set_battle_winner(battle, battle.entries.order_by("slot_order").first().team_id)
        final_result = materialize_recommended_duel_stage(competition)
        self.assertEqual(final_result["stage"], CompetitionStage.FINAL)
        return semifinals

    def play_battle_stage(self, competition, stage):
        battles = list(
            competition.battles.filter(stage=stage)
            .prefetch_related("entries")
            .order_by("order")
        )
        self.assertTrue(battles)
        for battle in battles:
            battle = type(battle).objects.select_related("competition").prefetch_related(
                "entries"
            ).get(pk=battle.pk)
            team_ids = list(battle.entries.order_by("slot_order").values_list("team_id", flat=True))
            self.assertGreaterEqual(len(team_ids), 2)
            target = _battle_qualifier_target(battle)
            if target > 1:
                set_battle_qualifiers(battle, team_ids[:target])
            else:
                set_battle_winner(battle, team_ids[0])

    def finish_progressive_tournament(self, competition):
        for _step in range(12):
            final_battle = (
                competition.battles.filter(stage=CompetitionStage.FINAL)
                .prefetch_related("entries")
                .order_by("order")
                .first()
            )
            if final_battle and final_battle.entries.exists():
                finalist_ids = list(
                    final_battle.entries.order_by("slot_order").values_list("team_id", flat=True)
                )
                if len(finalist_ids) >= 3:
                    save_final_podium(
                        competition,
                        champion_team_id=finalist_ids[0],
                        second_team_id=finalist_ids[1],
                        third_team_id=finalist_ids[2],
                    )
                else:
                    third_battle = (
                        competition.battles.filter(stage=CompetitionStage.THIRD_PLACE)
                        .prefetch_related("entries")
                        .order_by("order")
                        .first()
                    )
                    if third_battle and third_battle.entries.exists() and not third_battle.winner_id:
                        third_id = third_battle.entries.order_by("slot_order").first().team_id
                        set_battle_winner(third_battle, third_id)
                    save_final_podium(
                        competition,
                        champion_team_id=finalist_ids[0],
                        second_team_id=finalist_ids[1],
                    )
                competition.refresh_from_db()
                self.assertEqual(competition.status, "completed")
                return final_podium_payload(competition)

            try:
                result = materialize_recommended_duel_stage(competition)
            except ValueError as error:
                active_count = competition.team_states.filter(
                    current_status__in=[ParticipantStatus.ACTIVE, ParticipantStatus.QUALIFIED]
                ).count()
                created = (competition.configuration or {}).get("progressive_created_stages", [])
                self.fail(
                    f"No se pudo materializar la fase: {error}; "
                    f"activos={active_count}; fases_creadas={created}"
                )
            if result["stage"] != CompetitionStage.FINAL:
                self.play_battle_stage(competition, result["stage"])
        self.fail("El torneo no alcanzo el podio dentro del limite de fases seguro.")

    def assert_competition_integrity(self, competition):
        duplicated_stage_teams = (
            CompetitionBattleEntry.objects.filter(battle__competition=competition)
            .values("battle__stage", "team_id")
            .annotate(total=Count("battle_id", distinct=True))
            .filter(total__gt=1)
        )
        self.assertFalse(duplicated_stage_teams.exists())
        for battle in competition.battles.filter(winner__isnull=False).prefetch_related("entries"):
            self.assertIn(battle.winner_id, set(battle.entries.values_list("team_id", flat=True)))
        payload = final_podium_payload(competition)
        podium_ids = [
            payload["champion_team_id"],
            payload["second_team_id"],
            payload["third_team_id"],
        ]
        self.assertNotIn(None, podium_ids)
        self.assertEqual(len(podium_ids), len(set(podium_ids)))

    def initialize_legacy_competition(self, count, division=DivisionType.UNIVERSITY, overrides=None):
        self.create_teams(count, division)
        competition = initialize_competition(
            self.edition,
            division,
            overrides=overrides,
        )
        configuration = {**competition.configuration, "progressive_flow": False}
        competition.configuration = configuration
        competition.save(update_fields=["configuration", "updated_at"])
        return initialize_competition(
            self.edition,
            division,
            overrides=overrides,
            preserve_existing_profile=overrides is None,
        )

    def finish_legacy_tournament(self, competition):
        self.complete_groups(competition)
        for stage in [
            CompetitionStage.PURGATORY_1,
            CompetitionStage.ROUND_OF_32,
            CompetitionStage.ROUND_OF_16,
            CompetitionStage.PURGATORY_2,
            CompetitionStage.QUARTERFINAL,
            CompetitionStage.SEMIFINAL,
        ]:
            if competition.battles.filter(stage=stage, entries__isnull=False).exists():
                self.play_battle_stage(competition, stage)
        third_battle = (
            competition.battles.filter(stage=CompetitionStage.THIRD_PLACE)
            .prefetch_related("entries")
            .first()
        )
        if third_battle and third_battle.entries.exists():
            set_battle_winner(
                third_battle,
                third_battle.entries.order_by("slot_order").first().team_id,
            )
        final_battle = (
            competition.battles.filter(stage=CompetitionStage.FINAL)
            .prefetch_related("entries")
            .first()
        )
        self.assertIsNotNone(final_battle)
        self.assertEqual(final_battle.entries.count(), 2)
        set_battle_winner(
            final_battle,
            final_battle.entries.order_by("slot_order").first().team_id,
        )
        competition.refresh_from_db()
        self.assertEqual(competition.status, "completed")
        self.assert_competition_integrity(competition)


class GroupMatrixTests(TournamentAuditTestCase):
    def test_automatic_group_matrix_is_balanced_and_complete(self):
        compatible_counts = [4, 5, 6, 7, 8, 9, 10, 12, 16, 17, 24, 31, 32, 33, 40, 73]
        for division in [DivisionType.SCHOOL, DivisionType.UNIVERSITY]:
            for count in compatible_counts:
                with self.subTest(division=division, count=count):
                    edition = TournamentEdition.objects.create(
                        name=f"AUDIT-MATRIX-{division}-{count}"
                    )
                    self.edition = edition
                    teams = self.create_teams(count, division)
                    competition = initialize_competition(edition, division)
                    assigned_ids = list(
                        competition.groups.values_list("entries__team_id", flat=True).order_by("entries__team_id")
                    )
                    sizes = [group.entries.count() for group in competition.groups.order_by("order")]
                    self.assertEqual(len(assigned_ids), count)
                    self.assertEqual(len(set(assigned_ids)), count)
                    self.assertEqual(set(assigned_ids), {team.id for team in teams})
                    self.assertLessEqual(max(sizes) - min(sizes), 1)
                    self.assertNotIn(0, sizes)
                    if count >= 4:
                        self.assertNotIn(1, sizes)

    def test_counts_below_four_remain_explicitly_pending(self):
        for division in [DivisionType.SCHOOL, DivisionType.UNIVERSITY]:
            for count in [2, 3]:
                with self.subTest(division=division, count=count):
                    profile = auto_profile(count)
                    self.assertEqual(profile["key"], "minimum_pending")
                    self.assertEqual(profile["group_count"], 0)
                    self.assertEqual(profile["stages"], [])

    def test_school_and_university_competitions_never_mix(self):
        school_teams = self.create_teams(9, DivisionType.SCHOOL)
        university_teams = self.create_teams(10, DivisionType.UNIVERSITY, start=100)
        school = initialize_competition(self.edition, DivisionType.SCHOOL)
        university = initialize_competition(self.edition, DivisionType.UNIVERSITY)
        school_ids = set(school.groups.values_list("entries__team_id", flat=True))
        university_ids = set(university.groups.values_list("entries__team_id", flat=True))
        self.assertEqual(school_ids, {team.id for team in school_teams})
        self.assertEqual(university_ids, {team.id for team in university_teams})
        self.assertFalse(school_ids & university_ids)


class ProgressSafetyTests(TournamentAuditTestCase):
    def test_reinitialization_preserves_existing_group_results(self):
        self.create_teams(8)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        group = competition.groups.order_by("order").first()
        selected_ids = list(group.entries.order_by("slot_order").values_list("id", flat=True)[:2])
        set_group_qualifiers(group, selected_ids)
        original_entry_ids = set(
            competition.groups.values_list("entries__id", flat=True)
        )

        refreshed = initialize_competition(
            self.edition,
            DivisionType.SCHOOL,
            preserve_existing_profile=True,
        )

        self.assertEqual(
            set(refreshed.groups.values_list("entries__id", flat=True)),
            original_entry_ids,
        )
        self.assertEqual(
            set(
                DivisionGroupEntry.objects.filter(
                    group__competition=refreshed,
                    group_id=group.pk,
                    qualified_from_group=True,
                ).values_list("id", flat=True)
            ),
            set(selected_ids),
        )

    def test_new_approved_team_is_not_silently_excluded_after_progress(self):
        self.create_teams(4)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        group = competition.groups.order_by("order").first()
        selected_ids = list(group.entries.order_by("slot_order").values_list("id", flat=True)[:2])
        set_group_qualifiers(group, selected_ids)
        self.create_teams(1, start=100)

        with self.assertRaisesRegex(ValueError, "equipos aprobados"):
            initialize_competition(
                self.edition,
                DivisionType.SCHOOL,
                preserve_existing_profile=True,
            )

    def test_late_semifinal_correction_replaces_stale_finalist(self):
        self.create_teams(4)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        semifinals = self.create_standard_final(competition)
        corrected_battle = semifinals[0]
        corrected_battle.refresh_from_db()
        old_winner_id = corrected_battle.winner_id
        new_winner_id = (
            corrected_battle.entries.exclude(team_id=old_winner_id).values_list("team_id", flat=True).get()
        )

        with self.assertRaises(ManualCorrectionRequired):
            set_battle_winner(corrected_battle, new_winner_id)
        result = set_battle_winner(corrected_battle, new_winner_id, manual_override=True)

        final_team_ids = set(
            competition.battles.filter(stage=CompetitionStage.FINAL)
            .values_list("entries__team_id", flat=True)
        )
        self.assertTrue(result["manual_correction_applied"])
        self.assertIn(new_winner_id, final_team_ids)
        self.assertNotIn(old_winner_id, final_team_ids)

    def test_late_group_correction_replaces_stale_semifinalist(self):
        self.create_teams(8)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        materialize_recommended_duel_stage(competition)
        group = competition.groups.prefetch_related("entries").order_by("order").first()
        qualified = list(group.entries.filter(qualified_from_group=True).order_by("slot_order"))
        replacement = group.entries.filter(qualified_from_group=False).order_by("slot_order").first()
        old_qualifier = qualified[0]
        corrected_ids = [qualified[1].id, replacement.id]

        with self.assertRaises(ManualCorrectionRequired):
            set_group_qualifiers(group, corrected_ids)
        set_group_qualifiers(group, corrected_ids, manual_override=True)

        semifinal_ids = set(
            competition.battles.filter(stage=CompetitionStage.SEMIFINAL)
            .values_list("entries__team_id", flat=True)
        )
        self.assertIn(replacement.team_id, semifinal_ids)
        self.assertNotIn(old_qualifier.team_id, semifinal_ids)

    def test_late_multi_qualifier_correction_replaces_stale_semifinalist(self):
        self.create_teams(16)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        group_round = materialize_recommended_duel_stage(competition)
        self.play_battle_stage(competition, group_round["stage"])
        materialize_recommended_duel_stage(competition)
        battle = (
            competition.battles.filter(stage=group_round["stage"])
            .prefetch_related("entries")
            .order_by("order")
            .first()
        )
        competition.refresh_from_db()
        selected_ids = list(
            (competition.configuration or {})["battle_qualifiers"][str(battle.id)]
        )
        replacement_id = (
            battle.entries.exclude(team_id__in=selected_ids)
            .order_by("slot_order")
            .values_list("team_id", flat=True)
            .first()
        )
        corrected_ids = [selected_ids[1], replacement_id]

        with self.assertRaises(ManualCorrectionRequired):
            set_battle_qualifiers(battle, corrected_ids)
        set_battle_qualifiers(battle, corrected_ids, manual_override=True)

        semifinal_ids = set(
            competition.battles.filter(stage=CompetitionStage.SEMIFINAL)
            .values_list("entries__team_id", flat=True)
        )
        self.assertIn(replacement_id, semifinal_ids)
        self.assertNotIn(selected_ids[0], semifinal_ids)

    def test_semifinal_correction_invalidates_saved_podium_and_downstream_results(self):
        self.create_teams(4)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        semifinals = self.create_standard_final(competition)
        final_battle = competition.battles.get(stage=CompetitionStage.FINAL)
        third_battle = competition.battles.get(stage=CompetitionStage.THIRD_PLACE)
        final_ids = list(final_battle.entries.order_by("slot_order").values_list("team_id", flat=True))
        third_id = third_battle.entries.order_by("slot_order").values_list("team_id", flat=True).first()
        set_battle_winner(final_battle, final_ids[0])
        set_battle_winner(third_battle, third_id)
        save_final_podium(
            competition,
            champion_team_id=final_ids[0],
            second_team_id=final_ids[1],
        )

        corrected_battle = semifinals[0]
        corrected_battle.refresh_from_db()
        replacement_id = (
            corrected_battle.entries.exclude(team_id=corrected_battle.winner_id)
            .values_list("team_id", flat=True)
            .get()
        )
        set_battle_winner(corrected_battle, replacement_id, manual_override=True)

        competition.refresh_from_db()
        final_battle.refresh_from_db()
        third_battle.refresh_from_db()
        self.assertNotIn("final_podium", competition.configuration)
        self.assertNotEqual(competition.status, "completed")
        self.assertEqual(final_battle.status, "pending")
        self.assertIsNone(final_battle.winner_id)
        self.assertEqual(third_battle.status, "pending")
        self.assertIsNone(third_battle.winner_id)

    def test_deep_group_correction_preserves_unaffected_semifinal_result(self):
        self.create_teams(8)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        materialize_recommended_duel_stage(competition)
        semifinals = list(
            competition.battles.filter(stage=CompetitionStage.SEMIFINAL)
            .prefetch_related("entries")
            .order_by("order")
        )
        for battle in semifinals:
            set_battle_winner(
                battle,
                battle.entries.order_by("slot_order").first().team_id,
            )
        materialize_recommended_duel_stage(competition)
        group = competition.groups.prefetch_related("entries").order_by("order").first()
        qualified = list(group.entries.filter(qualified_from_group=True).order_by("slot_order"))
        replacement = group.entries.filter(qualified_from_group=False).order_by("slot_order").first()
        old_qualifier = qualified[0]
        affected_semifinal = next(
            battle
            for battle in semifinals
            if battle.entries.filter(team_id=old_qualifier.team_id).exists()
        )
        unaffected_semifinal = next(
            battle for battle in semifinals if battle.id != affected_semifinal.id
        )
        affected_semifinal.refresh_from_db()
        unaffected_semifinal.refresh_from_db()
        unaffected_winner_id = unaffected_semifinal.winner_id

        set_group_qualifiers(
            group,
            [qualified[1].id, replacement.id],
            manual_override=True,
        )

        affected_semifinal.refresh_from_db()
        unaffected_semifinal.refresh_from_db()
        self.assertEqual(affected_semifinal.status, "pending")
        self.assertIsNone(affected_semifinal.winner_id)
        self.assertIn(
            replacement.team_id,
            set(affected_semifinal.entries.values_list("team_id", flat=True)),
        )
        self.assertEqual(unaffected_semifinal.status, "finished")
        self.assertEqual(unaffected_semifinal.winner_id, unaffected_winner_id)
        self.assertFalse(
            competition.battles.filter(
                stage__in=[CompetitionStage.FINAL, CompetitionStage.THIRD_PLACE],
                entries__isnull=False,
            ).exists()
        )
        set_battle_winner(
            affected_semifinal,
            affected_semifinal.entries.order_by("slot_order").first().team_id,
        )
        rebuilt = materialize_recommended_duel_stage(competition)
        self.assertEqual(rebuilt["stage"], CompetitionStage.FINAL)
        final_battle = competition.battles.get(stage=CompetitionStage.FINAL)
        third_battle = competition.battles.get(stage=CompetitionStage.THIRD_PLACE)
        set_battle_winner(
            third_battle,
            third_battle.entries.order_by("slot_order").first().team_id,
        )
        final_ids = list(
            final_battle.entries.order_by("slot_order").values_list("team_id", flat=True)
        )
        save_final_podium(
            competition,
            champion_team_id=final_ids[0],
            second_team_id=final_ids[1],
        )
        self.assert_competition_integrity(competition)

    def test_repeated_winner_request_is_idempotent(self):
        self.create_teams(4)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        materialize_recommended_duel_stage(competition)
        battle = (
            competition.battles.filter(stage=CompetitionStage.SEMIFINAL)
            .prefetch_related("entries")
            .order_by("order")
            .first()
        )
        winner_id = battle.entries.order_by("slot_order").first().team_id
        set_battle_winner(battle, winner_id)
        history_count = CompetitionHistoryEntry.objects.filter(competition=competition).count()

        set_battle_winner(battle, winner_id)

        self.assertEqual(
            CompetitionHistoryEntry.objects.filter(competition=competition).count(),
            history_count,
        )

    def test_repeated_group_and_multi_qualifier_requests_are_idempotent(self):
        self.create_teams(16)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        group = competition.groups.prefetch_related("entries").order_by("order").first()
        group_ids = list(group.entries.order_by("slot_order").values_list("id", flat=True)[:2])
        set_group_qualifiers(group, group_ids)
        group_history_count = CompetitionHistoryEntry.objects.filter(
            competition=competition
        ).count()
        set_group_qualifiers(group, group_ids)
        self.assertEqual(
            CompetitionHistoryEntry.objects.filter(competition=competition).count(),
            group_history_count,
        )

        self.complete_groups(competition)
        group_round = materialize_recommended_duel_stage(competition)
        battle = (
            competition.battles.filter(stage=group_round["stage"])
            .prefetch_related("entries")
            .order_by("order")
            .first()
        )
        battle = type(battle).objects.select_related("competition").prefetch_related(
            "entries"
        ).get(pk=battle.pk)
        target = _battle_qualifier_target(battle)
        selected_ids = list(
            battle.entries.order_by("slot_order").values_list("team_id", flat=True)[:target]
        )
        set_battle_qualifiers(battle, selected_ids)
        battle_history_count = CompetitionHistoryEntry.objects.filter(
            competition=competition
        ).count()
        set_battle_qualifiers(battle, selected_ids)
        self.assertEqual(
            CompetitionHistoryEntry.objects.filter(competition=competition).count(),
            battle_history_count,
        )


class PodiumTests(TournamentAuditTestCase):
    def test_standard_podium_waits_for_third_place_and_contains_three_unique_teams(self):
        self.create_teams(4)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.create_standard_final(competition)
        final_battle = (
            competition.battles.filter(stage=CompetitionStage.FINAL)
            .prefetch_related("entries")
            .get()
        )
        third_battle = (
            competition.battles.filter(stage=CompetitionStage.THIRD_PLACE)
            .prefetch_related("entries")
            .get()
        )

        set_battle_winner(final_battle, final_battle.entries.order_by("slot_order").first().team_id)
        competition.refresh_from_db()
        self.assertNotEqual(competition.status, "completed")

        set_battle_winner(third_battle, third_battle.entries.order_by("slot_order").first().team_id)
        competition.refresh_from_db()
        payload = final_podium_payload(competition)
        podium_ids = [
            payload["champion_team_id"],
            payload["second_team_id"],
            payload["third_team_id"],
        ]
        self.assertEqual(competition.status, "completed")
        self.assertNotIn(None, podium_ids)
        self.assertEqual(len(set(podium_ids)), 3)


class RegistrationSyncSafetyTests(TournamentAuditTestCase):
    def test_shared_institution_name_cannot_change_category_silently(self):
        Institution.objects.create(
            name="AUDIT-SHARED-INSTITUTION",
            institution_type=InstitutionType.UNIVERSITY,
        )
        registration = SchoolRegistration.objects.create(
            edition=self.edition,
            institution_name="AUDIT-SHARED-INSTITUTION",
            responsible_name="Audit",
            robot_name="AUDIT-SCHOOL-ROBOT",
            contact_phone="3000000000",
            contact_email="audit-school@example.test",
            status=RegistrationStatus.APPROVED,
        )

        with self.assertRaisesRegex(ValueError, "categoria"):
            sync_registration_to_team(registration, InstitutionType.SCHOOL)


    def test_same_robot_name_in_other_institution_does_not_bypass_progress_guard(self):
        teams = self.create_teams(4)
        conflicting_team = teams[0]
        conflicting_team.name = "AUDIT-LATE-ROBOT"
        conflicting_team.robot_name = "AUDIT-LATE-ROBOT"
        conflicting_team.save(update_fields=["name", "robot_name", "updated_at"])
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        registration = SchoolRegistration.objects.create(
            edition=self.edition,
            institution_name="AUDIT-LATE-INSTITUTION",
            responsible_name="Audit Late",
            robot_name="AUDIT-LATE-ROBOT",
            contact_phone="3000000000",
            contact_email="audit-late@example.test",
            status=RegistrationStatus.SUBMITTED,
        )

        with self.assertRaisesRegex(ValueError, "progreso"):
            sync_registration_to_team(registration, InstitutionType.SCHOOL)

        self.assertFalse(Institution.objects.filter(name="AUDIT-LATE-INSTITUTION").exists())
        self.assertEqual(Team.objects.filter(edition=self.edition, name="AUDIT-LATE-ROBOT").count(), 1)

    def test_existing_bracket_team_can_be_resynchronized_after_progress(self):
        team = self.create_teams(4)[0]
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        registration = SchoolRegistration.objects.create(
            edition=self.edition,
            institution_name=team.institution.name,
            responsible_name="Audit Updated",
            robot_name=team.name,
            contact_phone="3000000000",
            contact_email="audit-updated@example.test",
            status=RegistrationStatus.APPROVED,
        )

        synchronized_team = sync_registration_to_team(registration, InstitutionType.SCHOOL)

        self.assertEqual(synchronized_team.pk, team.pk)
        self.assertEqual(Team.objects.filter(edition=self.edition, name=team.name).count(), 1)

    def test_failed_confirmation_rolls_back_registration(self):
        self.create_teams(4)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        registration = SchoolRegistration.objects.create(
            edition=self.edition,
            institution_name="AUDIT-ROLLBACK-INSTITUTION",
            responsible_name="Audit Rollback",
            robot_name="AUDIT-ROLLBACK-ROBOT",
            contact_phone="3000000000",
            contact_email="audit-rollback@example.test",
            status=RegistrationStatus.SUBMITTED,
        )

        with self.assertRaisesRegex(ValueError, "progreso"):
            confirm_attendance(registration, "colegio", InstitutionType.SCHOOL)

        registration.refresh_from_db()
        self.assertIsNone(registration.attendance_confirmed_at)
        self.assertIsNone(registration.team_synced_at)
        self.assertEqual(registration.status, RegistrationStatus.SUBMITTED)
        self.assertFalse(Team.objects.filter(edition=self.edition, name="AUDIT-ROLLBACK-ROBOT").exists())


class DestructiveCommandSafetyTests(TournamentAuditTestCase):
    def test_audit_settings_keep_demo_reset_disabled_by_default(self):
        self.assertFalse(getattr(settings, "ALLOW_DESTRUCTIVE_DEMO_RESET", False))

    def test_demo_reset_rejects_non_temporary_database_even_when_confirmed(self):
        unsafe_name = settings.BASE_DIR / "db.sqlite3"
        with patch.dict(connection.settings_dict, {"NAME": unsafe_name}):
            with override_settings(ALLOW_DESTRUCTIVE_DEMO_RESET=True):
                with self.assertRaisesRegex(CommandError, "directorio temporal"):
                    call_command(
                        "reset_tournament_demo",
                        school_count=4,
                        university_count=4,
                        confirm_demo_reset=True,
                        stdout=StringIO(),
                    )

        self.assertTrue(TournamentEdition.objects.filter(pk=self.edition.pk).exists())

    def test_demo_reset_is_disabled_without_isolated_environment_setting(self):
        with override_settings(ALLOW_DESTRUCTIVE_DEMO_RESET=False):
            with self.assertRaisesRegex(CommandError, "deshabilitado"):
                call_command(
                    "reset_tournament_demo",
                    school_count=4,
                    university_count=4,
                    confirm_demo_reset=True,
                    stdout=StringIO(),
                )

    def test_demo_reset_requires_explicit_cli_confirmation(self):
        with override_settings(ALLOW_DESTRUCTIVE_DEMO_RESET=True):
            with self.assertRaisesRegex(CommandError, "confirm-demo-reset"):
                call_command(
                    "reset_tournament_demo",
                    school_count=4,
                    university_count=4,
                    stdout=StringIO(),
                )

    def test_demo_reset_remains_available_in_confirmed_isolated_database(self):
        with override_settings(ALLOW_DESTRUCTIVE_DEMO_RESET=True):
            call_command(
                "reset_tournament_demo",
                school_count=4,
                university_count=4,
                confirm_demo_reset=True,
                stdout=StringIO(),
            )
        self.assertEqual(Team.objects.count(), 8)
        self.assertEqual(TournamentEdition.objects.filter(is_active=True).count(), 1)


class IntegralTournamentSimulationTests(TournamentAuditTestCase):
    def test_complete_odd_school_tournament_without_repechage(self):
        self.create_teams(5, DivisionType.SCHOOL)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        self.finish_progressive_tournament(competition)
        competition = type(competition).objects.get(pk=competition.pk)
        self.assertEqual(competition.status, "completed")
        self.assert_competition_integrity(competition)

    def test_complete_university_tournament_with_exact_initial_bracket(self):
        self.create_teams(16, DivisionType.UNIVERSITY)
        competition = initialize_competition(self.edition, DivisionType.UNIVERSITY)
        self.complete_groups(competition)
        self.finish_progressive_tournament(competition)
        self.assert_competition_integrity(competition)

    def test_complete_legacy_university_tournament_without_repechage(self):
        competition = self.initialize_legacy_competition(16)
        self.assertFalse(competition.configuration["progressive_flow"])
        self.finish_legacy_tournament(competition)

    def test_complete_legacy_university_tournament_with_one_repechage(self):
        competition = self.initialize_legacy_competition(40)
        profile = competition_profile_from_instance(competition)
        self.assertTrue(profile["allow_purgatory_one"])
        self.assertFalse(profile["allow_purgatory_two"])
        self.finish_legacy_tournament(competition)

    def test_complete_legacy_university_tournament_with_two_repechages(self):
        overrides = {
            "mode_source": "manual",
            "group_count": 8,
            "qualifiers_per_group": 2,
            "allow_purgatory_one": True,
            "allow_purgatory_two": True,
            "enable_third_place": True,
        }
        competition = self.initialize_legacy_competition(40, overrides=overrides)
        profile = competition_profile_from_instance(competition)
        self.assertTrue(profile["allow_purgatory_one"])
        self.assertTrue(profile["allow_purgatory_two"])
        self.finish_legacy_tournament(competition)


class TournamentAjaxSafetyTests(TournamentAuditTestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            username="audit-organizer",
            password="audit-password",
            is_staff=True,
        )
        self.client.force_login(self.user)

    def stage_url(self, competition, stage):
        return reverse(
            "tournament:control_division_stage",
            args=[competition.id, stage],
        )

    def test_empty_group_payload_returns_structured_json_error(self):
        self.create_teams(4)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        group = competition.groups.order_by("order").first()

        response = self.client.post(
            self.stage_url(competition, CompetitionStage.GROUPS),
            {"action": "save_group_qualifiers", "group_id": group.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertFalse(response.json()["ok"])

    def test_cross_competition_group_payload_returns_json_error(self):
        self.create_teams(4, DivisionType.SCHOOL)
        self.create_teams(4, DivisionType.UNIVERSITY, start=100)
        school = initialize_competition(self.edition, DivisionType.SCHOOL)
        university = initialize_competition(self.edition, DivisionType.UNIVERSITY)
        foreign_group = university.groups.order_by("order").first()

        response = self.client.post(
            self.stage_url(school, CompetitionStage.GROUPS),
            {"action": "save_group_qualifiers", "group_id": foreign_group.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertFalse(response.json()["ok"])

    def test_cross_stage_winner_payload_returns_json_error(self):
        self.create_teams(4)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        semifinals = self.create_standard_final(competition)
        battle = semifinals[0]
        battle.refresh_from_db()
        original_winner_id = battle.winner_id

        response = self.client.post(
            self.stage_url(competition, CompetitionStage.FINAL),
            {
                "action": "save_battle_winner",
                "battle_id": battle.id,
                "winner_team_id": original_winner_id,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])
        battle.refresh_from_db()
        self.assertEqual(battle.winner_id, original_winner_id)

    def test_cross_stage_multi_qualifier_payload_returns_json_error(self):
        self.create_teams(16)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        group_round = materialize_recommended_duel_stage(competition)
        self.play_battle_stage(competition, group_round["stage"])
        next_round = materialize_recommended_duel_stage(competition)
        battle = (
            competition.battles.filter(stage=group_round["stage"])
            .prefetch_related("entries")
            .order_by("order")
            .first()
        )
        competition.refresh_from_db()
        selected_ids = list(
            (competition.configuration or {})["battle_qualifiers"][str(battle.id)]
        )

        response = self.client.post(
            self.stage_url(competition, next_round["stage"]),
            {
                "action": "save_battle_qualifiers",
                "battle_id": battle.id,
                "qualified_team_ids": selected_ids,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])
        competition.refresh_from_db()
        self.assertEqual(
            list((competition.configuration or {})["battle_qualifiers"][str(battle.id)]),
            selected_ids,
        )

    def test_completed_tournament_rejects_phase_creation_posts(self):
        self.create_teams(8)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        self.finish_progressive_tournament(competition)
        competition.refresh_from_db()
        self.assertEqual(competition.status, "completed")
        snapshot = {
            "configuration": dict(competition.configuration or {}),
            "battles": competition.battles.count(),
            "entries": CompetitionBattleEntry.objects.filter(battle__competition=competition).count(),
            "history": CompetitionHistoryEntry.objects.filter(competition=competition).count(),
        }
        blocked_actions = [
            "create_recommended_phase",
            "create_repechage_phase",
            "create_manual_duel_phase",
            "generate_manual_phase_proposal",
            "confirm_manual_phase_proposal",
        ]

        for action in blocked_actions:
            with self.subTest(action=action):
                response = self.client.post(
                    self.stage_url(competition, CompetitionStage.FINAL),
                    {"action": action},
                    HTTP_X_REQUESTED_WITH="XMLHttpRequest",
                )
                self.assertEqual(response.status_code, 409)
                self.assertFalse(response.json()["ok"])

        html_response = self.client.post(
            self.stage_url(competition, CompetitionStage.FINAL),
            {"action": "create_recommended_phase"},
        )
        self.assertEqual(html_response.status_code, 302)
        competition.refresh_from_db()
        self.assertEqual(competition.status, "completed")
        self.assertEqual(competition.configuration, snapshot["configuration"])
        self.assertEqual(competition.battles.count(), snapshot["battles"])
        self.assertEqual(
            CompetitionBattleEntry.objects.filter(battle__competition=competition).count(),
            snapshot["entries"],
        )
        self.assertEqual(
            CompetitionHistoryEntry.objects.filter(competition=competition).count(),
            snapshot["history"],
        )

    def test_ajax_manual_correction_uses_409_confirmation_contract(self):
        self.create_teams(4)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        semifinals = self.create_standard_final(competition)
        battle = semifinals[0]
        battle.refresh_from_db()
        old_winner_id = battle.winner_id
        new_winner_id = battle.entries.exclude(team_id=old_winner_id).values_list("team_id", flat=True).get()
        url = self.stage_url(competition, CompetitionStage.SEMIFINAL)

        response = self.client.post(
            url,
            {
                "action": "save_battle_winner",
                "battle_id": battle.id,
                "winner_team_id": new_winner_id,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 409)
        self.assertTrue(response.json()["requires_confirmation"])

        response = self.client.post(
            url,
            {
                "action": "save_battle_winner",
                "battle_id": battle.id,
                "winner_team_id": new_winner_id,
                "manual_override": "1",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        final_ids = set(
            competition.battles.filter(stage=CompetitionStage.FINAL)
            .values_list("entries__team_id", flat=True)
        )
        self.assertIn(new_winner_id, final_ids)
        self.assertNotIn(old_winner_id, final_ids)

    def test_stale_second_tab_cannot_overwrite_saved_winner_without_confirmation(self):
        self.create_teams(4)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        materialize_recommended_duel_stage(competition)
        battle = (
            competition.battles.filter(stage=CompetitionStage.SEMIFINAL)
            .prefetch_related("entries")
            .order_by("order")
            .first()
        )
        team_ids = list(
            battle.entries.order_by("slot_order").values_list("team_id", flat=True)
        )
        url = self.stage_url(competition, CompetitionStage.SEMIFINAL)
        first = self.client.post(
            url,
            {
                "action": "save_battle_winner",
                "battle_id": battle.id,
                "winner_team_id": team_ids[0],
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        stale = self.client.post(
            url,
            {
                "action": "save_battle_winner",
                "battle_id": battle.id,
                "winner_team_id": team_ids[1],
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(stale.status_code, 409)
        battle.refresh_from_db()
        self.assertEqual(battle.winner_id, team_ids[0])

    def test_csrf_is_required_for_result_posts(self):
        self.create_teams(4)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        group = competition.groups.order_by("order").first()
        strict_client = Client(enforce_csrf_checks=True)
        strict_client.force_login(self.user)

        response = strict_client.post(
            self.stage_url(competition, CompetitionStage.GROUPS),
            {"action": "save_group_qualifiers", "group_id": group.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 403)

    def test_removed_manual_move_route_is_not_accessible(self):
        self.create_teams(4)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        state = competition.team_states.first()

        response = self.client.post(
            f"/torneo/control/divisiones/{competition.id}/participantes/{state.id}/actualizar/",
            {"target_stage": CompetitionStage.FINAL},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 404)


class IntegralTournamentSimulationExtendedTests(TournamentAuditTestCase):
    def test_both_categories_complete_independently(self):
        school_teams = self.create_teams(9, DivisionType.SCHOOL)
        university_teams = self.create_teams(10, DivisionType.UNIVERSITY, start=100)
        school = initialize_competition(self.edition, DivisionType.SCHOOL)
        university = initialize_competition(self.edition, DivisionType.UNIVERSITY)
        self.complete_groups(school)
        self.complete_groups(university)
        self.finish_progressive_tournament(school)
        self.finish_progressive_tournament(university)
        self.assert_competition_integrity(school)
        self.assert_competition_integrity(university)
        self.assertEqual(
            set(school.groups.values_list("entries__team_id", flat=True)),
            {team.id for team in school_teams},
        )
        self.assertEqual(
            set(university.groups.values_list("entries__team_id", flat=True)),
            {team.id for team in university_teams},
        )

    def test_excess_counts_17_and_33_reach_a_valid_podium(self):
        for count in [17, 33]:
            with self.subTest(count=count):
                edition = TournamentEdition.objects.create(name=f"AUDIT-EXCESS-{count}")
                self.edition = edition
                self.create_teams(count)
                competition = initialize_competition(edition, DivisionType.SCHOOL)
                self.complete_groups(competition)
                self.finish_progressive_tournament(competition)
                self.assert_competition_integrity(competition)

    def test_one_repechage_completes_without_duplicates(self):
        self.create_teams(40)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        repechage = materialize_repechage_stage(competition)
        self.play_battle_stage(competition, repechage["stage"])
        self.finish_progressive_tournament(competition)
        self.assert_competition_integrity(competition)

    def test_two_repechages_complete_without_duplicates(self):
        self.create_teams(40)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        first = materialize_repechage_stage(competition)
        first_team_ids = set(
            competition.battles.filter(stage=first["stage"])
            .values_list("entries__team_id", flat=True)
        )
        self.play_battle_stage(competition, first["stage"])
        normal_round = materialize_recommended_duel_stage(competition)
        self.play_battle_stage(competition, normal_round["stage"])
        second = materialize_repechage_stage(competition)
        self.assertNotEqual(first["stage"], second["stage"])
        second_team_ids = set(
            competition.battles.filter(stage=second["stage"])
            .values_list("entries__team_id", flat=True)
        )
        self.assertTrue(first_team_ids.isdisjoint(second_team_ids))
        self.play_battle_stage(competition, second["stage"])
        self.finish_progressive_tournament(competition)
        self.assert_competition_integrity(competition)

    def test_repechage_excludes_active_multi_qualifiers(self):
        self.create_teams(16)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        group_round = materialize_recommended_duel_stage(competition)
        self.play_battle_stage(competition, group_round["stage"])
        active_states = list(
            TeamCompetitionState.objects.filter(
                competition=competition,
                current_status__in=[ParticipantStatus.ACTIVE, ParticipantStatus.QUALIFIED],
            ).select_related("team")
        )
        active_ids = {state.team_id for state in active_states}
        active_names = {state.team.robot_name for state in active_states}
        self.assertTrue(active_ids)

        recommendation = next_phase_recommendation(competition)
        candidate_names = {
            candidate["name"]
            for candidate in recommendation["repechage_preview"]["candidates"]
        }
        self.assertTrue(active_names.isdisjoint(candidate_names))

        repechage = materialize_repechage_stage(competition)
        repechage_ids = set(
            competition.battles.filter(stage=repechage["stage"])
            .values_list("entries__team_id", flat=True)
        )
        self.assertTrue(active_ids.isdisjoint(repechage_ids))

    def test_second_repechage_cannot_immediately_reuse_first_repechage_participants(self):
        self.create_teams(40)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        first = materialize_repechage_stage(competition)
        self.play_battle_stage(competition, first["stage"])

        recommendation = next_phase_recommendation(competition)
        self.assertFalse(recommendation["repechage_preview"]["can_offer"])
        with self.assertRaisesRegex(ValueError, "elegibles"):
            materialize_repechage_stage(competition)

    def test_completed_tournament_hides_phase_advance_action(self):
        self.create_teams(8)
        competition = initialize_competition(self.edition, DivisionType.SCHOOL)
        self.complete_groups(competition)
        self.finish_progressive_tournament(competition)
        competition.refresh_from_db()
        self.assertEqual(competition.status, "completed")

        organizer = get_user_model().objects.create_user(
            username="audit-completed-organizer",
            password="not-used",
            is_staff=True,
        )
        self.client.force_login(organizer)

        overview = self.client.get(
            reverse("tournament:control_division", args=[competition.id])
        )
        final_stage = self.client.get(
            reverse(
                "tournament:control_division_stage",
                args=[competition.id, CompetitionStage.FINAL],
            )
        )

        for response in (overview, final_stage):
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Torneo completado")
            self.assertContains(response, "Torneo finalizado")
            self.assertNotContains(response, "data-phase-decision-open")
