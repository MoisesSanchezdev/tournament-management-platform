from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q

from apps.common.models import TimeStampedModel
from apps.participants.models import Team


class TournamentEdition(TimeStampedModel):
    name = models.CharField(max_length=160, unique=True)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=160, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=Q(is_active=True),
                name="single_active_tournament_edition",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class DivisionType(models.TextChoices):
    SCHOOL = "school", "Colegios"
    UNIVERSITY = "university", "Universidades"


class RuleSection(TimeStampedModel):
    edition = models.ForeignKey(
        TournamentEdition,
        on_delete=models.CASCADE,
        related_name="rule_sections",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=140)
    summary = models.CharField(max_length=240)
    body = models.TextField()
    order = models.PositiveIntegerField(default=1)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self) -> str:
        return self.title


class PhaseType(models.TextChoices):
    QUALIFIERS = "qualifiers", "Clasificatoria"
    GROUPS = "groups", "Grupos"
    ROUND_OF_16 = "round_of_16", "Octavos"
    QUARTERFINAL = "quarterfinal", "Cuartos"
    SEMIFINAL = "semifinal", "Semifinal"
    FINAL = "final", "Final"
    CUSTOM = "custom", "Personalizada"


class TournamentPhase(TimeStampedModel):
    edition = models.ForeignKey(TournamentEdition, on_delete=models.CASCADE, related_name="phases")
    name = models.CharField(max_length=120)
    phase_type = models.CharField(max_length=20, choices=PhaseType.choices, default=PhaseType.CUSTOM)
    order = models.PositiveIntegerField(default=1)
    is_public = models.BooleanField(default=False)
    configuration = models.JSONField(
        default=dict,
        blank=True,
        help_text="Permite guardar formato, cantidad de clasificados u otras reglas variables."
    )

    class Meta:
        ordering = ["order", "created_at"]
        unique_together = ("edition", "order")

    def __str__(self) -> str:
        return f"{self.edition.name} - {self.name}"


class MatchStatus(models.TextChoices):
    PENDING = "pending", "Pendiente"
    READY = "ready", "Listo"
    IN_PROGRESS = "in_progress", "En juego"
    FINISHED = "finished", "Finalizado"
    CANCELED = "canceled", "Cancelado"


class CompetitionStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    READY = "ready", "Listo"
    IN_PROGRESS = "in_progress", "En progreso"
    COMPLETED = "completed", "Completado"


class CompetitionStage(models.TextChoices):
    GROUPS = "groups", "Grupos"
    PURGATORY_1 = "purgatory_1", "Purgatorio 1"
    ROUND_OF_32 = "round_of_32", "Ronda de 32"
    ROUND_OF_16 = "round_of_16", "Octavos"
    PURGATORY_2 = "purgatory_2", "Purgatorio 2"
    QUARTERFINAL = "quarterfinal", "Cuartos"
    SEMIFINAL = "semifinal", "Semifinal"
    THIRD_PLACE = "third_place", "Tercer lugar"
    FINAL = "final", "Final"


class BattleFormat(models.TextChoices):
    GROUP = "group", "Grupo"
    BATTLE_ROYALE = "battle_royale", "Campal"
    DUEL = "duel", "1 vs 1"
    TRIANGULAR = "triangular", "Triangular"


class ParticipantStatus(models.TextChoices):
    ACTIVE = "active", "Activo"
    ELIMINATED = "eliminated", "Eliminado"
    REPECHAGE = "repechage", "En repechaje"
    QUALIFIED = "qualified", "Clasificado"
    WITHDRAWN = "withdrawn", "Retirado"


class HistoryActionType(models.TextChoices):
    AUTO_SYNC = "auto_sync", "Sincronizacion automatica"
    GROUP_RESULT = "group_result", "Resultado de grupos"
    BATTLE_RESULT = "battle_result", "Resultado de batalla"
    MANUAL_MOVE = "manual_move", "Movimiento manual"
    STATUS_CHANGE = "status_change", "Cambio de estado"
    REINTEGRATED = "reintegrated", "Reintegrado"


class DivisionCompetition(TimeStampedModel):
    edition = models.ForeignKey(TournamentEdition, on_delete=models.CASCADE, related_name="competitions")
    division = models.CharField(max_length=20, choices=DivisionType.choices)
    name = models.CharField(max_length=120)
    format_key = models.CharField(max_length=40, blank=True)
    configuration = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=CompetitionStatus.choices, default=CompetitionStatus.DRAFT)
    shuffle_seed = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["division", "created_at"]
        constraints = [
            models.UniqueConstraint(fields=["edition", "division"], name="unique_competition_per_division"),
        ]

    def __str__(self) -> str:
        return f"{self.edition.name} - {self.get_division_display()}"


class DivisionGroup(TimeStampedModel):
    competition = models.ForeignKey(DivisionCompetition, on_delete=models.CASCADE, related_name="groups")
    label = models.CharField(max_length=4)
    order = models.PositiveSmallIntegerField()
    expected_size = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "label"]
        constraints = [
            models.UniqueConstraint(fields=["competition", "label"], name="unique_group_label_per_competition"),
            models.UniqueConstraint(fields=["competition", "order"], name="unique_group_order_per_competition"),
        ]

    def __str__(self) -> str:
        return f"{self.competition} - Grupo {self.label}"


class DivisionGroupEntry(TimeStampedModel):
    group = models.ForeignKey(DivisionGroup, on_delete=models.CASCADE, related_name="entries")
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="group_entries")
    slot_order = models.PositiveSmallIntegerField()
    final_rank = models.PositiveSmallIntegerField(null=True, blank=True)
    qualified_from_group = models.BooleanField(default=False)

    class Meta:
        ordering = ["slot_order", "created_at"]
        constraints = [
            models.UniqueConstraint(fields=["group", "team"], name="unique_team_per_group"),
            models.UniqueConstraint(fields=["group", "slot_order"], name="unique_slot_per_group"),
            models.UniqueConstraint(
                fields=["group", "final_rank"],
                condition=Q(final_rank__isnull=False),
                name="unique_rank_per_group",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.group} - {self.team}"


class CompetitionBattle(TimeStampedModel):
    competition = models.ForeignKey(DivisionCompetition, on_delete=models.CASCADE, related_name="battles")
    stage = models.CharField(max_length=20, choices=CompetitionStage.choices)
    format_type = models.CharField(max_length=20, choices=BattleFormat.choices, default=BattleFormat.DUEL)
    order = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=MatchStatus.choices, default=MatchStatus.PENDING)
    winner = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="competition_wins",
        null=True,
        blank=True,
    )
    arena = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["stage", "order", "created_at"]
        constraints = [
            models.UniqueConstraint(fields=["competition", "stage", "order"], name="unique_battle_order_per_stage"),
        ]

    def __str__(self) -> str:
        return f"{self.competition} - {self.name}"

    def clean(self):
        if self.winner and not self.entries.filter(team=self.winner).exists():
            raise ValidationError("El ganador debe pertenecer a los participantes de la batalla.")


class CompetitionBattleEntry(TimeStampedModel):
    battle = models.ForeignKey(CompetitionBattle, on_delete=models.CASCADE, related_name="entries")
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="battle_entries")
    slot_order = models.PositiveSmallIntegerField()
    origin_label = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["slot_order", "created_at"]
        constraints = [
            models.UniqueConstraint(fields=["battle", "team"], name="unique_team_per_battle"),
            models.UniqueConstraint(fields=["battle", "slot_order"], name="unique_slot_per_battle"),
        ]

    def __str__(self) -> str:
        return f"{self.battle} - {self.team}"


class TeamCompetitionState(TimeStampedModel):
    competition = models.ForeignKey(DivisionCompetition, on_delete=models.CASCADE, related_name="team_states")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="competition_states")
    current_stage = models.CharField(max_length=20, choices=CompetitionStage.choices, default=CompetitionStage.GROUPS)
    current_status = models.CharField(
        max_length=20,
        choices=ParticipantStatus.choices,
        default=ParticipantStatus.ACTIVE,
    )
    current_group = models.ForeignKey(
        DivisionGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_states",
    )
    current_battle = models.ForeignKey(
        CompetitionBattle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_states",
    )
    manual_status_override = models.CharField(
        max_length=20,
        choices=ParticipantStatus.choices,
        blank=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["competition", "team__robot_name"]
        constraints = [
            models.UniqueConstraint(fields=["competition", "team"], name="unique_state_per_team_competition"),
        ]

    def __str__(self) -> str:
        return f"{self.competition} - {self.team.robot_name}"


class CompetitionHistoryEntry(TimeStampedModel):
    competition = models.ForeignKey(DivisionCompetition, on_delete=models.CASCADE, related_name="history_entries")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="competition_history")
    action_type = models.CharField(max_length=20, choices=HistoryActionType.choices)
    stage = models.CharField(max_length=20, choices=CompetitionStage.choices, blank=True)
    status = models.CharField(max_length=20, choices=ParticipantStatus.choices, blank=True)
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    previous_stage = models.CharField(max_length=20, choices=CompetitionStage.choices, blank=True)
    new_stage = models.CharField(max_length=20, choices=CompetitionStage.choices, blank=True)
    previous_status = models.CharField(max_length=20, choices=ParticipantStatus.choices, blank=True)
    new_status = models.CharField(max_length=20, choices=ParticipantStatus.choices, blank=True)
    previous_group = models.ForeignKey(
        DivisionGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history_previous_entries",
    )
    new_group = models.ForeignKey(
        DivisionGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history_new_entries",
    )
    battle = models.ForeignKey(
        CompetitionBattle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history_entries",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.competition} - {self.team.robot_name} - {self.title}"


class Match(TimeStampedModel):
    phase = models.ForeignKey(TournamentPhase, on_delete=models.CASCADE, related_name="matches")
    arena = models.CharField(max_length=80, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    team_a = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="matches_as_a")
    team_b = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="matches_as_b")
    score_a = models.PositiveSmallIntegerField(default=0)
    score_b = models.PositiveSmallIntegerField(default=0)
    winner = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="won_matches",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=MatchStatus.choices, default=MatchStatus.PENDING)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Datos flexibles: tiempo, juez, observaciones, globos explotados, etc."
    )

    class Meta:
        ordering = ["scheduled_at", "created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["scheduled_at"]),
        ]
        constraints = [
            models.CheckConstraint(check=~Q(team_a=F("team_b")), name="prevent_self_match"),
        ]

    def __str__(self) -> str:
        return f"{self.team_a} vs {self.team_b}"

    def clean(self):
        if self.winner and self.winner not in {self.team_a, self.team_b}:
            raise ValidationError("El ganador debe ser uno de los equipos del enfrentamiento.")
