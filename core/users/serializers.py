from rest_framework import serializers
from django.db.models import Q
from duels.models import Duels
from .models import CustomUser, Report, UserQuestions


class CustomUserSerializer(serializers.ModelSerializer):
    win_count = serializers.SerializerMethodField()
    lose_count = serializers.SerializerMethodField()
    total_finished_duels = serializers.SerializerMethodField()
    last_four_duels = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'photo', 'balance', 'win_count', 'lose_count', 'total_finished_duels', 'last_four_duels', 'leaves']

    def get_win_count(self, obj):
        return Duels.objects.filter(winner=obj, status='finished').count()

    def get_lose_count(self, obj):
        return Duels.objects.filter(~Q(winner=obj), status='finished').count()

    def get_total_finished_duels(self, obj):
        return Duels.objects.filter(status='finished').count()

    def get_last_four_duels(self, obj):
        duels = Duels.objects.filter(Q(player_1=obj) | Q(player_2=obj)).exclude(status__in=['open', 'pending', 'canceled']).order_by('-date')[:4]
        return [{'id': duel.id, 'winner': duel.winner.username if duel.winner else None, 'status': duel.status} for duel in duels]


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['user', 'reported_user', 'report_type', 'description']
        
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuestions
        fields = ['user', 'question', 'answer', 'question_type']