from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
import nflgame
from nflgame import update_sched
from datetime import datetime, date
import sys
from django.db import connection
from django.contrib.auth.models import User
from api.models import *
import random
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Populates the database with test data'
    playmakers_left = 2
    positions_left = {
        'QB': 8,
        'RB': 8,
        'WRTE': 8,
        'K': 8,
    }
    teams_left = {
        'AFC': 1,
        'NFC': 1,
    }
    used_conferences = []
    used_teams = []

    def handle(self, *args, **options):
        random.seed()
        self.clear_database()
        self.create_users_and_teams()
        self.make_regular_season_picks()
        # self.make_post_season_picks()

    def create_users_and_teams(self):
        sys.stdout.write('Creating users with teams')
        self.show_progress()
        team_number = 1
        for i in xrange(1, 25):
            # self.show_progress()
            # print('    Creating user testuser' + str(i))
            user = User(
                username='testuser' + str(i),
                first_name='Test' + str(i),
                last_name='User' + str(i),
                email='testuser' + str(i) + '@example.com',
            )
            user.set_password('testing' + str(i))
            user.save()

            for j in xrange(1, random.randrange(2, 4)):
                # self.show_progress()
                # print('        Creating team #' + str(team_number))
                team = Team(
                    user=user,
                    name='Test Team #' + str(team_number),
                    slug='test-team-' + str(team_number),
                    paid=random.choice([True, False])
                );
                team.save()
                team_number += 1

            self.show_progress()

        print('Done.')

    def make_regular_season_picks(self):
        print('Making team picks:')
        for team in Team.objects.all():
            sys.stdout.write('    Making picks for ' + str(team.name))
            self.show_progress()

            self.playmakers_left = 2
            self.positions_left = {
                'QB': 8,
                'RB': 8,
                'WRTE': 8,
                'K': 8,
            }
            self.teams_left = {
                'AFC': 1,
                'NFC': 1,
            }
            self.used_conferences = []
            self.used_teams = []

            for week in xrange(1, 18):
                self.show_progress()

                for number in xrange(1, 3):
                    self.make_pick(team, week, number)

            print('Done')

        print('Done')

    def make_pick(self, team, week, number):
        random.seed()

        first_game = NflGame.objects.filter(week=week).order_by('starts_at').first()
        pick_date_time = first_game.starts_at - timedelta(days=2)
        # print('    Team: {}, Week: {}, Number: {}'.format(team.id, week, number))

        can_pick_teams = bool([conference for conference in self.teams_left.values() if conference != 0])
        can_pick_players = bool([position for position in self.positions_left.values() if position != 0])
        can_pick_playmaker = bool(self.playmakers_left > 0)

        playmaker = True if can_pick_playmaker and random.randint(0, 100) > 60 else False

        if not can_pick_players and not can_pick_teams:
            print('positions')
            print(positions_left)
            print('teams')
            print(teams_left)
            raise('Still expecting a pick but no picks available')
        elif not can_pick_teams:
            # only pick from players
            pick_type = 'player'
        elif not can_pick_players:
            # only pick from teams
            pick_type = 'team'
        else:
            # pick from either teams or players
            pick_type = 'player' if random.randint(0, 100) > 60 else 'team'

        if pick_type == 'player':
            position_key = random.choice([position for position in self.positions_left.keys() if self.positions_left[position] > 0])
            if position_key == 'WRTE':
                position = ['WR', 'TE']
            elif position_key == 'RB':
                position = ['RB', 'FB']
            else:
                position = [position_key]


            # make a player pick
            nfl_player = NflPlayer.objects.exclude(team__abbr__in=self.used_teams).filter(position__in=position).order_by('?').first()
            # print(    '    Selecting ' + str(nfl_player))

            self.positions_left[position_key] -= 1
            self.used_teams.append(nfl_player.team.abbr)

            try:
                pick = NflStat.objects.get(week=week, player=nfl_player)
            except ObjectDoesNotExist:
                pick = NflStat.objects.create(
                    week = week,
                    td = 0,
                    two = 0,
                    xp = 0,
                    fg = 0,
                    diff = 0,
                    player = nfl_player
                )
                pick.save()
        else:
            playmaker = False
            #make a team pick
            nfl_team = NflTeam.objects.exclude(conference__in=self.used_conferences).order_by('?').first()
            # print(    '    Selecting ' + str(nfl_team))

            self.teams_left[nfl_team.conference] -= 1
            self.used_conferences.append(nfl_team.conference)

            try:
                pick = NflStat.objects.get(week=week, team=nfl_team)
            except ObjectDoesNotExist:
                pick = NflStat.objects.create(
                    week = week,
                    td = 0,
                    two = 0,
                    xp = 0,
                    fg = 0,
                    diff = 0,
                    team = nfl_team
                )
                pick.save()

        if not pick:
            print('positions')
            print(positions_left)
            print('teams')
            print(teams_left)
            raise('No pick was made for some reason')

        pick.save()

        if playmaker:
            self.playmakers_left -= 1


        teamPick = TeamPick(
            team=team,
            week=week,
            number=number,
            playmaker=playmaker,
            valid=True,
            reason='',
            picked_at=pick_date_time,
            pick=pick
        )
        teamPick.save()

    def create_storylines(self):
        user = PickemsUser.objects.get(id=1)

        for week in range(1, 18):
            week_game = NflGame.objects.filter(week=week).order_by('starts_at').first()
            posted_date = week_game.starts_at - timedelta(days=2)

            Storyline.objects.create(
                user=user,
                week=week,
                story='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean at malesuada tellus, sed aliquet velit. Proin cursus metus eros, ac vehicula lorem lobortis nec. Etiam mollis urna risus, eget faucibus nulla commodo eget. Vestibulum auctor semper nibh et iaculis. Vestibulum aliquam varius lorem, id porttitor risus cursus eu. Maecenas dictum ut dolor condimentum euismod. Integer lectus orci, aliquet vitae lobortis et, fringilla eu ante. Curabitur venenatis urna ligula, et dignissim neque volutpat eu. Cras in lacus aliquam, euismod orci a, tincidunt eros. Praesent urna tortor, luctus vitae ex eget, euismod vestibulum ex. Phasellus interdum cursus diam, at mattis odio fermentum sit amet.',
                posted_at=posted_date
            )

    def show_progress(self):
        sys.stdout.write('.')
        sys.stdout.flush()

    def clear_database(self):
        sys.stdout.write('Clearing database tables')
        self.show_progress()

        cursor = connection.cursor()
        TeamPlayoffPick.objects.all().delete()
        self.show_progress()
        cursor.execute('ALTER SEQUENCE api_teamplayoffpick_id_seq RESTART WITH 1')
        self.show_progress()

        TeamPick.objects.all().delete()
        self.show_progress()
        cursor.execute('ALTER SEQUENCE api_teampick_id_seq RESTART WITH 1')
        self.show_progress()

        Team.objects.all().delete()
        self.show_progress()
        cursor.execute('ALTER SEQUENCE api_team_id_seq RESTART WITH 1')
        self.show_progress()

        User.objects.filter(id__gt=1).delete()
        self.show_progress()
        cursor.execute('ALTER SEQUENCE auth_user_id_seq RESTART WITH 2')
        self.show_progress()

        Storyline.objects.all().delete()
        self.show_progress()
        cursor.execute('ALTER SEQUENCE api_storyline_id_seq RESTART WITH 1')
        self.show_progress()

        print('Done.')

