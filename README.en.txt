IL2 stats - statistics system for a dedicated server IL2 Battle of Stalingrad.
The system is designed to collect information about the actions of the players and organize the data on a particular dedicated server.

The software is conceived, developed and supported by a team of two people (=FB=Vaal and =FB=Isay) solely as a personal initiative, ie It is not a project studio 1CGS.
The main motivation for the creation of this project wishes to develop IL-2 BOS,
create new opportunities for the community to organize multiplayer projects IL-2 BOS.
Software is free. License MIT.
The authors of the software do not give any warranty and do not bear any responsibility.


===== VERSION INFORMATION =====

This version has been migrated to Django 5.2 LTS for improved security, performance, and long-term support.

Current Stack:
- Django 5.2.17 LTS (Long-Term Support until April 2028)
- Python 3.11+ (3.12 recommended)
- PostgreSQL 10+ (13+ recommended)
- WhiteNoise 6.12.0 for static file serving

For installation and upgrade instructions, see INSTALLATION.md or use the scripts in the /run directory.


!!!!! IMPORTANT !!!!!

Algorithms collection statistics IL2 stats differs from statistics in-game. As a consequence of these statistics will not coincide with the game.
The kill count system is designed for the server with setting - finishMissionIfLanded.

===== SYSTEM REQUIREMENTS =====

Before installation, ensure you have:
1. Python 3.11 or 3.12 installed
2. PostgreSQL 10.0 or newer
3. pip and virtualenv
4. At least 1GB of available disk space

===== INSTALLATION =====

Windows:
1. Navigate to the /run directory
2. Run: install.cmd
3. Follow the prompts

Linux/Mac:
1. Navigate to the /run directory
2. Run: chmod +x install.sh && ./install.sh
3. Follow the prompts

Alternatively, manual installation:
1. Create virtual environment: python3 -m venv .venv
2. Activate it: source .venv/bin/activate  (Linux/Mac) or .venv\Scripts\activate (Windows)
3. Install dependencies: pip install -r requirements.txt
4. Navigate to src: cd src
5. Run migrations: python manage.py migrate
6. Collect static files: python manage.py collectstatic --noinput
7. Create admin user: python manage.py createsuperuser
8. (Optional) Import data: python manage.py import_csv_data

===== RUNNING THE APPLICATION =====

Windows:
- Run ./run/waitress.cmd to start the server

Linux/Mac:
- Run ./run/waitress.sh to start the server

The server will be available at the configured host and port (default: http://localhost:8000)

===== OPTIONS =====

The name of the server on the site changes in the administrative panel, see Chunks.

In the stats section are optional settings:
mission_report_delete - remove already processed logs (true / false)
mission_report_backup_days - the number of days to keep backup copies of the logs (they are stored in a packed zip file)
inactive_player_days - How many days a player must be out to statistics exclude it from the rankings
new_tour_by_month - activating automatic system tours by months (true / false)
win_by_score - Activation of calculating victory on scores in the mission if not victory by the completed task
win_score_min - the minimum number of scores for the coalition wins on scores
win_score_ratio - minimum ratio of two coalition scores to determine the winning coalition


Email section contains settings for sending mail.
Settings required to send email of registration activation or reset password.
We recommend using the smtp server https://mailgun.com/
Their free fare allows you to send 10,000 email a month.
By default, sending mail is disabled. The functions that depend on it are automatically deactivated.


===== RECOMMENDED WAYS TO MAKE CHANGES =====

Scores need to change in the administrative panel of site (http://адрес_сайта/admin/), section Scoring.

To change the templates and css styles - it is recommended to create a copy of the file (and subdirectories if required) in the catalog custom.
Files of custom directory will take precedence over the original files, and because the original files will be untouched. This makes it easier to update statistics on a new version.

After making changes in css styles, images, templates - is needed to run a command collectstatic to rebuild  static files.

===== UPDATING FROM DJANGO 1.11 =====

If you are upgrading from Django 1.11.29:
1. Backup your database
2. Update the codebase from git
3. Run ./run/update.cmd (Windows) or ./run/update.sh (Linux/Mac)
4. Verify the application loads without errors
5. Test all features in a staging environment first

Note: The migration to Django 5.2 includes:
- Updated URL routing patterns
- Modernized database field types
- Enhanced security settings
- Better performance and caching

===== SUPPORT & DOCUMENTATION =====

For detailed migration information, see MIGRATION_REPORT.md
For troubleshooting, check the application logs in django.log
For Django 5.2 documentation, visit https://docs.djangoproject.com/en/5.2/

