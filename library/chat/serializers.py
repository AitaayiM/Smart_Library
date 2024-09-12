from rest_framework import serializers
from .models import Message, Visibility

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'