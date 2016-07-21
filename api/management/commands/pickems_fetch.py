from api.models import *
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.core import management
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
import sys
import nflgame
from nflgame import update_sched
from datetime import datetime, date
import pprint

class Command(BaseCommand):
    help = 'Fetches data from the current week or all weeks'

    def add_arguments(self, parser):
        parser.add_argument('year', nargs=1, type=int)

    def handle(self, *args, **options):
        self.year = options['year'][0]
        games = NflGame.objects.filter(starts_at__gte=date.today())
        self.week = games[:1][0].week if len(games) else 1
        self.update_games()
        self.update_players()
        self.update_player_stats()

    def update_games(self):
        print('Updating games:')
        for year, phase, week in update_sched.year_phase_week(year=self.year):
            if phase != 'PRE':
                print('    {} year: {}, week: {}'.format(phase, year, week))
                try:
                    for game in nflgame.games(year, week=week, kind=phase):

                    # for game in update_sched.week_schedule(year, phase, week):
                        # format the date
                        meridiem = game.schedule.get('meridiem') if game.schedule.get('meridiem') else 'PM'
                        year = game.schedule.get('year') if game.schedule.get('month') > 7 else game.schedule.get('year') + 1
                        time_string = str(year) + '-' + str(game.schedule.get('month')) + '-' + str(game.schedule.get('day')) + ' ' + str(game.schedule.get('time')) + str(meridiem)
                        start_time = datetime.strptime(time_string, '%Y-%m-%d %I:%M%p')

                        # setup the home and away teams
                        home_team = NflTeam.objects.get(abbr=nflgame.standard_team(game.schedule.get('home')))
                        away_team = NflTeam.objects.get(abbr=nflgame.standard_team(game.schedule.get('away')))

                        try:
                            # fetch game from game key
                            gameObj = NflGame.objects.get(game_key=game.schedule.get('gamekey'))

                            # update the start time
                            if gameObj.starts_at != start_time:
                                print('        Updating start_time {}: {}'.format(gameObj.game_key, start_time))
                                gameObj.starts_at = start_time
                                gameObj.save()

                        except NflGame.DoesNotExist:
                            # convert week
                            if phase == 'REG':
                                week = game.schedule.get('week') if week > 0 else 1
                            elif phase == 'POST':
                                week = game.schedule.get('week') + 17 if week > 0 else 18

                            # print('        Creating game {}: {} vs {} at {}'.format(game.schedule.get('gamekey'), home_team, away_team, start_time))
                            # create the game
                            gameObj = NflGame.objects.create(
                                week = week,
                                starts_at = start_time,
                                game_key = game.schedule.get('gamekey'),
                                game_id = game.schedule.get('eid'),
                                type = phase,
                                home_team = home_team,
                                away_team = away_team,
                            )
                            gameObj.save()

                        # update the winning and losing teams
                        print('        {} ({}) vs {} ({})'.format(home_team, game.score_home, away_team, game.score_away))
                        if(game.score_home >= game.score_away):
                            gameObj.winning_team = home_team
                            gameObj.losing_team = away_team
                        else:
                            gameObj.losing_team = home_team
                            gameObj.winning_team = away_team

                        # save the game update
                        gameObj.save()

                        # calculate score diffs
                        home_diff = game.score_home - game.score_away
                        away_diff = game.score_away - game.score_home

                        try:
                            stat = NflStat.objects.get(week=week, team=home_team.abbr)
                        except ObjectDoesNotExist:
                            stat = NflStat.objects.create(
                                week = week,
                                td = 0,
                                two = 0,
                                xp = 0,
                                fg = 0,
                                diff = home_diff,
                                team = home_team
                            )
                            stat.save()

                        # update/create away team stats
                        try:
                            stat = NflStat.objects.get(week=week, team=away_team.abbr)
                        except ObjectDoesNotExist:
                            stat = NflStat.objects.create(
                                week = week,
                                td = 0,
                                two = 0,
                                xp = 0,
                                fg = 0,
                                diff = away_diff,
                                team = away_team
                            )
                            stat.save()
                except TypeError:
                    pass

    def update_players(self):
        print('Updating players...')

        for gsis_id in nflgame.players:
            # get the player object
            playerObj = nflgame.players[gsis_id]

            if playerObj.team and playerObj.position in ['QB', 'WR', 'TE', 'RB', 'FB', 'K']:
                # get nfl team
                team = NflTeam.objects.get(abbr=nflgame.standard_team(playerObj.team))

                try:
                    playerExists = NflPlayer.objects.get(gsis_id=playerObj.gsis_id, active=True)

                    # update team if different
                    if playerExists.team != team:
                        playerExists.team = team
                        #print('    Updating player team {}:{} ({})'.format(playerExists.gsis_id, playerExists.name, playerExists.team))
                        playerExists.save();

                except ObjectDoesNotExist:
                    # convert position
                    position = playerObj.position
                    if playerObj.position == 'FB':
                        position = 'RB'

                    # add player
                    player = NflPlayer.objects.create(
                        team = team,
                        gsis_id = playerObj.gsis_id,
                        name = playerObj.full_name,
                        position = position,
                        active = True
                    )
                    player.save()
                    #print('    Added player {}:{} ({})'.format(playerExists.gsis_id, playerExists.name, playerExists.team))

        for player in NflPlayer.objects.all():
            # if the player has no team
            if not nflgame.players[player.gsis_id].team:
                #print('    Deactivated player {}:{} ({})'.format(playerExists.gsis_id, playerExists.name, playerExists.team))
                player.active = False
                player.save()

    def update_player_stats(self):
        print('Updating player stats...')

        for year, phase, week in update_sched.year_phase_week(year=self.year):
            if phase != 'PRE':
                print('    {} year: {}, week: {}'.format(phase, year, week))
                try:
                    games = nflgame.games(year, week, kind=phase)
                    real_week = week + 17 if phase == 'POST' else week
                    if len(games):
                        players = nflgame.combine_game_stats(games)

                        for player in players:
                            if player.player:
                                try:
                                    playerObj = NflPlayer.objects.get(gsis_id=player.player.player_id, active=True)
                                except ObjectDoesNotExist:
                                    #print('        Did not find {}: {}'.format(player.player.player_id, player))
                                    continue

                                try:
                                    stat = NflStat.objects.get(week=real_week, player=playerObj)
                                    # if player.player.player_id == '00-0026138':
                                    # if phase == 'POST':
                                    #     print('        Updating {}'.format(stat))
                                    # update the stat data
                                    stat.td = player.tds
                                    stat.fg = player.kicking_fpm
                                    stat.two = player.twoptm
                                    stat.xp = player.kicking_xpmade
                                    stat.diff = 0
                                    # if player.player.player_id == '00-0026138':
                                    #     print('    updating {}'.format(stat))
                                    stat.save()
                                except ObjectDoesNotExist:
                                    # create the stat
                                    # if player.player.player_id == '00-0026138':
                                    # if phase == 'POST':
                                    #     print('    Creating stat for {} {}'.format(week, player.player.player_id))
                                    stat = NflStat.objects.create(
                                        week = real_week,
                                        td = player.tds,
                                        fg = player.kicking_fgm,
                                        xp = player.kicking_xpmade,
                                        two = player.twoptm,
                                        diff = 0,
                                        player = playerObj
                                    )
                                    # if player.player.player_id == '00-0026138':
                                    #     print('    creating {}'.format(stat))
                                    stat.save()
                except TypeError:
                    # needed for nflgame not pulling post season data correctly
                    pass

