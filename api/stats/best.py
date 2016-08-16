from rest_framework.decorators import api_view
from django.http import JsonResponse
from api.models import BestPossible
from django.forms.models import model_to_dict
import json

@api_view(['GET'])
def view(request):
    results = []
    overall_total = 0

    for best in BestPossible.objects.order_by('week').all():
        results.append({
            'week': best.week,
            'pick1': str(best.pick1.player) if best.pick1.player else str(best.pick1.team),
            'pick1_points': best.pick1_points,
            'pick1_playmaker': best.pick1_playmaker,
            'pick2': str(best.pick2.player) if best.pick2.player else str(best.pick2.team),
            'pick2_points': best.pick2_points,
            'pick2_playmaker': best.pick2_playmaker,
            'total': best.total
        })

        overall_total += best.total

    results.append({
        'week': 18,
        'pick1': None,
        'pick1_points': None,
        'pick1_playmaker': None,
        'pick2': None,
        'pick2_points': None,
        'pick2_playmaker': None,
        'total': overall_total
    })

    return JsonResponse(results, safe=False)
