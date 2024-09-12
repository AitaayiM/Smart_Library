from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Message, Visibility
from .serializers import MessageSerializer
from personality.models import Personal, Friendship
from django.db.models import Q
from identity.models import Roles
from identity.utils import role_required
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MessageFilter


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def get_queue_token(request):
    personal = Personal.objects.get(user=request.user)
    receiver_id = request.data.get('receiver_id')

    try:
        receiver = Personal.objects.get(id=receiver_id)
        friendship_sender = Friendship.objects.filter(personal=personal, friend=receiver).first()
        friendship_receiver = Friendship.objects.filter(personal=receiver, friend=personal).first()

        # Check if they are friends
        if not (friendship_sender and friendship_receiver):
            return Response({'detail': 'Not friends'}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            "queue_token_sender": friendship_sender.queue_token,
            "queue_token_receiver": friendship_receiver.queue_token
        }, status=status.HTTP_200_OK)
    except Personal.DoesNotExist:
        return Response({'detail': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def send_message(request):
    personal = Personal.objects.get(user=request.user)
    receiver_id = request.data.get('receiver_id')
    data = request.data

    try:
        receiver = Personal.objects.get(id=receiver_id)

        # Check if they are friends
        if not Friendship.objects.filter(personal=personal, friend=receiver).exists() and \
           not Friendship.objects.filter(personal=receiver, friend=personal).exists():
            return Response({'detail': 'Not friends'}, status=status.HTTP_403_FORBIDDEN)
        
        # Add sender and receiver to the data
        data = data.copy()
        # inverse this ids for saved it after receiving
        data['sender'] = receiver.id
        data['receiver'] = personal.id

        serializer = MessageSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            Visibility.objects.create(message=serializer.instance, personal=personal)
            Visibility.objects.create(message=serializer.instance, personal=receiver)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Personal.DoesNotExist:
        return Response({'detail': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def reply_to_message(request, message_id):
    try:
        personal = Personal.objects.get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'details':'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    parent_message = get_object_or_404(Message, id=message_id)
    data = request.data.copy()
    data['sender'] = personal.id
    data['receiver'] = parent_message.sender.id  # Assuming reply goes back to the original sender
    data['parent_message'] = parent_message.id

    serializer = MessageSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        Visibility.objects.create(message=serializer.instance, personal=personal)
        Visibility.objects.create(message=serializer.instance, personal=parent_message.sender)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def update_message(request, message_id):
    try:
        personal = Personal.objects.get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    message = get_object_or_404(Message, id=message_id)

    if message.receiver != personal:
        return Response({'detail': 'Not authorized to update this message'}, status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    data['sender'] = personal.id  # Ensure the sender is the current user
    serializer = MessageSerializer(message, data=data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def delete_message(request, message_id):
    try:
        personal = Personal.objects.get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    message = get_object_or_404(Message, id=message_id)

    action = request.data.get('action', 'delete_for_self')  # Default to 'delete_for_self'

    if action == 'delete_for_everyone':
        # Only the sender or receiver can delete the message for everyone
        if message.sender != personal and message.receiver != personal:
            return Response({'detail': 'Not authorized to delete this message'}, status=status.HTTP_403_FORBIDDEN)
        
        message.delete()
        return Response({'detail': 'Message deleted for everyone'}, status=status.HTTP_204_NO_CONTENT)

    elif action == 'delete_for_self':
        # Mark the message as not visible for the user
        visibility = Visibility.objects.get(message=message, personal=personal)
        visibility.delete()
        return Response({'detail': 'Message hidden for personal'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'detail': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def get_messages(request, friend_id):
    user = request.user
    personal = Personal.objects.get(user=user)
    friend = get_object_or_404(Personal, id=friend_id)
    
    if not Friendship.objects.filter(personal=personal, friend=friend).exists() and \
       not Friendship.objects.filter(personal=friend, friend=personal).exists():
        return Response({'detail': 'Not friends'}, status=status.HTTP_403_FORBIDDEN)

    messages = Message.objects.filter(
        (Q(sender=personal) & Q(receiver=friend) & Q(visibilities__personal=personal)) |
        (Q(sender=friend) & Q(receiver=personal) & Q(visibilities__personal=personal))
    ).order_by('timestamp')
    # Apply filtering
    filter_backend = DjangoFilterBackend()
    view = None  # Pass `None` as the view is not necessary for filtering
    filter_set = MessageFilter(request.GET, queryset=messages)
    filtered_messages = filter_backend.filter_queryset(request, filter_set.qs, view)

    serializer = MessageSerializer(filtered_messages, many=True)
    return Response(serializer.data)
