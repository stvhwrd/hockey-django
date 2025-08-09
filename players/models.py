from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from teams.models import Team, Season


class Position(models.Model):
    """Hockey positions"""
    name = models.CharField(max_length=50, unique=True)  # e.g., "Center", "Left Wing"
    abbreviation = models.CharField(max_length=5, unique=True)  # e.g., "C", "LW"
    category = models.CharField(max_length=20, choices=[
        ('forward', 'Forward'),
        ('defense', 'Defense'),
        ('goalie', 'Goalie'),
    ])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['category', 'name']


class Player(models.Model):
    """NHL Player"""
    # Basic info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    jersey_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        null=True, blank=True
    )

    # Physical attributes
    height_inches = models.PositiveIntegerField(null=True, blank=True)  # Total height in inches
    weight_lbs = models.PositiveIntegerField(null=True, blank=True)

    # Personal details
    birth_date = models.DateField(null=True, blank=True)
    birth_city = models.CharField(max_length=100, blank=True)
    birth_country = models.CharField(max_length=100, blank=True)
    nationality = models.CharField(max_length=100, blank=True)

    # Hockey details
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='players')
    shoots = models.CharField(max_length=5, choices=[
        ('L', 'Left'),
        ('R', 'Right'),
    ], blank=True)
    catches = models.CharField(max_length=5, choices=[
        ('L', 'Left'),
        ('R', 'Right'),
    ], blank=True)  # For goalies

    # Career info
    draft_year = models.PositiveIntegerField(null=True, blank=True)
    draft_round = models.PositiveIntegerField(null=True, blank=True)
    draft_pick = models.PositiveIntegerField(null=True, blank=True)
    draft_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='drafted_players')

    # Status
    is_active = models.BooleanField(default=True)
    is_rookie = models.BooleanField(default=False)

    # External IDs (for data imports)
    nhl_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    @property
    def height_display(self):
        """Convert height in inches to feet'inches" format"""
        if self.height_inches:
            feet = self.height_inches // 12
            inches = self.height_inches % 12
            return f"{feet}'{inches}\""
        return None

    class Meta:
        ordering = ['last_name', 'first_name']


class PlayerTeamHistory(models.Model):
    """Track player's team history"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='team_history')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='player_history')
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    # Contract details
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # Null if still active
    jersey_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        null=True, blank=True
    )

    # Status
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.player.full_name} - {self.team.full_name} ({self.season.name})"

    class Meta:
        ordering = ['-start_date']
        unique_together = ['player', 'team', 'season']


class PlayerStats(models.Model):
    """Player statistics for a specific season"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='stats')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='player_stats')
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    # Game counts
    games_played = models.PositiveIntegerField(default=0)

    # Scoring stats (for forwards/defense)
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)  # goals + assists
    plus_minus = models.IntegerField(default=0)
    penalty_minutes = models.PositiveIntegerField(default=0)

    # Power play stats
    power_play_goals = models.PositiveIntegerField(default=0)
    power_play_assists = models.PositiveIntegerField(default=0)
    power_play_points = models.PositiveIntegerField(default=0)

    # Short handed stats
    short_handed_goals = models.PositiveIntegerField(default=0)
    short_handed_assists = models.PositiveIntegerField(default=0)
    short_handed_points = models.PositiveIntegerField(default=0)

    # Shooting stats
    shots_on_goal = models.PositiveIntegerField(default=0)
    shooting_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    # Time stats
    time_on_ice_seconds = models.PositiveIntegerField(default=0)  # Total TOI in seconds
    average_time_on_ice_seconds = models.PositiveIntegerField(default=0)  # Average TOI per game

    # Goalie stats
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    overtime_losses = models.PositiveIntegerField(default=0)
    shutouts = models.PositiveIntegerField(default=0)
    goals_against = models.PositiveIntegerField(default=0)
    shots_against = models.PositiveIntegerField(default=0)
    saves = models.PositiveIntegerField(default=0)
    goals_against_average = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    save_percentage = models.DecimalField(max_digits=5, decimal_places=3, default=0.0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-calculate derived stats
        self.points = self.goals + self.assists
        self.power_play_points = self.power_play_goals + self.power_play_assists
        self.short_handed_points = self.short_handed_goals + self.short_handed_assists

        # Calculate shooting percentage
        if self.shots_on_goal > 0:
            self.shooting_percentage = (self.goals / self.shots_on_goal) * 100

        # Calculate save percentage
        if self.shots_against > 0:
            self.save_percentage = (self.saves / self.shots_against)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player.full_name} - {self.season.name} ({self.team.abbreviation})"

    @property
    def average_time_on_ice_display(self):
        """Convert average TOI seconds to MM:SS format"""
        if self.average_time_on_ice_seconds:
            minutes = self.average_time_on_ice_seconds // 60
            seconds = self.average_time_on_ice_seconds % 60
            return f"{minutes}:{seconds:02d}"
        return "0:00"

    class Meta:
        ordering = ['-season__start_date', '-points']
        unique_together = ['player', 'team', 'season']
