from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from .models import *

class PickemsUserSerializer(serializers.ModelSerializer):
    included_serializers = {
        'teams': 'api.serializers.TeamSerializer'
    }

    teams = ResourceRelatedField(read_only=True, many=True)

    class Meta:
        model = PickemsUser
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'last_login', 'teams')

    def create(self, validated_data):
        password = self.context['request'].data.get('password')
        # call set_password on user object. Without this
        # the password will be stored in plain text.
        user = PickemsUser(**validated_data)

        # ensure lowercase email and username
        user.email = user.email.lower()
        user.username = user.username.lower()

        # encrypt the password
        user.set_password(password)
        user.save()

        return user

    def update(self, instance, validated_data):
        # do the regular update
        super(UserSerializer, self).update(instance, validated_data)

        # ensure lowercase email and username
        instance.email = instance.email.lower()
        instance.username = instance.username.lower()

        # handle the password encryption
        password = self.context['request'].data.get('password')
        if password:
            instance.set_password(password)
            update_last_login(None, instance)

        instance.save()
        return instance


class TeamSerializer(serializers.ModelSerializer):
    included_serializers = {
        'picks': 'api.serializers.TeamPickSerializer'
    }

    picks = ResourceRelatedField(read_only=True, many=True)

    class Meta:
        model = Team


class TeamPickSerializer(serializers.ModelSerializer):
    included_serializers = {
        'pick': 'api.serializers.NflStatSerializer'
    }

    pick = ResourceRelatedField(read_only=True)

    class Meta:
        model = TeamPick


class TeamPlayoffPickSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamPlayoffPick


class NflTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = NflTeam


class NflGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = NflGame


class NflPlayerSerializer(serializers.ModelSerializer):
    included_serializers = {
        'team': 'api.serializers.NflTeamSerializer'
    }

    team = ResourceRelatedField(queryset=NflTeam.objects.all())

    class Meta:
        model = NflPlayer


class NflStatSerializer(serializers.ModelSerializer):
    included_serializers = {
        'player': 'api.serializers.NflPlayerSerializer',
        'team': 'api.serializers.NflTeamSerializer'
    }

    player = ResourceRelatedField(queryset=NflPlayer.objects.all())
    team = ResourceRelatedField(queryset=NflTeam.objects.all())

    class Meta:
        model = NflStat

