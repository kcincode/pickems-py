from api.models import *
from django.core.management.base import BaseCommand
from django.core import management
import nflgame
from nflgame import update_sched
from datetime import datetime

class Command(BaseCommand):
    help = 'Initializes the database with the starting data'

    def add_arguments(self, parser):
        parser.add_argument('year', nargs=1, type=int)

    def handle(self, *args, **options):
        self.year = options['year'][0]
        self.cleanDatabase()
        self.createAdminUser()
        self.importTeams()
        management.call_command('pickems_fetch', str(self.year))
        # self.importGames()
        # self.importPlayers()
        print('Finished.')

    def cleanDatabase(self):
        management.call_command('migrate')
        management.call_command('flush')


    def createAdminUser(self):
        print('Creating the admin user')
        user = PickemsUser.objects.create_user(
            username='admin',
            email='admin@felicelli.com',
            password='testing',
            first_name = 'System',
            last_name = 'Administrator'
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()

    def importTeams(self):
        print('Importing teams.')
        teams = (
            {'abbr': 'ARI', 'city': 'Arizona', 'name': 'Cardinals', 'conference': 'NFC'},
            {'abbr': 'ATL', 'city': 'Atlanta', 'name': 'Falcons', 'conference': 'NFC'},
            {'abbr': 'BAL', 'city': 'Baltimore', 'name': 'Ravens', 'conference': 'AFC'},
            {'abbr': 'BUF', 'city': 'Buffalo', 'name': 'Bills', 'conference': 'AFC'},
            {'abbr': 'CAR', 'city': 'Carolina', 'name': 'Panthers', 'conference': 'NFC'},
            {'abbr': 'CHI', 'city': 'Chicago', 'name': 'Bears', 'conference': 'NFC'},
            {'abbr': 'CIN', 'city': 'Cincinnati', 'name': 'Bengals', 'conference': 'AFC'},
            {'abbr': 'CLE', 'city': 'Cleveland', 'name': 'Browns', 'conference': 'AFC'},
            {'abbr': 'DAL', 'city': 'Dallas', 'name': 'Cowboys', 'conference': 'NFC'},
            {'abbr': 'DEN', 'city': 'Denver', 'name': 'Broncos', 'conference': 'AFC'},
            {'abbr': 'DET', 'city': 'Detroit', 'name': 'Lions', 'conference': 'NFC'},
            {'abbr': 'GB', 'city': 'Green Bay', 'name': 'Packers', 'conference': 'NFC'},
            {'abbr': 'HOU', 'city': 'Houston', 'name': 'Texans', 'conference': 'AFC'},
            {'abbr': 'IND', 'city': 'Indianapolis', 'name': 'Colts', 'conference': 'AFC'},
            {'abbr': 'JAC', 'city': 'Jacksonville', 'name': 'Jaguars', 'conference': 'AFC'},
            {'abbr': 'KC', 'city': 'Kansas City', 'name': 'Chiefs', 'conference': 'AFC'},
            {'abbr': 'MIA', 'city': 'Miami', 'name': 'Dolphins', 'conference': 'AFC'},
            {'abbr': 'MIN', 'city': 'Minnesota', 'name': 'Vikings', 'conference': 'NFC'},
            {'abbr': 'NE', 'city': 'New England', 'name': 'Patriots', 'conference': 'AFC'},
            {'abbr': 'NO', 'city': 'New Orleans', 'name': 'Saints', 'conference': 'NFC'},
            {'abbr': 'NYG', 'city': 'New York', 'name': 'Giants', 'conference': 'NFC'},
            {'abbr': 'NYJ', 'city': 'New York', 'name': 'Jets', 'conference': 'AFC'},
            {'abbr': 'OAK', 'city': 'Oakland', 'name': 'Raiders', 'conference': 'AFC'},
            {'abbr': 'PHI', 'city': 'Philadelphia', 'name': 'Eagles', 'conference': 'NFC'},
            {'abbr': 'PIT', 'city': 'Pittsburgh', 'name': 'Steelers', 'conference': 'AFC'},
            {'abbr': 'SD', 'city': 'San Diego', 'name': 'Chargers', 'conference': 'AFC'},
            {'abbr': 'SEA', 'city': 'Seattle', 'name': 'Seahawks', 'conference': 'NFC'},
            {'abbr': 'SF', 'city': 'San Francisco', 'name': '49ers', 'conference': 'NFC'},
            {'abbr': 'STL', 'city': 'St. Louis', 'name': 'Rams', 'conference': 'NFC'},
            {'abbr': 'TB', 'city': 'Tampa Bay', 'name': 'Buccaneers', 'conference': 'NFC'},
            {'abbr': 'TEN', 'city': 'Tennessee', 'name': 'Titans', 'conference': 'AFC'},
            {'abbr': 'WAS', 'city': 'Washington', 'name': 'Redskins', 'conference': 'NFC'},
        )

        for team in teams:
            teamObj = NflTeam.objects.create(
                abbr = team.get('abbr'),
                city = team.get('city'),
                name = team.get('name'),
                conference = team.get('conference')
            )
            teamObj.save()
