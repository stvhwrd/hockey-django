from django.core.management.base import BaseCommand
from teams.models import Conference, Division, Team, Season
from players.models import Position
from datetime import date


class Command(BaseCommand):
    help = 'Populate database with initial NHL data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate database...'))

        # Create conferences
        eastern, created = Conference.objects.get_or_create(
            name='Eastern Conference',
            defaults={'abbreviation': 'EC'}
        )
        western, created = Conference.objects.get_or_create(
            name='Western Conference',
            defaults={'abbreviation': 'WC'}
        )

        # Create divisions
        atlantic, created = Division.objects.get_or_create(
            name='Atlantic Division',
            defaults={'abbreviation': 'ATL', 'conference': eastern}
        )
        metropolitan, created = Division.objects.get_or_create(
            name='Metropolitan Division',
            defaults={'abbreviation': 'MET', 'conference': eastern}
        )
        central, created = Division.objects.get_or_create(
            name='Central Division',
            defaults={'abbreviation': 'CEN', 'conference': western}
        )
        pacific, created = Division.objects.get_or_create(
            name='Pacific Division',
            defaults={'abbreviation': 'PAC', 'conference': western}
        )

        # Create current season
        current_season, created = Season.objects.get_or_create(
            name='2024-25',
            defaults={
                'start_date': date(2024, 10, 4),
                'end_date': date(2025, 4, 18),
                'playoffs_start_date': date(2025, 4, 21),
                'is_current': True
            }
        )

        # Create some NHL teams
        teams_data = [
            # Atlantic Division
            {'name': 'Bruins', 'city': 'Boston', 'abbreviation': 'BOS', 'division': atlantic},
            {'name': 'Sabres', 'city': 'Buffalo', 'abbreviation': 'BUF', 'division': atlantic},
            {'name': 'Red Wings', 'city': 'Detroit', 'abbreviation': 'DET', 'division': atlantic},
            {'name': 'Panthers', 'city': 'Florida', 'abbreviation': 'FLA', 'division': atlantic},
            {'name': 'Canadiens', 'city': 'Montreal', 'abbreviation': 'MTL', 'division': atlantic},
            {'name': 'Senators', 'city': 'Ottawa', 'abbreviation': 'OTT', 'division': atlantic},
            {'name': 'Lightning', 'city': 'Tampa Bay', 'abbreviation': 'TBL', 'division': atlantic},
            {'name': 'Maple Leafs', 'city': 'Toronto', 'abbreviation': 'TOR', 'division': atlantic},

            # Metropolitan Division
            {'name': 'Hurricanes', 'city': 'Carolina', 'abbreviation': 'CAR', 'division': metropolitan},
            {'name': 'Blue Jackets', 'city': 'Columbus', 'abbreviation': 'CBJ', 'division': metropolitan},
            {'name': 'Devils', 'city': 'New Jersey', 'abbreviation': 'NJD', 'division': metropolitan},
            {'name': 'Islanders', 'city': 'New York', 'abbreviation': 'NYI', 'division': metropolitan},
            {'name': 'Rangers', 'city': 'New York', 'abbreviation': 'NYR', 'division': metropolitan},
            {'name': 'Flyers', 'city': 'Philadelphia', 'abbreviation': 'PHI', 'division': metropolitan},
            {'name': 'Penguins', 'city': 'Pittsburgh', 'abbreviation': 'PIT', 'division': metropolitan},
            {'name': 'Capitals', 'city': 'Washington', 'abbreviation': 'WSH', 'division': metropolitan},

            # Central Division
            {'name': 'Coyotes', 'city': 'Arizona', 'abbreviation': 'ARI', 'division': central},
            {'name': 'Blackhawks', 'city': 'Chicago', 'abbreviation': 'CHI', 'division': central},
            {'name': 'Avalanche', 'city': 'Colorado', 'abbreviation': 'COL', 'division': central},
            {'name': 'Stars', 'city': 'Dallas', 'abbreviation': 'DAL', 'division': central},
            {'name': 'Wild', 'city': 'Minnesota', 'abbreviation': 'MIN', 'division': central},
            {'name': 'Predators', 'city': 'Nashville', 'abbreviation': 'NSH', 'division': central},
            {'name': 'Blues', 'city': 'St. Louis', 'abbreviation': 'STL', 'division': central},
            {'name': 'Jets', 'city': 'Winnipeg', 'abbreviation': 'WPG', 'division': central},

            # Pacific Division
            {'name': 'Ducks', 'city': 'Anaheim', 'abbreviation': 'ANA', 'division': pacific},
            {'name': 'Flames', 'city': 'Calgary', 'abbreviation': 'CGY', 'division': pacific},
            {'name': 'Oilers', 'city': 'Edmonton', 'abbreviation': 'EDM', 'division': pacific},
            {'name': 'Kings', 'city': 'Los Angeles', 'abbreviation': 'LAK', 'division': pacific},
            {'name': 'Sharks', 'city': 'San Jose', 'abbreviation': 'SJS', 'division': pacific},
            {'name': 'Kraken', 'city': 'Seattle', 'abbreviation': 'SEA', 'division': pacific},
            {'name': 'Canucks', 'city': 'Vancouver', 'abbreviation': 'VAN', 'division': pacific},
            {'name': 'Golden Knights', 'city': 'Vegas', 'abbreviation': 'VGK', 'division': pacific},
        ]

        for team_data in teams_data:
            team, created = Team.objects.get_or_create(
                abbreviation=team_data['abbreviation'],
                defaults=team_data
            )
            if created:
                self.stdout.write(f'Created team: {team.full_name}')

        # Create positions
        positions_data = [
            {'name': 'Center', 'abbreviation': 'C', 'category': 'forward'},
            {'name': 'Left Wing', 'abbreviation': 'LW', 'category': 'forward'},
            {'name': 'Right Wing', 'abbreviation': 'RW', 'category': 'forward'},
            {'name': 'Left Defense', 'abbreviation': 'LD', 'category': 'defense'},
            {'name': 'Right Defense', 'abbreviation': 'RD', 'category': 'defense'},
            {'name': 'Goalie', 'abbreviation': 'G', 'category': 'goalie'},
        ]

        for pos_data in positions_data:
            position, created = Position.objects.get_or_create(
                abbreviation=pos_data['abbreviation'],
                defaults=pos_data
            )
            if created:
                self.stdout.write(f'Created position: {position.name}')

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
