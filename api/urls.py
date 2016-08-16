from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from .views import *
from .stats.rankings import view as rankings_view
from .stats.weekly import view as weekly_view
from .stats.best import view as best_view

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
    url(r'stats/rankings', rankings_view),
    url(r'stats/weekly', weekly_view),
    url(r'stats/best', best_view),
    url(r'^', include(router.urls))
]
