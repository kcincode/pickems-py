from rest_framework.decorators import api_view
from django.http import JsonResponse
from api.models import WeekLeaders

@api_view(['GET'])
def view(request):
    data = []
    for weekly in WeekLeaders.objects.order_by('week'):
        data.append({
            'week': weekly.week,
            'team': weekly.team.name,
            'team_id': weekly.team.id,
            'team_slug': weekly.team.slug,
            'points': weekly.points
        })

    return JsonResponse(data, safe=False)
