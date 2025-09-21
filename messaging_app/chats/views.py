from rest_framework import viewsets, status, filters   # 👈 added filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversations:
    - List conversations
    - Create new conversations
    - Retrieve a specific conversation
    """

    queryset = Conversation.objects.all().prefetch_related("participants", "messages")
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter]   # 👈 added
    search_fields = ["participants__email"]    # example field, adjust if needed

    def create(self, request, *args, **kwargs):
        participants = request.data.get("participants", [])
        if not participants or len(participants) < 2:
            return Response(
                {"error": "A conversation must have at least 2 participants."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Messages:
    - List messages
    - Create messages inside a conversation
    """

    queryset = Message.objects.all().select_related("sender", "conversation")
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter]   # 👈 added
    search_fields = ["message_body"]           # example field

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get("conversation")
        sender_id = request.data.get("sender")
        message_body = request.data.get("message_body")

        if not conversation_id or not sender_id or not message_body:
            return Response(
                {"error": "conversation, sender, and message_body are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation = get_object_or_404(Conversation, id=conversation_id)

        message = Message.objects.create(
            conversation=conversation,
            sender_id=sender_id,
            message_body=message_body,
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
