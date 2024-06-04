from rest_framework import serializers
from users.serializers import CustomUserSerializer
from .models import Duels, Maps


class MapsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maps
        fields = '__all__'

class DuelsSerializer(serializers.ModelSerializer):
    winner = CustomUserSerializer(read_only=True)
    player_1 = serializers.SerializerMethodField()
    player_2 = serializers.SerializerMethodField()
    map_name = MapsSerializer(read_only=True)

    class Meta:
        model = Duels
        fields = (
            'id', 
            'bet', 
            'winner', 
            'player_1', 
            'player_2', 
            'created_at', 
            'started_at',
            'pending_at',
            'completed_at',
            'date',
            'time',
            'time_zone',
            'status',
            'map_name'
        )
        
    def get_player_1(self, obj):
        player = CustomUserSerializer(obj.player_1).data
        player['ready'] = obj.player_1_ready
        return player

    def get_player_2(self, obj):
        player = CustomUserSerializer(obj.player_2).data
        player['ready'] = obj.player_2_ready
        return player