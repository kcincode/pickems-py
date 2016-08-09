from rest_framework import viewsets
from .serializers import *
from .models import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.db.models import Q
from .utils.functions import validate_picks
import json
import datetime

# Create your views here.
class PickemsUserViewSet(viewsets.ModelViewSet):
    queryset = PickemsUser.objects.all()
    serializer_class = PickemsUserSerializer

    def get_permissions(self):
        # allow non-authenticated user to create via POST
        return (AllowAny() if self.request.method == 'POST' else IsAuthenticated()),


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    filter_fields = ('slug', 'user',)


# class TeamPickViewSet(viewsets.ModelViewSet):
#     queryset = TeamPick.objects.all()
#     serializer_class = TeamPickSerializer
#     filter_fields = ('week', 'team', 'team__slug', 'number')


# class TeamPlayoffPickViewSet(viewsets.ModelViewSet):
#     queryset = TeamPlayoffPick.objects.all()
#     serializer_class = TeamPlayoffPickSerializer


# class NflTeamViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = NflTeam.objects.all()
#     serializer_class = NflTeamSerializer


# class NflGameViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = NflGame.objects.all()
#     serializer_class = NflGameSerializer


# class NflPlayerViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = NflPlayer.objects.all()
#     serializer_class = NflPlayerSerializer


# class NflStatViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = NflStat.objects.all()
#     serializer_class = NflStatSerializer

@api_view()
def current_user(request):
    pickems_user = PickemsUser.objects.get(id=request.user.id)

    teams = []
    for team in pickems_user.teams.all():
        teams.append({'data': {'type': 'team', 'id': team.id}})

    data = {
        'data': {
            'id': request.user.id,
            'attributes': {
                'username': pickems_user.username,
                'first-name': pickems_user.first_name,
                'last-name': pickems_user.last_name,
                'email': pickems_user.email,
                'is_staff': pickems_user.is_staff,
            },
            'relationships': {
                'teams': teams
            }
        }
    }

    return JsonResponse(data)


@api_view()
def picks_view(request):
    week = request.GET.get('week', 1)
    slug = request.GET.get('team')

    # make sure the team is the users
    for team in request.user.teams.all():
        if slug == team.slug:
            team = slug

    if not team:
        return JsonResponse({'errors': [{'code': 400, 'title': 'You do not have access to that team'}]}, status=400)

    schedule = {}
    for game in NflGame.objects.filter(week=week).order_by('starts_at'):
        # setup the key
        day = game.starts_at.strftime('%A, %b %d %Y @ %I:%M %p')

        # create key if not already there
        try:
            schedule[day]
        except KeyError:
            schedule[day] = []

        # add the scheduled game to the correct key
        schedule[day].append({
            'starts_at': game.starts_at,
            'home': '{} {}'.format(game.home_team.city, game.home_team.name),
            'away': '{} {}'.format(game.away_team.city, game.away_team.name),
            'url': 'http://www.nfl.com/gamecenter/{}/{}/{}{}/{}@{}'.format(game.game_id, game.starts_at.year, game.type, week, game.away_team.name.lower(), game.home_team.name.lower())
        })

    pick1 = {
        'selected': None,
        'disabled': False,
        'id': None,
        'type': None,
        'valid': True,
        'reason': None,
        'playmaker': False
    }

    pick2 = {
        'selected': None,
        'disabled': False,
        'id': None,
        'type': None,
        'valid': True,
        'reason': None,
        'playmaker': False
    }

    picks_left = {
        'QB': 8,
        'RB': 8,
        'WRTE': 8,
        'K': 8,
        'playmakers': 2,
        'afc': 1,
        'nfc': 1
    }

    validate_picks(team)


    all_teams_picked = []
    team_picks = TeamPick.objects.filter(team__slug=team)
    for pick in team_picks:
        if int(pick.week) == int(week):
            if pick.pick.player:
                pick_type = 'player'
                pick_id = pick.pick.player.id
                pick_text = str(pick.pick.player)
                pick_available = pick.pick.player.team.abbr not in all_teams_picked
            elif pick.pick.team:
                pick_type = 'team'
                pick_id = pick.pick.team.id
                pick_text = str(pick.pick.team)
                pick_available = picks_left.get(pick.pick.team.conference.lower()) > 0
            else:
                pick_id = False

            if pick_id:
                pick_data = {
                    'selected': {'id': pick_id, 'text': pick_text, 'available': pick_available, 'type': pick_type},
                    'id': pick_id,
                    'type': pick_type,
                    'valid': pick_available,
                    'reason': pick.reason,
                    'playmaker': pick.playmaker,
                    'disabled': False
                }

                if pick.number == 1:
                    pick1 = pick_data
                else:
                    pick2 = pick_data

        if pick.pick.player:
            all_teams_picked.append(pick.pick.player.team.abbr)

            if pick.pick.player.position == 'RB' or pick.pick.player.position == 'FB':
                picks_left['RB'] -= 1
            elif pick.pick.player.position == 'WR' or pick.pick.player.position == 'TE':
                picks_left['WRTE'] -= 1
            else:
                picks_left[pick.pick.player.position] -= 1
        elif pick.pick.team:
            # print('team pick from {}'.format(pick.pick.team.conference.lower()))
            picks_left[pick.pick.team.conference.lower()] -= 1

        if pick.playmaker:
            picks_left['playmakers'] -= 1

    teams_picked = {'AFC': [], 'NFC': []}
    for team in NflTeam.objects.order_by('abbr'):
        teams_picked.get(team.conference).append({
            'name': '{} {}'.format(team.city, team.name),
            'abbr': team.abbr,
            'available': team.abbr not in all_teams_picked
        })

    return  JsonResponse({
        'schedule': schedule,
        'week': week,
        'pick1': pick1,
        'pick2': pick2,
        'picks_left': picks_left,
        'teams_picked': teams_picked
    })

@api_view(['GET'])
def picks_filter(request):
    term = request.GET.get('term')

    if not term:
        return JsonResponse({'errors': [{'code': 400, 'title': 'Please enter a search term'}]}, status=400)

    results = []
    for player in NflPlayer.objects.filter(Q(name__icontains=term) | Q(team__abbr__icontains=term)).order_by('name'):
        results.append({
            'id': player.id,
            'text': str(player),
            'available': True,
            'type': 'player'
        })

    for team in NflTeam.objects.filter(Q(name__icontains=term) | Q(city__icontains=term) | Q(abbr__icontains=term)).order_by('city'):
        results.append({
            'id': team.id,
            'text': str(team),
            'available': True,
            'type': 'team'
        })

    return JsonResponse(results, safe=False)

@api_view(['POST'])
def update_team_picks(request):
    post_data = request.POST.dict()

    week = post_data.get('week')
    number = post_data.get('number')
    team = post_data.get('team')
    value = json.loads(post_data.get('value', '{}'))
    playmaker = post_data.get('playmaker', False)

    if not week or not number or not team:
        return JsonResponse({'errors': [{'code': 400, 'title': 'Missing data'}]}, status=400)

    team_pick = TeamPick.objects.filter(week=week, number=number, team=team).first()
    if value:
        if value.get('type') == 'player':
            team_pick.pick.team = None
            team_pick.pick.player = NflPlayer.objects.get(id=value.get('id'))
            team_pick.playmaker = playmaker
        else:
            team_pick.pick.player = None
            team_pick.pick.team = NflTeam.objects.get(id=value.get('id'))
            team_pick.playmaker = False

        team_pick.pick.save()
    else:
        team_pick.pick.team = None
        team_pick.pick.player = None
        team_pick.pick.save()

        team_pick.playmaker = False

    # update common data
    team_pick.valid = True
    team_pick.reason = None
    team_pick.picked_at = datetime.datetime.now()
    team_pick.save()

    validate_picks(team)

    return JsonResponse({'status': 'ok'})
