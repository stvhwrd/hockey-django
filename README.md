# Fantasy Hockey Platform

A Django-based fantasy hockey platform focused on comprehensive data management and analytics.

## Quick Start

To get the app running quickly:

```bash
# Clone and setup
git clone https://github.com/stvhwrd/hockey-django.git
cd hockey-django
python3 -m venv .venv
source .venv/bin/activate

# Install and setup database
pip install -r requirements.txt
python manage.py migrate
python manage.py populate_initial_data

# Run the server
python manage.py runserver
```

Then visit <http://localhost:8000> to see the application!

## Project Structure

This project is organized into several Django apps:

### Apps

- **`teams/`** - NHL teams, conferences, divisions, and seasons
- **`players/`** - Player profiles, statistics, and team history
- **`games/`** - Game data, events, goals, and player game statistics
- **`fantasy/`** - Fantasy leagues, teams, rosters, and scoring

## Database Models

### Teams App

- **Conference** - NHL conferences (Eastern, Western)
- **Division** - NHL divisions (Atlantic, Metropolitan, Central, Pacific)
- **Team** - NHL teams with branding and arena information
- **Season** - NHL seasons with date ranges

### Players App

- **Position** - Hockey positions (C, LW, RW, LD, RD, G)
- **Player** - Player profiles with personal and career information
- **PlayerTeamHistory** - Track player movements between teams
- **PlayerStats** - Season statistics for players

### Games App

- **Game** - Individual NHL games
- **GameEvent** - Game events (goals, penalties, shots, etc.)
- **Goal** - Detailed goal information with assists
- **PlayerGameStats** - Player statistics for specific games

### Fantasy App

- **League** - Fantasy leagues with settings and rules
- **FantasyTeam** - Teams within fantasy leagues
- **Roster/RosterSlot** - Player rosters and positions
- **Trade** - Trading system between fantasy teams
- **FantasyScoring** - Configurable scoring settings
- **FantasyWeek/Matchup** - Weekly matchups and scheduling
- **PlayerFantasyStats** - Weekly fantasy points calculation

## Getting Started

### Prerequisites

- Python 3.8+
- Django 5.2+

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/stvhwrd/hockey-django.git
   cd hockey-django
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   *Or install manually:*

   ```bash
   pip install django python-decouple psycopg2-binary pillow
   ```

4. **Run database migrations:**

   ```bash
   python manage.py migrate
   ```

5. **Populate initial NHL data:**

   ```bash
   python manage.py populate_initial_data
   ```

6. **Create a superuser (optional):**

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server:**

   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   - Main site: <http://localhost:8000/>
   - Admin interface: <http://localhost:8000/admin/>

### Admin Interface

Access the Django admin at `http://localhost:8000/admin/` to manage:

- Teams and organizational structure
- Player profiles and statistics
- Game data and events
- Fantasy leagues and teams

## Key Features

### Data-Centric Design

- Comprehensive player statistics tracking
- Detailed game event logging
- Historical data preservation
- Flexible fantasy scoring systems
- **NHL data integration** via `nhldata` package for real-time API access

### Fantasy Features

- Multiple league types (points, categories, head-to-head)
- Configurable roster sizes and positions
- Trading system between teams
- Weekly matchups and scoring
- Automated fantasy points calculation

### Extensibility

- Modular app structure for easy feature additions
- JSON fields for flexible event data storage
- External ID fields for data imports
- Abstract base classes for common functionality

## Development

### Adding New Features

1. Create models in the appropriate app
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Register models in admin.py if needed
5. Create management commands for data population

### Data Import

The project is designed to accept data from external sources:

- **NHL API integration** via the `nhldata` package for accessing:
  - Official NHL APIs (roster data, stats, schedules)
  - MoneyPuck.com advanced analytics and shot data
  - Real-time and historical NHL data
- External ID fields for data imports from other sources
- Flexible JSON fields for varying data structures
- Bulk import capabilities through management commands

## Future Enhancements

- Enhanced NHL data integration with `nhldata` package:
  - Automated player roster updates
  - Real-time game statistics import
  - Historical shot data from MoneyPuck
  - Advanced analytics and projections
- Mobile app support
- Social features (leagues, chat, etc.)
- Draft tools and utilities
- Live scoring and notifications

## License

This project is licensed under the MIT License.
