import datetime
from api.models import NflGame, TeamPick, Team
from django.db.models import Q

def validate_picks(team_id):
    if not team_id.isdigit():
        team = Team.objects.get(slug=team_id)
        team_id = team.id

    picks_left = {
        'QB': 8,
        'RB': 8,
        'WRTE': 8,
        'K': 8,
        'playmakers': 2,
        'afc': 1,
        'nfc': 1
    }

    teams_picked = []
    conferences_picked = []

    now = datetime.datetime.now()

    for pick in TeamPick.objects.filter(team=team_id).order_by('week'):
        pick_type = 'player' if pick.pick and pick.pick.player else 'team'

        # clear out any errors
        pick.valid = True
        pick.reason = None

        if pick.pick.player:
            # pick is a player
            pick_type = 'player'
            position = get_position(pick.pick.player)
            team = pick.pick.player.team.abbr

            # validate pick based on game time
            game = NflGame.objects.filter(Q(home_team=pick.pick.player.team) | Q(away_team=pick.pick.player.team), week=pick.week, type='REG').first()
            if game and game.starts_at < now:
                pick.valid = False
                pick.reason = 'Your pick was after the game had started'

            # validate playmaker
            if pick.playmaker and picks_left['playmakers'] < 1:
                pick.valid = False
                pick.reason = 'No more playmaker picks left'

            if picks_left[position] < 1:
                # validate the pick by position count
                pick.valid = False
                pick.reason = 'No more {} picks left'.format(position)
            elif team in teams_picked:
                # validate the pick by team picks
                pick.valid = False
                pick.reason = 'You have already picked from {}'.format(team)

            # update counts if valid pick
            if pick.valid:
                teams_picked.append(team)
                picks_left[position] -= 1
        elif pick.pick.team:
            # pick is a team
            pick_type = 'team'
            team = pick.pick.team

            # validate pick based on game time
            game = NflGame.objects.filter(Q(home_team=team) | Q(away_team=team), week=pick.week, type='REG').first()
            if game and game.starts_at < now:
                pick.valid = False
                pick.reason = 'Your pick was after the game had started'

            # validate conference
            if team.conference in conferences_picked:
                pick.valid = False
                pick.reason = 'You have already picked from {}'.format(team.conference)

            # update counts if valid
            if pick.valid:
                conferences_picked.append(team.conference)

        pick.save()

def get_position(player):
    if player.position == 'RB' or player.position == 'FB':
        return 'RB'
    elif player.position == 'WR' or player.position == 'TE':
        return 'WRTE'
    else:
        return player.position.upper()
