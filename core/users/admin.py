from django.contrib import admin
from django.db.models import Count, Q, F
from duels.models import Duels
from .models import CustomUser, Report

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'username', 
        'first_name', 
        'last_name', 
        'auth_type',
        'balance', 
        'leaves',
        'total_completed_duels',
        'total_wins',
        'total_losses',
        'accepted_reports',
        'last_duel',
    ]
    search_fields = ['username', 'first_name', 'last_name']
    list_filter = ['created_at',]
    readonly_fields = [
        'total_completed_duels', 
        'total_wins', 
        'total_losses', 
        'last_duel', 
        'created_at', 
        'accepted_reports', 
        'password'
    ]
    
    fieldsets = (
        ('User Info', {
            'fields': ('username', 'first_name', 'last_name', 'photo', 'auth_type', 'email')
        }),
        ('Duel And Balance', {
            'fields': ('balance', 'total_completed_duels', 'total_wins', 'total_losses', 'last_duel', 'accepted_reports', 'leaves')
        }),
        ('Time Stamps', {
            'fields': ('created_at',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')    
        }),
    )
                
    def total_completed_duels(self, obj):
        return Duels.objects.filter(Q(player_1=obj) | Q(player_2=obj), status='completed').count()
    
    def total_wins(self, obj):
        return Duels.objects.filter(winner=obj, status='completed').count()
    
    def total_losses(self, obj):
        return Duels.objects.filter(Q(player_1=obj) | Q(player_2=obj), status='completed').exclude(winner=obj).count()
    
    def last_duel(self, obj):
        last = Duels.objects.filter(Q(player_1=obj) | Q(player_2=obj), status='completed').order_by('-created_at').first()
        return last.completed_at if last else '--'
    
    def accepted_reports(self, obj):
        return ''

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'reported_user', 'report_type', 'result_type', 'created_at']
    list_editable = ['result_type', 'report_type']
    list_filter = ['report_type', 'result_type']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['user', 'reported_user']