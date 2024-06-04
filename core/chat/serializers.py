from rest_framework.serializers import ModelSerializer
from .models import Chats, Messages

class MessagesSerializer(ModelSerializer):
    class Meta:
        model = Messages
        fields = '__all__'
        
class ChatsSerializer(ModelSerializer):
    class Meta:
        model = Chats
        fields = '__all__'