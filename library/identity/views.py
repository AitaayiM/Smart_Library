from datetime import datetime, timedelta
import random
import string
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination

from .models import User, Role, Roles
from .filters import UserFilter
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignUpSerializer, UserSerializer

from django.utils import timezone
from django.contrib.auth import authenticate, login as django_login
from .models import Profile
from .utils import role_required

from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.views import TokenObtainPairView
# Create your views here.

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.GUEST, Roles.ADMIN)
def update_user(request):
    user = request.user
    data = request.data

    user.first_name = data['first_name']
    user.username = data['username']
    user.last_name = data['last_name']
    user.gender = data['gender']
    user.date_of_birth = data['date_of_birth']

    if data['password'] != "":
        user.password =  make_password(data['password'])

    user.save()
    return Response(
                {'details': 'Your account updated successfully!'},
                status= status.HTTP_205_RESET_CONTENT
            )

@api_view(['GET'])
def available(request):
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register(request):
    data = request.data
    user = SignUpSerializer(data = data)

    if user.is_valid():
        if not User.objects.filter(username = data['username']).exists():
            user = User.objects.create(
                first_name = data['first_name'],
                last_name = data['last_name'],
                username = data['username'],
                date_of_birth = data['date_of_birth'],
                gender = data['gender'],
                password = make_password(data['password']),
            )
            guest_role, created = Role.objects.get_or_create(name=Roles.GUEST)
            user.roles.add(guest_role)
            return Response(
                {'details':'Your account registered successfully!'},
                status= status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error':'Email or password invalid!'},
                status= status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(user.errors)

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, username=email, password=password)

    if user is not None:
        # User credentials are valid, proceed with code generation and email sending
        user_profile = Profile.objects.get(user=user)       
        # Generate a random code
        verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        user_profile.one_time_password = verification_code
        user_profile.one_time_password_expire = timezone.now() + timedelta(hours=1)
        user_profile.save()

        # Send the code via email (use Django's send_mail function)
        send_mail(
            'Verification Code',
            f'Your verification code is: {user_profile.one_time_password}',
            'M-Read@gmail.com',
            [email],
            fail_silently=False,
        )
        return Response({'detail': 'Verification code sent successfully.'}, status=status.HTTP_200_OK)
    return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def login_verification(request):
    email = request.data.get('username')
    password = request.data.get('password')
    one_time_password = request.data.get('one_time_password')
    user = authenticate(request, username=email, password=password)

    if user is not None:
        user_profile = Profile.objects.get(user=user)
        # Check if the verification code is valid and not expired
        if (
            user_profile.one_time_password is not None and
            user_profile.one_time_password == one_time_password and
            user_profile.one_time_password_expire > timezone.now()
        ):
            # Verification successful, generate access and refresh tokens
            django_login(request, user)
            # Verification successful, generate access and refresh tokens
            factory = APIRequestFactory()
            token_request = factory.post('/token/', {'username': email, 'password': password} ,format='json')
            token_obtain_pair_view = TokenObtainPairView.as_view()
            response = token_obtain_pair_view(token_request)
            # Reset verification code and expiry time
            user_profile.one_time_password = ''
            user_profile.one_time_password_expire = None
            user_profile.save()
            return response
    return Response({'detail': 'Invalid verification code or credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.GUEST, Roles.ADMIN)
def current_info(request):
    user = SignUpSerializer(request.user)
    return Response(user.data)

def get_current_host(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/".format(protocol=protocol, host=host)

@api_view(['POST'])
def forgot_password(request):
    data = request.data
    user = get_object_or_404(User, username=data['email'])
    token = get_random_string(40)
    expire_date = datetime.now()+timedelta(minutes=30)
    user.profile.one_time_password = token
    user.profile.one_time_password_expire = expire_date
    user.profile.save()

    link = "{host}api/reset_password/{token}/".format(host=get_current_host(request), token=token)
    body = "Your password reset link is : {link}".format(link=link)
    send_mail(
        "Password reset from M-Read",
        body,
        "m.read@gmail.com",
        [data['email']]
    )
    return Response({'details','Password reset sent to {email}'.format(email=data['email'])})

@api_view(['POST'])
def reset_password(request, token):
    data = request.data
    user = get_object_or_404(User, profile__one_time_password = token)

    if user.profile.one_time_password_expire.replace(tzinfo=None) < datetime.now():
        return Response({'error':'Token is expired'}, status.HTTP_400_BAD_REQUEST)
    
    if data['password'] != data['confirmPassword']:
        return Response({'error':'Password are not same'}, status=status.HTTP_400_BAD_REQUEST)
    
    user.password = make_password(data['password'])
    user.profile.one_time_password = ""
    user.profile.one_time_password_expire = None
    user.profile.save()
    user.save()
    return Response({'details':'Password reset done'})

@api_view(['GET'])
def get_all_users(request):
    try:
        filterset = UserFilter(request.GET, queryset=User.objects.all(), request=request)
        count = filterset.qs.count()
        resPage = 15
        paginator = PageNumberPagination()
        paginator.page_size = resPage

        queryset = paginator.paginate_queryset(filterset.qs, request)
        serializer = UserSerializer(queryset, many=True)
        return Response({"users":serializer.data, "per page":resPage, "count":count})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"details": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.GUEST, Roles.ADMIN)
def delete_user(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': f"User with username {username} does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # Supprime tous les rôles de l'utilisateur
    user.roles.clear()

    # Supprime le profil associé
    try:
        profile = Profile.objects.filter(user__username=username).first()
        profile.delete()
    except Profile.DoesNotExist:
        pass  # Le profil n'existe pas, donc aucune action requise

    # Supprime l'utilisateur lui-même
    user.delete()

    return Response({'message': f"User {username} and associated roles and profile have been deleted"}, status=status.HTTP_204_NO_CONTENT)