from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter(trailing_slash=False)
router.register(r'users', PickemsUserViewSet)
router.register(r'teams', TeamViewSet)
# router.register(r'team-picks', TeamPickViewSet)
# router.register(r'nfl-teams', NflTeamViewSet)
# router.register(r'nfl-games', NflGameViewSet)
# router.register(r'nfl-players', NflPlayerViewSet)
# router.register(r'nfl-stats', NflStatViewSet)

urlpatterns = [
    url(r'users/current', current_user),
    url(r'picks-filter', picks_filter),
    url(r'team-picks', update_team_picks),
    url(r'picks', picks_view),
    url(r'^', include(router.urls)),
]
