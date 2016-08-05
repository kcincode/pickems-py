from rest_framework import viewsets
from .serializers import *
from .models import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response

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


class TeamPickViewSet(viewsets.ModelViewSet):
    queryset = TeamPick.objects.all()
    serializer_class = TeamPickSerializer
    filter_fields = ('week', 'team')


class TeamPlayoffPickViewSet(viewsets.ModelViewSet):
    queryset = TeamPlayoffPick.objects.all()
    serializer_class = TeamPlayoffPickSerializer


class NflTeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NflTeam.objects.all()
    serializer_class = NflTeamSerializer


class NflGameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NflGame.objects.all()
    serializer_class = NflGameSerializer


class NflPlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NflPlayer.objects.all()
    serializer_class = NflPlayerSerializer


class NflStatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NflStat.objects.all()
    serializer_class = NflStatSerializer

@api_view()
def current_user(request):
    pickems_user = PickemsUser.objects.get(id=request.user.id)
    return Response(PickemsUserSerializer(pickems_user).data)
