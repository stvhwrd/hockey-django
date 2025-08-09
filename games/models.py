from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from teams.models import Team, Season
from players.models import Player


class Game(models.Model):
    """NHL Game"""
    # Basic game info
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_games')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_games')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='games')

    # Game details
    game_date = models.DateTimeField()
    game_type = models.CharField(max_length=20, choices=[
        ('regular', 'Regular Season'),
        ('playoff', 'Playoff'),
        ('preseason', 'Preseason'),
        ('all_star', 'All-Star Game'),
    ], default='regular')

    # Scores
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)

    # Game status
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('final', 'Final'),
        ('overtime', 'Final (OT)'),
        ('shootout', 'Final (SO)'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
    ], default='scheduled')

    # Game periods
    periods_played = models.PositiveIntegerField(default=0)
    overtime_periods = models.PositiveIntegerField(default=0)
    shootout = models.BooleanField(default=False)

    # Attendance and venue
    attendance = models.PositiveIntegerField(null=True, blank=True)
    venue = models.CharField(max_length=200, blank=True)

    # External IDs
    nhl_game_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.away_team.abbreviation} @ {self.home_team.abbreviation} - {self.game_date.strftime('%Y-%m-%d')}"

    @property
    def winner(self):
        if self.status in ['final', 'overtime', 'shootout']:
            if self.home_score > self.away_score:
                return self.home_team
            elif self.away_score > self.home_score:
                return self.away_team
        return None

    @property
    def loser(self):
        if self.status in ['final', 'overtime', 'shootout']:
            if self.home_score > self.away_score:
                return self.away_team
            elif self.away_score > self.home_score:
                return self.home_team
        return None

    @property
    def is_overtime_game(self):
        return self.status in ['overtime', 'shootout']

    class Meta:
        ordering = ['-game_date']
        unique_together = ['home_team', 'away_team', 'game_date']


class GameEvent(models.Model):
    """Individual events that happen during a game (goals, penalties, etc.)"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='events')

    # Event details
    event_type = models.CharField(max_length=20, choices=[
        ('goal', 'Goal'),
        ('assist', 'Assist'),
        ('penalty', 'Penalty'),
        ('save', 'Save'),
        ('shot', 'Shot'),
        ('hit', 'Hit'),
        ('blocked_shot', 'Blocked Shot'),
        ('faceoff', 'Faceoff'),
        ('giveaway', 'Giveaway'),
        ('takeaway', 'Takeaway'),
    ])

    # Timing
    period = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    time_in_period = models.CharField(max_length=10)  # e.g., "12:34"
    game_time_seconds = models.PositiveIntegerField()  # Total seconds elapsed in game

    # Players involved
    primary_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='primary_events')
    secondary_player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='secondary_events')

    # Team
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='game_events')

    # Event-specific details (JSON field for flexibility)
    event_details = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.primary_player.full_name} ({self.time_in_period} P{self.period})"

    class Meta:
        ordering = ['game_time_seconds']


class Goal(models.Model):
    """Detailed goal information"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='goals')
    scorer = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='goals_scored')
    assist1 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_assists')
    assist2 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='secondary_assists')

    # Goal details
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='goals_for')
    period = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    time_in_period = models.CharField(max_length=10)
    game_time_seconds = models.PositiveIntegerField()

    # Goal type
    goal_type = models.CharField(max_length=20, choices=[
        ('even_strength', 'Even Strength'),
        ('power_play', 'Power Play'),
        ('short_handed', 'Short Handed'),
        ('penalty_shot', 'Penalty Shot'),
        ('empty_net', 'Empty Net'),
    ], default='even_strength')

    # Strength at time of goal
    home_players_on_ice = models.PositiveIntegerField(default=6)
    away_players_on_ice = models.PositiveIntegerField(default=6)

    def __str__(self):
        return f"{self.scorer.full_name} ({self.time_in_period} P{self.period}) - {self.game}"

    class Meta:
        ordering = ['game', 'game_time_seconds']


class PlayerGameStats(models.Model):
    """Player statistics for a specific game"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_stats')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='player_stats')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)  # Team they played for in this game

    # Playing status
    played = models.BooleanField(default=True)
    starter = models.BooleanField(default=False)

    # Basic stats
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)
    plus_minus = models.IntegerField(default=0)
    penalty_minutes = models.PositiveIntegerField(default=0)

    # Shooting
    shots_on_goal = models.PositiveIntegerField(default=0)
    shots_missed = models.PositiveIntegerField(default=0)
    shots_blocked = models.PositiveIntegerField(default=0)

    # Time on ice
    time_on_ice_seconds = models.PositiveIntegerField(default=0)

    # Physical play
    hits = models.PositiveIntegerField(default=0)
    blocked_shots = models.PositiveIntegerField(default=0)

    # Faceoffs (for centers)
    faceoff_wins = models.PositiveIntegerField(default=0)
    faceoff_attempts = models.PositiveIntegerField(default=0)

    # Goalie stats
    saves = models.PositiveIntegerField(default=0)
    goals_against = models.PositiveIntegerField(default=0)
    shots_against = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # Auto-calculate points
        self.points = self.goals + self.assists
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player.full_name} - {self.game}"

    @property
    def faceoff_percentage(self):
        if self.faceoff_attempts > 0:
            return (self.faceoff_wins / self.faceoff_attempts) * 100
        return 0

    @property
    def save_percentage(self):
        if self.shots_against > 0:
            return (self.saves / self.shots_against)
        return 0

    @property
    def time_on_ice_display(self):
        """Convert TOI seconds to MM:SS format"""
        if self.time_on_ice_seconds:
            minutes = self.time_on_ice_seconds // 60
            seconds = self.time_on_ice_seconds % 60
            return f"{minutes}:{seconds:02d}"
        return "0:00"

    class Meta:
        ordering = ['-game__game_date', '-points']
        unique_together = ['player', 'game']
