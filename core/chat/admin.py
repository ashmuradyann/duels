from django.contrib import admin


from .models import Chats, Messages


@admin.register(Chats)
class ChatsAdmin(admin.ModelAdmin):
    list_display = ['id', 'duel', 'player', 'admin', 'created_at', 'updated_at']
    list_display_links = ['id', 'duel']
    list_filter = ['duel']
    search_fields = ['duel', 'player', 'admin']
    list_per_page = 25
    

@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat', 'user', 'message', 'created_at', 'updated_at']
    list_display_links = ['id', 'chat']
    list_filter = ['chat', 'user']
    search_fields = ['chat', 'user', 'message']
    list_per_page = 25
