from django.contrib import admin

from .models import (
    CompetitionBattle,
    CompetitionBattleEntry,
    CompetitionHistoryEntry,
    DivisionCompetition,
    DivisionGroup,
    DivisionGroupEntry,
    Match,
    RuleSection,
    TeamCompetitionState,
    TournamentEdition,
    TournamentPhase,
)


class RuleSectionInline(admin.TabularInline):
    model = RuleSection
    extra = 0


@admin.register(TournamentEdition)
class TournamentEditionAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "location", "is_active")
    list_filter = ("is_active",)
    inlines = [RuleSectionInline]


@admin.register(TournamentPhase)
class TournamentPhaseAdmin(admin.ModelAdmin):
    list_display = ("name", "edition", "phase_type", "order", "is_public")
    list_filter = ("phase_type", "is_public")
    search_fields = ("name", "edition__name")


@admin.register(RuleSection)
class RuleSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "edition", "order", "is_published")
    list_filter = ("is_published", "edition")
    search_fields = ("title", "summary", "edition__name")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("phase", "team_a", "team_b", "scheduled_at", "status", "winner")
    list_filter = ("status", "phase__edition")
    search_fields = ("team_a__name", "team_b__name", "phase__name")


@admin.register(DivisionCompetition)
class DivisionCompetitionAdmin(admin.ModelAdmin):
    list_display = ("edition", "division", "format_key", "status", "shuffle_seed")
    list_filter = ("division", "status", "edition")


@admin.register(DivisionGroup)
class DivisionGroupAdmin(admin.ModelAdmin):
    list_display = ("competition", "label", "order", "expected_size")
    list_filter = ("competition__edition", "competition__division")


@admin.register(DivisionGroupEntry)
class DivisionGroupEntryAdmin(admin.ModelAdmin):
    list_display = ("group", "team", "slot_order", "final_rank", "qualified_from_group")
    list_filter = ("group__competition__edition", "group__competition__division")
    search_fields = ("team__name", "team__robot_name")


@admin.register(CompetitionBattle)
class CompetitionBattleAdmin(admin.ModelAdmin):
    list_display = ("competition", "stage", "name", "order", "status", "winner")
    list_filter = ("competition__edition", "competition__division", "stage", "status")
    search_fields = ("name", "winner__name", "winner__robot_name")


@admin.register(CompetitionBattleEntry)
class CompetitionBattleEntryAdmin(admin.ModelAdmin):
    list_display = ("battle", "team", "slot_order", "origin_label")
    list_filter = ("battle__competition__edition", "battle__competition__division", "battle__stage")
    search_fields = ("team__name", "team__robot_name", "origin_label")


@admin.register(TeamCompetitionState)
class TeamCompetitionStateAdmin(admin.ModelAdmin):
    list_display = ("competition", "team", "current_stage", "current_status", "current_group", "current_battle")
    list_filter = ("competition__edition", "competition__division", "current_stage", "current_status")
    search_fields = ("team__robot_name", "team__institution__name")


@admin.register(CompetitionHistoryEntry)
class CompetitionHistoryEntryAdmin(admin.ModelAdmin):
    list_display = ("competition", "team", "action_type", "stage", "status", "title", "created_at")
    list_filter = ("competition__edition", "competition__division", "action_type", "stage", "status")
    search_fields = ("team__robot_name", "title", "description")
