from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class PickemsUser(User):
    class Meta:
        proxy = True

    class JSONAPIMeta:
        resource_name = 'users'


CONFERENCES = (
    ('AFC', 'AFC'),
    ('NFC', 'NFC'),
)


class NflTeam(models.Model):
    abbr = models.CharField(max_length=5, unique=True)
    conference = models.CharField(max_length=5, choices=CONFERENCES)
    city = models.CharField(max_length=50)
    name = models.CharField(max_length=50)

    class JSONAPIMeta:
        resource_name = 'nfl-teams'

    def __str__(self):
        return '{} {}-{}-{}'.format(self.city, self.name, self.abbr, self.conference)

SEASON_TYPES = (
    ('REG', 'REG'),
    ('POST', 'POST'),
)


class NflGame(models.Model):
    week = models.IntegerField()
    starts_at = models.DateTimeField()
    game_key = models.CharField(max_length=10, unique=True)
    game_id = models.CharField(max_length=15, unique=True)
    type = models.CharField(max_length=5, choices=SEASON_TYPES, default='REG')
    home_team = models.ForeignKey(NflTeam, to_field='abbr', related_name='games_home')
    away_team = models.ForeignKey(NflTeam, to_field='abbr', related_name='games_away')
    winning_team = models.ForeignKey(NflTeam, to_field='abbr', related_name='games_won', null=True, blank=True)
    losing_team = models.ForeignKey(NflTeam, to_field='abbr', related_name='games_lost', null=True, blank=True)

    class JSONAPIMeta:
        resource_name = 'nfl-games'

    def __str__(self):
        return '{} - {} vs {}'.format(self.week, self.away_team, self.home_team)


class NflPlayer(models.Model):
    team = models.ForeignKey(NflTeam, to_field='abbr', related_name="players")
    gsis_id = models.CharField(max_length=25)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=5)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('gsis_id', 'active',)

    class JSONAPIMeta:
        resource_name = 'nfl-players'

    def __str__(self):
        return '{}-{}-{}'.format(self.name, self.team.abbr, self.position)


class NflStat(models.Model):
    player = models.ForeignKey(NflPlayer, null=True, blank=True, related_name='stats')
    team = models.ForeignKey(NflTeam, to_field='abbr', null=True, blank=True, related_name='stats')
    week = models.IntegerField()
    td = models.IntegerField(default=0)
    fg = models.IntegerField(default=0)
    xp = models.IntegerField(default=0)
    two = models.IntegerField(default=0)
    diff = models.IntegerField(default=0)

    class JSONAPIMeta:
        resource_name = 'nfl-stats'

    def __str__(self):
        object = self.player if self.player else self.team
        return '{}: {}, {}, {}, {}, {}'.format(object, self.td, self.fg, self.xp, self.two, self.diff)


class Team(models.Model):
    user = models.ForeignKey(PickemsUser, related_name='teams')
    name = models.CharField(max_length=128)
    slug = models.CharField(max_length=128, unique=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    class JSONAPIMeta:
        resource_name = 'teams'

    def __str__(self):
        return '{}: {} ({})'.format(self.slug, self.user, self.paid)


class TeamPick(models.Model):
    team = models.ForeignKey(Team, related_name="picks")
    week = models.IntegerField()
    number = models.IntegerField()
    pick = models.ForeignKey(NflStat, null=True, blank=True)
    playmaker = models.BooleanField(default=False)
    valid = models.BooleanField(default=True)
    reason = models.TextField(null=True, blank=True)
    picked_at = models.DateTimeField()

    class Meta:
        unique_together = ('team', 'week', 'number',)

    class JSONAPIMeta:
        resource_name = 'team-picks'

    def __str__(self):
        return '{}: {}, {}, {}'.format(self.team, self.week, self.number, self.pick)


class TeamPlayoffPick(models.Model):
    team = models.OneToOneField(Team, related_name="playoff_picks")
    starting_points = models.IntegerField()
    picks = models.TextField()
    valid = models.BooleanField(default=True)
    reason = models.TextField(null=True, blank=True)
    picked_at = models.DateTimeField()

    class JSONAPIMeta:
        resource_name = 'team-playoff-picks'

    def __str__(self):
        return '{}: {}'.format(self.team, self.picks)


class Storyline(models.Model):
    user = models.ForeignKey(PickemsUser)
    week = models.IntegerField()
    story = models.TextField()
    posted_at = models.DateTimeField()

    class JSONAPIMeta:
        resource_name = 'storylines'

    def __str__(self):
        return '{}: {}'.format(self.week, self.story)
