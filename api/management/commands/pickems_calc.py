from django.core.management.base import BaseCommand
from api.models import NflGame, Team, TeamWinLoss, TeamRankings, WeekLeaders, TeamPick, BestPossible, NflStat, NflTeam
from django.db import connection
import sys
from api.utils.functions import team_points, stat_points, pick_points, get_position
import math
import json
import datetime

def sort_teams(a, b):
    if a.get('points') == b.get('points'):
        return -1 if a.get('wl') > b.get('wl') else 1
    else:
        return -1 if a.get('points') > b.get('points') else 1

def sort_weekly_leaders(a, b):
    return -1 if a.get('score') > b.get('score') else 1

def week_sorting(a, b):
    return -1 if a.get('week') > b.get('week') else 1


class Command(BaseCommand):
    help = 'Regenerates the calculated fields'

    def handle(self, *args, **options):
        closest_game = NflGame.objects.filter(starts_at__gte=datetime.datetime.now()).first()
        up_to_week = closest_game.week if closest_game else 18

        self.calculateWinLoss(up_to_week)
        self.calculateRankings(up_to_week)
        self.calculateWeeklyLeaders(up_to_week)
        self.calculateBestPossiblePicks(up_to_week)

    def show_progress(self):
        sys.stdout.write('.')
        sys.stdout.flush()

    # calculate all win/losses per nfl team
    def calculateWinLoss(self, up_to_week):
        sys.stdout.write('Calculating W/L ratios')
        nfl_teams= {}
        for nfl_game in NflGame.objects.all():
            winning_team = nfl_game.winning_team.abbr
            losing_team = nfl_game.losing_team.abbr

            # create the object if it doesn't exist
            if winning_team not in nfl_teams:
                nfl_teams[winning_team] = {
                    'w': 0,
                    'l': 0
                }

            # create the object if it doesn't exist
            if losing_team not in nfl_teams:
                nfl_teams[losing_team] = {
                    'w': 0,
                    'l': 0
                }

            nfl_teams[winning_team]['w'] += 1
            nfl_teams[losing_team]['l'] += 1

        # clear ratios for teams
        cursor = connection.cursor()
        TeamWinLoss.objects.all().delete()
        cursor.execute('ALTER SEQUENCE api_teamwinloss_id_seq RESTART WITH 1')

        for team in Team.objects.all():
            self.show_progress()
            # generate the teams picked
            picked_teams = []
            for pick in team.picks.all():
                if pick.pick.player:
                    picked_teams.append(pick.pick.player.team.abbr)
                elif pick.pick.team:
                    picked_teams.append(pick.pick.team.abbr)

            win_loss = {'w': 0, 'l': 0}
            for wl_team in nfl_teams:
                # add the w's and l's
                if wl_team not in picked_teams:
                    win_loss['w'] += nfl_teams[wl_team]['w']
                    win_loss['l'] += nfl_teams[wl_team]['l']

            # calculate ration for team
            win_loss_ratio = win_loss['w'] / win_loss['l'] if win_loss['w'] > 0 else 0.000
            team_win_loss = TeamWinLoss.objects.create(
                team=team,
                wl=win_loss_ratio
            )
        print('Done.')

    def calculateRankings(self, up_to_week):
        sys.stdout.write('Calculating Rankings')
        # clear ratios for teams
        cursor = connection.cursor()
        TeamRankings.objects.all().delete()
        cursor.execute('ALTER SEQUENCE api_teamrankings_id_seq RESTART WITH 1')

        teams = {
            'paid': [],
            'not-paid': []
        }

        for team in Team.objects.all():
            self.show_progress()
            data = {
                'team': team,
                'points': team_points(team, up_to_week),
                'playoffs': 0
            }

            if team.paid:
                teams['paid'].append(data)
            else:
                teams['not-paid'].append(data)

        teams['paid'] = sorted(teams['paid'], cmp=sort_teams)
        teams['not-paid'] = sorted(teams['not-paid'], cmp=sort_teams)

        gold = int(math.ceil(len(teams['paid']) / 2))

        # insert gold
        rank = 1
        gold_length = len(teams['paid'][0:gold])
        for team in teams['paid'][0:gold]:
            playoff = (gold_length - rank) * 6
            TeamRankings.objects.create(
                rank=rank,
                category='gold',
                team=team['team'],
                points=team['points'],
                playoff=playoff
            )

            rank += 1


        # insert silver
        rank = 1
        silver_length = len(teams['paid'][gold:])
        for team in teams['paid'][gold:]:
            playoff = (silver_length - rank) * 6
            TeamRankings.objects.create(
                rank=rank,
                category='silver',
                team=team['team'],
                points=team['points'],
                playoff=playoff
            )

            rank += 1

        # insert bronze
        rank = 1
        bronze_length = len(teams['not-paid'])
        for team in teams['not-paid']:
            playoff = (bronze_length - rank) * 6
            TeamRankings.objects.create(
                rank=rank,
                category='bronze',
                team=team['team'],
                points=team['points'],
                playoff=playoff
            )

            rank += 1

        print('Done.')

    def calculateWeeklyLeaders(self, up_to_week):
        sys.stdout.write('Calculating Weekly Leaders')

        # clear ratios for teams
        cursor = connection.cursor()
        WeekLeaders.objects.all().delete()
        cursor.execute('ALTER SEQUENCE api_weekleaders_id_seq RESTART WITH 1')

        for week in range(1, up_to_week):
            self.show_progress()
            team_picks = {}
            for pick in TeamPick.objects.filter(week=week):
                if pick.team.slug not in team_picks.keys():
                    team_picks[pick.team.slug] = {'team': pick.team, 'score': pick_points(pick)}
                else:
                    team_picks[pick.team.slug]['score'] += pick_points(pick)

            team_pick_list = []
            for slug in team_picks:
                team_pick_list.append(team_picks[slug])

            team_pick_list = sorted(team_pick_list, cmp=sort_weekly_leaders)
            WeekLeaders.objects.create(
                week=week,
                team=team_pick_list[0]['team'],
                points=team_pick_list[0]['score']
            )

        print('Done.')

    def calculateBestPossiblePicks(self, up_to_week):
        sys.stdout.write('Calculating Best Picks')

        # clear ratios for teams
        cursor = connection.cursor()
        BestPossible.objects.all().delete()
        cursor.execute('ALTER SEQUENCE api_bestpossible_id_seq RESTART WITH 1')

        data = {}

        picks_left = {
            'QB': 8,
            'RB': 8,
            'WRTE': 8,
            'K': 8,
            'playmakers': 2,
            'afc': 1,
            'nfc': 1,
        }
        teams_picked = []
        all_data = []

        # loop through all stats
        self.show_progress()
        for stat in NflStat.objects.filter(week__lt=up_to_week):
            # get pick type
            pick_type = 'team' if stat.team else 'player'

            # generate data
            pick_data = {
                'week': stat.week,
                'type': pick_type,
                'object': stat,
                'playmaker': False,
                'name': str(stat.team) if stat.team else str(stat.player),
                'conference': stat.team.conference.lower() if stat.team else None,
                'position': None if stat.team else get_position(stat.player),
                'team': stat.team.abbr if stat.team else stat.player.team.abbr,
                'score': stat_points(stat, False)
            }

            if pick_data['score'] >= 0:
                all_data.append(pick_data)

        # sort by score
        self.show_progress()
        all_data = sorted(all_data, cmp=sort_weekly_leaders)

        self.show_progress()
        # print('')
        for pick in all_data:
            # generate the week key
            week_key = 'week{}'.format(pick['week'])

            # create the week key if it doesn't exist
            if week_key not in data:
                data[week_key] = []

            # if week_key == 'week10' and picks_left['RB'] == 1:
            #     print(pick)

            # if all picks are made then exit
            if all(value == 0 for value in picks_left.values()):
                break

            # continue if picks are already made for this week
            if len(data[week_key]) >= 2:
                continue

            # print('{}: {}pts, week {}'.format(pick['name'], pick['score'], pick['week']))

            if pick['type'] == 'team' and picks_left[pick['conference']] > 0:
                picks_left[pick['conference']] -= 1

                # set the team pick
                data[week_key].append(pick)
                # print('Picking {}: {} -- {}'.format(week_key, pick['name'], picks_left))
                # print(NflTeam.objects.exclude(abbr__in=teams_picked).values_list('abbr'))
                # print('---------------------------------------')
                self.show_progress()
            elif pick['type'] == 'player' and picks_left[pick['position']] > 0 and pick['team'] not in teams_picked:
                picks_left[pick['position']] -= 1
                teams_picked.append(pick['team'])

                if picks_left['playmakers'] > 0:
                    picks_left['playmakers'] -= 1
                    pick['playmaker'] = True
                    pick['score'] *= 2

                data[week_key].append(pick)
                # print('Picking {}: {} -- {}'.format(week_key, pick['name'], picks_left))
                # print(NflTeam.objects.exclude(abbr__in=teams_picked).values_list('abbr'))
                # print('---------------------------------------')
                self.show_progress()

        # print('---------------------------------------')
        # print('---------------------------------------')

        # insert the data for the weeks
        for week_key in data:
            # print('DATA {}: {}'.format(week_key, len(data[week_key])))
            BestPossible.objects.create(
                week=data[week_key][0]['week'],
                pick1=data[week_key][0]['object'],
                pick1_points=data[week_key][0]['score'],
                pick1_playmaker= data[week_key][0]['playmaker'],
                pick2=data[week_key][1]['object'],
                pick2_points=data[week_key][1]['score'],
                pick2_playmaker= data[week_key][0]['playmaker'],
                total=data[week_key][0]['score'] + data[week_key][1]['score']
            )

        print('Done.')
