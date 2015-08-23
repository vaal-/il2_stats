IL2 stats - statistics system for a dedicated server IL2 Battle of Stalingrad.
The system is designed to collect information about the actions of the players and organize the data on a particular dedicated server.

The software is conceived, developed and supported by a team of two people (=FB=Vaal and =FB=Isay) solely as a personal initiative, ie It is not a project studio 1CGS.
The main motivation for the creation of this project wishes to develop IL-2 BOS,
create new opportunities for the community to organize multiplayer projects IL-2 BOS.
Software is free. License MIT.
The authors of the software do not give any warranty and do not bear any responsibility.


!!!!! IMPORTANT !!!!!

Algorithms collection statistics IL2 stats differs from statistics in-game. As a consequence of these statistics will not coincide with the game.
The kill count system is designed for the server with setting - finishMissionIfLanded.

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
