from rest_framework.decorators import api_view
from django.http import JsonResponse
from api.models import TeamRankings
import math


@api_view(['GET'])
def view(request):
    data = {
        'gold': [],
        'silver': [],
        'bronze': []
    }

    for ranking in TeamRankings.objects.order_by('rank'):
        data[ranking.category].append({
            'rank': ranking.rank,
            'team': ranking.team.name,
            'team_id': ranking.team.id,
            'team_slug': ranking.team.slug,
            'points': ranking.points,
            'wl': ranking.team.wl.get().wl,
            'playoff': ranking.playoff,
        })

    return JsonResponse(data)
