from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from identity.models import Roles
from identity.utils import role_required
from rest_framework.response import Response
from .tasks import get_admin_dashboard_data, get_writer_dashboard_data, get_post_dashboard_data, get_friends_followers_dashboard_data, get_reaction_variation_data, get_followers_friends_variation_data, get_admin_variation_data
from celery.result import AsyncResult

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
@role_required(Roles.ADMIN)
def admin_dashboard_data(request):
    task = get_admin_dashboard_data.delay()
    result = AsyncResult(task.id)
    while not result.ready():
        continue
    data = result.get()
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER)
def writer_dashboard_data(request):
    user = request.user
    task = get_writer_dashboard_data.delay(user.id)
    result = AsyncResult(task.id)
    while not result.ready():
        continue
    data = result.get()
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER)
def post_dashboard_data(request, pk):
    user = request.user
    task = get_post_dashboard_data.delay(user.id, pk)
    result = AsyncResult(task.id)
    while not result.ready():
        continue
    data = result.get()
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER)
def friends_followers_dashboard_data(request):
    user = request.user
    task = get_friends_followers_dashboard_data.delay(user.id)
    result = AsyncResult(task.id)
    while not result.ready():
        continue
    data = result.get()
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER)
def reaction_variation_data(request):
    user = request.user
    task = get_reaction_variation_data.delay(user.id)
    result = AsyncResult(task.id)
    while not result.ready():
        continue
    data = result.get()
    if 'error' in data:
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER)
def followers_friends_variation_data(request):
    user = request.user
    task = get_followers_friends_variation_data.delay(user.id)
    result = AsyncResult(task.id)
    while not result.ready():
        continue
    data = result.get()
    if 'error' in data:
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_variation_data(request):
    task = get_admin_variation_data.delay()
    result = AsyncResult(task.id)
    while not result.ready():
        continue
    data = result.get()
    return Response(data)
