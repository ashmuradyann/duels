from django.contrib import admin
from .models import Duels, Maps
from .forms import DuelForm

@admin.register(Duels)
class DuelsAdmin(admin.ModelAdmin):
    list_display = ['pk', 'player_1_ready', 'player_2_ready', 'bet', 'date', 'time', 'time_zone', 'status', 'player_1', 'player_2', 'winner', 'player_1_is_winner', 'player_2_is_winner']
    list_display_links = ['pk']
    search_fields = ['bet', 'date', 'time', 'time_zone', 'status']
    list_filter = ['status', 'created_at']
    list_editable = ['status', 'winner']
    readonly_fields = ['created_at', 'started_at', 'completed_at']
    form = DuelForm
    
    fieldsets = (
        ('Duel Info', {
            'fields': ('map_name', 'bet', 'date', 'time', 'time_zone')
        }),
        ('Players', {
            'fields': ('player_1', 'player_2', 'winner')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'started_at', 'completed_at')
        }),
    )
    
    
@admin.register(Maps)
class MapsAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'image']
    list_display_links = ['pk', 'name']
    search_fields = ['name', 'image']
    list_filter = ['name']
    list_editable = ['image']
    
    fieldsets = (
        ('Map Info', {
            'fields': ('name', 'image')
        }),
    )