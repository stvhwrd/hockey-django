from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from teams.models import Season
from players.models import Player
from games.models import Game


class League(models.Model):
    """Fantasy League"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='fantasy_leagues')

    # League settings
    max_teams = models.PositiveIntegerField(
        default=12,
        validators=[MinValueValidator(4), MaxValueValidator(20)]
    )
    roster_size = models.PositiveIntegerField(default=23)
    starting_lineup_size = models.PositiveIntegerField(default=9)

    # Scoring settings
    scoring_system = models.CharField(max_length=20, choices=[
        ('points', 'Points Only'),
        ('categories', 'Categories'),
        ('rotisserie', 'Rotisserie'),
        ('head_to_head', 'Head-to-Head'),
    ], default='points')

    # Draft settings
    draft_type = models.CharField(max_length=20, choices=[
        ('snake', 'Snake Draft'),
        ('linear', 'Linear Draft'),
        ('auction', 'Auction Draft'),
    ], default='snake')
    draft_date = models.DateTimeField(null=True, blank=True)
    is_drafted = models.BooleanField(default=False)

    # League status
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    commissioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commissioner_leagues')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.season.name})"

    @property
    def current_teams_count(self):
        return self.teams.count()

    @property
    def is_full(self):
        return self.current_teams_count >= self.max_teams

    class Meta:
        ordering = ['-created_at']


class FantasyTeam(models.Model):
    """Fantasy Team within a League"""
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fantasy_teams')
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='teams')

    # Team settings
    logo_url = models.URLField(blank=True)

    # Performance tracking
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    ties = models.PositiveIntegerField(default=0)
    total_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

    @property
    def win_percentage(self):
        total_games = self.wins + self.losses + self.ties
        if total_games > 0:
            return (self.wins + (self.ties * 0.5)) / total_games
        return 0

    class Meta:
        ordering = ['-total_points']
        unique_together = ['owner', 'league']


class Roster(models.Model):
    """Player roster for a fantasy team"""
    fantasy_team = models.OneToOneField(FantasyTeam, on_delete=models.CASCADE, related_name='roster')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fantasy_team.name} Roster"


class RosterPosition(models.Model):
    """Define roster positions for fantasy teams"""
    name = models.CharField(max_length=50)  # e.g., "Center", "Left Wing", "Bench"
    abbreviation = models.CharField(max_length=10)  # e.g., "C", "LW", "BN"
    is_starting = models.BooleanField(default=True)  # False for bench positions
    max_players = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['is_starting', 'name']


class RosterSlot(models.Model):
    """Individual roster slot for a player"""
    roster = models.ForeignKey(Roster, on_delete=models.CASCADE, related_name='slots')
    position = models.ForeignKey(RosterPosition, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)  # For starting lineup

    def __str__(self):
        player_name = self.player.full_name if self.player else "Empty"
        return f"{self.roster.fantasy_team.name} - {self.position.abbreviation}: {player_name}"

    class Meta:
        unique_together = ['roster', 'position', 'player']


class Trade(models.Model):
    """Trade between fantasy teams"""
    from_team = models.ForeignKey(FantasyTeam, on_delete=models.CASCADE, related_name='trades_sent')
    to_team = models.ForeignKey(FantasyTeam, on_delete=models.CASCADE, related_name='trades_received')

    # Trade status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ], default='pending')

    # Trade details
    proposed_date = models.DateTimeField(auto_now_add=True)
    response_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)

    # Optional message
    message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.from_team.name} ↔ {self.to_team.name} ({self.status})"

    class Meta:
        ordering = ['-proposed_date']


class TradePlayer(models.Model):
    """Players involved in a trade"""
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name='players')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    from_team = models.ForeignKey(FantasyTeam, on_delete=models.CASCADE, related_name='traded_away')
    to_team = models.ForeignKey(FantasyTeam, on_delete=models.CASCADE, related_name='traded_for')

    def __str__(self):
        return f"{self.player.full_name}: {self.from_team.name} → {self.to_team.name}"


class FantasyScoring(models.Model):
    """Fantasy scoring settings for a league"""
    league = models.OneToOneField(League, on_delete=models.CASCADE, related_name='scoring_settings')

    # Offensive stats
    goals_points = models.DecimalField(max_digits=5, decimal_places=2, default=6.0)
    assists_points = models.DecimalField(max_digits=5, decimal_places=2, default=4.0)
    plus_minus_points = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    penalty_minutes_points = models.DecimalField(max_digits=5, decimal_places=2, default=0.5)
    power_play_goals_points = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    power_play_assists_points = models.DecimalField(max_digits=5, decimal_places=2, default=0.5)
    short_handed_goals_points = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
    short_handed_assists_points = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    shots_on_goal_points = models.DecimalField(max_digits=5, decimal_places=2, default=0.4)
    hits_points = models.DecimalField(max_digits=5, decimal_places=2, default=0.6)
    blocked_shots_points = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)

    # Goalie stats
    wins_points = models.DecimalField(max_digits=5, decimal_places=2, default=4.0)
    losses_points = models.DecimalField(max_digits=5, decimal_places=2, default=-1.0)
    goals_against_points = models.DecimalField(max_digits=5, decimal_places=2, default=-1.0)
    saves_points = models.DecimalField(max_digits=5, decimal_places=2, default=0.6)
    shutouts_points = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)

    def __str__(self):
        return f"{self.league.name} Scoring Settings"


class FantasyWeek(models.Model):
    """Fantasy week/matchup period"""
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='weeks')
    week_number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_playoffs = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.league.name} - Week {self.week_number}"

    class Meta:
        ordering = ['week_number']
        unique_together = ['league', 'week_number']


class Matchup(models.Model):
    """Head-to-head matchup between two fantasy teams"""
    week = models.ForeignKey(FantasyWeek, on_delete=models.CASCADE, related_name='matchups')
    team1 = models.ForeignKey(FantasyTeam, on_delete=models.CASCADE, related_name='matchups_as_team1')
    team2 = models.ForeignKey(FantasyTeam, on_delete=models.CASCADE, related_name='matchups_as_team2')

    # Scores
    team1_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    team2_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Status
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name} - Week {self.week.week_number}"

    @property
    def winner(self):
        if self.is_complete:
            if self.team1_score > self.team2_score:
                return self.team1
            elif self.team2_score > self.team1_score:
                return self.team2
        return None

    class Meta:
        unique_together = ['week', 'team1', 'team2']


class PlayerFantasyStats(models.Model):
    """Player fantasy points for a specific week"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='fantasy_stats')
    week = models.ForeignKey(FantasyWeek, on_delete=models.CASCADE, related_name='player_stats')
    fantasy_team = models.ForeignKey(FantasyTeam, on_delete=models.CASCADE, related_name='player_weekly_stats')

    # Raw stats (copied from game stats)
    games_played = models.PositiveIntegerField(default=0)
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    plus_minus = models.IntegerField(default=0)
    penalty_minutes = models.PositiveIntegerField(default=0)
    power_play_goals = models.PositiveIntegerField(default=0)
    power_play_assists = models.PositiveIntegerField(default=0)
    short_handed_goals = models.PositiveIntegerField(default=0)
    short_handed_assists = models.PositiveIntegerField(default=0)
    shots_on_goal = models.PositiveIntegerField(default=0)
    hits = models.PositiveIntegerField(default=0)
    blocked_shots = models.PositiveIntegerField(default=0)

    # Goalie stats
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    goals_against = models.PositiveIntegerField(default=0)
    saves = models.PositiveIntegerField(default=0)
    shutouts = models.PositiveIntegerField(default=0)

    # Calculated fantasy points
    total_fantasy_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_fantasy_points(self):
        """Calculate fantasy points based on league scoring settings"""
        scoring = self.fantasy_team.league.scoring_settings

        points = (
            (self.goals * scoring.goals_points) +
            (self.assists * scoring.assists_points) +
            (self.plus_minus * scoring.plus_minus_points) +
            (self.penalty_minutes * scoring.penalty_minutes_points) +
            (self.power_play_goals * scoring.power_play_goals_points) +
            (self.power_play_assists * scoring.power_play_assists_points) +
            (self.short_handed_goals * scoring.short_handed_goals_points) +
            (self.short_handed_assists * scoring.short_handed_assists_points) +
            (self.shots_on_goal * scoring.shots_on_goal_points) +
            (self.hits * scoring.hits_points) +
            (self.blocked_shots * scoring.blocked_shots_points) +
            (self.wins * scoring.wins_points) +
            (self.losses * scoring.losses_points) +
            (self.goals_against * scoring.goals_against_points) +
            (self.saves * scoring.saves_points) +
            (self.shutouts * scoring.shutouts_points)
        )

        return points

    def save(self, *args, **kwargs):
        self.total_fantasy_points = self.calculate_fantasy_points()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player.full_name} - Week {self.week.week_number} ({self.total_fantasy_points} pts)"

    class Meta:
        ordering = ['-total_fantasy_points']
        unique_together = ['player', 'week', 'fantasy_team']
