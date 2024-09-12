from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Reaction, Share, Personal, Invitations, Replies, Reactions, Like, Invitation, Friendship, Following
from .serializers import InvitationSerializer, PostSerializer, CommentSerializer, ShareSerializer, PersonalSerializer, LikeSerializer
from rest_framework import status
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from identity.models import Role, Roles
from identity.utils import role_required
from ebook.models import EBook, Review
from .filters.postFilters import PostFilter
from .filters.personalFilters import PersonalFilter
from .filters.invitationFilters import InvitationFilter
from .filters.shareFilters import ShareFilter
from rest_framework.pagination import PageNumberPagination
from django.utils.crypto import get_random_string

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.GUEST, Roles.ADMIN)
@parser_classes([MultiPartParser, FormParser])
def create_personal_profile(request):
    data = request.data
    isWriter = data.get('is_writer')
    if isWriter == None:
        return Response({"error": "invalide request."}, status=status.HTTP_400_BAD_REQUEST)
    
    personal = PersonalSerializer(data = data, context={'request': request})
    if personal.is_valid():
        image_file = request.FILES.get('image')
        if image_file:
            validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
            try:
                validator(image_file)
            except ValidationError:
                return Response({"error": "Invalid file format. Only JPG, JPEG, PNG, and GIF formats are supported for the image."}, status=status.HTTP_400_BAD_REQUEST)
                
        isWriter = isWriter.lower() in ('true', '1', 't', 'y', 'yes')
        role_name = Roles.WRITER if isWriter else Roles.READER

        if request.user.roles.filter(name=role_name).exists():
            return Response({"error": f"You already have a {role_name.lower()} profile."}, status=status.HTTP_400_BAD_REQUEST)

        personal.save(user=request.user)
        role, created = Role.objects.get_or_create(name=role_name)
        request.user.roles.add(role)

        return Response({'details':'Your profile created successfully!'}, status=status.HTTP_201_CREATED)
    else:
        return Response(personal.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
@parser_classes([MultiPartParser, FormParser])
def create_or_add_profile(request):
    try:
        personal = Personal.objects.select_related('user').get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'details':'Not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    isWriter = data.get('is_writer')
    if isWriter == None:
        return Response({"error": "Invalide request."}, status=status.HTTP_400_BAD_REQUEST)
    
    instance = PersonalSerializer(instance=personal, data=data, partial=True, context={'request': request})

    if instance.is_valid():
        image_file = request.FILES.get('image')
        if image_file:
            validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
            try:
                validator(image_file)
            except ValidationError:
                return Response({"error": "Invalid file format. Only JPG, JPEG, PNG, and GIF formats are supported for the image."}, status=status.HTTP_400_BAD_REQUEST)
        
        isWriter = isWriter.lower() in ('true', '1', 't', 'y', 'yes')
        role_name = Roles.WRITER if isWriter else Roles.READER

        if request.user.roles.filter(name=role_name).exists():
            return Response({"error": f"You already have a {role_name.lower()} profile."}, status=status.HTTP_400_BAD_REQUEST)

        instance.save()
        role, created = Role.objects.get_or_create(name=role_name)
        request.user.roles.add(role)

        return Response({'details':'Your profile added successfully!'}, status=status.HTTP_201_CREATED)
    else:
        return Response(personal.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
@parser_classes([MultiPartParser, FormParser])
def update_personal_profile(request):
    try:
        personal = Personal.objects.select_related('user').get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'details':'Not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    personal = PersonalSerializer(instance=personal, data= data, partial=True, context={'request': request})
    
    if personal.is_valid():
        image_file = request.FILES.get('image')
        if image_file:
            validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
            try:
                validator(image_file)
            except ValidationError:
                return Response({"error": "Invalid file format. Only JPG, JPEG, PNG, and GIF formats are supported for the image."}, status=status.HTTP_400_BAD_REQUEST)
        
        personal.save(user= request.user)
        
        return Response({'details':'Your profile updated successfully!'}, status=status.HTTP_200_OK)
    else:
        return Response(personal.errors, status=status.HTTP_400_BAD_REQUEST)
      
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def delete_personal(request):
    try:
        personal = Personal.objects.select_related('user').get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'details': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    user = personal.user
    writer_role = Role.objects.get(name=Roles.WRITER)
    reader_role = Role.objects.get(name=Roles.READER)

    user.roles.remove(writer_role)
    user.roles.remove(reader_role)

    personal.delete()
    return Response({"details":"Delete personal is done"}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def delete_profile(request):
    try:
        personal = Personal.objects.get(user=request.user)
    except Personal.DoesNotExist:
        return Response({"details": "Personal profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    role_name = request.data.get("profile")
    if role_name not in [Roles.READER, Roles.WRITER]:
        return Response({"details": "Invalid role specified"}, status=status.HTTP_400_BAD_REQUEST)

    if role_name == Roles.READER:
        role = request.user.roles.filter(name=Roles.READER)
        role.delete()
    elif role_name == Roles.WRITER:
        role = request.user.roles.filter(name=Roles.WRITER)
        role.delete()

    if not request.user.roles.filter(name=Roles.WRITER).exists():
        ebooks = EBook.objects.filter(author=request.user)
        for ebook in ebooks:
            Review.objects.filter(ebook= ebook).delete()
            ebook.delete()

    if not request.user.roles.filter(name=Roles.WRITER).exists() and not request.user.roles.filter(name=Roles.READER).exists():
        posts = Post.objects.filter(personal=personal)
        for post in posts:
            Comment.objects.filter(post=post).delete()
            Reaction.objects.filter(post= post).delete()
            Share.objects.filter(post= post).delete()
            post.delete()

        Comment.objects.filter(personal=personal).delete()
        Reaction.objects.filter(personal=personal).delete()
        Share.objects.filter(personal=personal).delete()
        Invitation.objects.filter(from_personal=personal).delete()
        Invitation.objects.filter(to_personal=personal).delete()
        Friendship.objects.filter(personal=personal).delete()
        Friendship.objects.filter(friend=personal).delete()
        Following.objects.filter(follower=personal).delete()
        Following.objects.filter(followed_personal=personal).delete()

        try:
            print("5")
            personal.delete()
        except Exception as e:
            return Response({"details": "Error deleting personal profile"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"details": "Profile deletion is done"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def create_post(request):
    try:
        personal = Personal.objects.select_related('user').get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'details':'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    data = request.data
    post = PostSerializer(data = data)
    
    if post.is_valid():
        image_file = request.FILES.get('image')
        if image_file:
            validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
            try:
                validator(image_file)
            except ValidationError:
                return Response({"error": "Invalid file format. Only JPG, JPEG, PNG, and GIF formats are supported for the image."}, status=status.HTTP_400_BAD_REQUEST)
        
        res = post.save(personal=personal)
        serializer = PostSerializer(res, many= False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(post.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def update_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    if post.personal.user != request.user:
        return Response({"error":"Sorry you can't update this post"}, status=status.HTTP_403_FORBIDDEN)
    
    data = request.data
    post = PostSerializer(instance= post, data= data, partial= True)
    
    if post.is_valid():
        image_file = request.FILES.get('image')
        if image_file:
            validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
            try:
                validator(image_file)
            except ValidationError:
                return Response({"error": "Invalid file format. Only JPG, JPEG, PNG, and GIF formats are supported for the image."}, status=status.HTTP_400_BAD_REQUEST)
        
        res = post.save()
        serializer = PostSerializer(res, many= False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(post.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def delete_post(request, pk):
    post = get_object_or_404(Post, id=pk)

    if post.personal.user != request.user:
        return Response({"error":"Sorry you can't delete this post"}, status=status.HTTP_403_FORBIDDEN)
            
    Comment.objects.filter(post=post).delete()
    Reaction.objects.filter(post= post).delete()
    Share.objects.filter(post= post).delete()
    post.delete()
    
    return Response({"details":"Delete post is done"}, status=status.HTTP_200_OK)         

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def get_my_posts(request):
    posts = Post.objects.filter(personal__user=request.user)
    if posts.exists():
        res = PostSerializer(posts, many=True)
        return Response(res.data, status=status.HTTP_200_OK)    
    else:
        return Response({"details":"There are no posts."}, status=status.HTTP_200_OK) 
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def get_my_shared_posts(request):
    shared_posts = Share.objects.filter(personal__user=request.user)
    if shared_posts.exists():
        filterset = ShareFilter(request.GET, queryset=shared_posts)
        count = filterset.qs.count()
        resPage = 15
        paginator = PageNumberPagination()
        paginator.page_size = resPage

        queryset = paginator.paginate_queryset(filterset.qs, request)
        serializer = ShareSerializer(queryset, many=True)
        return Response({"posts":serializer.data, "per page":resPage, "count":count})  
    else:
        return Response({"details":"There are no posts."}, status=status.HTTP_200_OK) 
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def get_posts_of(request, pk):   
    try:
        friend = get_object_or_404(Personal, id=pk)
        if friend.locked:
            personal = Personal.objects.select_related('user').get(user=request.user)
            Friendship.objects.get(personal=personal, friend=friend)

        filterset = PostFilter(request.GET, queryset=Post.objects.filter(personal=friend).order_by('published_at'))
        count = filterset.qs.count()
        resPage = 15
        paginator = PageNumberPagination()
        paginator.page_size = resPage

        queryset = paginator.paginate_queryset(filterset.qs, request)
        serializer = PostSerializer(queryset, many=True)
        return Response({"posts":serializer.data, "per page":resPage, "count":count})
    except Personal.DoesNotExist:
        return Response({"error": "personal not found."}, status=status.HTTP_404_NOT_FOUND)
    except Friendship.DoesNotExist:
        return Response({"error": "Friendship not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def get_shared_posts_of(request, pk):   
    try:
        friend = get_object_or_404(Personal, id=pk)
        if friend.locked:
            personal = Personal.objects.select_related('user').get(user=request.user)
            Friendship.objects.get(personal=personal, friend=friend)
        
        shared_posts = Share.objects.filter(personal__user=request.user)
        if shared_posts.exists():
            filterset = ShareFilter(request.GET, queryset=shared_posts)
            count = filterset.qs.count()
            resPage = 15
            paginator = PageNumberPagination()
            paginator.page_size = resPage

            queryset = paginator.paginate_queryset(filterset.qs, request)
            serializer = ShareSerializer(queryset, many=True)
            return Response({"posts":serializer.data, "per page":resPage, "count":count})
        else:
            return Response({"details": "There are no shared posts."}, status=status.HTTP_200_OK)
    except Personal.DoesNotExist:
        return Response({"error": "personal not found."}, status=status.HTTP_404_NOT_FOUND)
    except Friendship.DoesNotExist:
        return Response({"error": "Friendship not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)   

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def share_post(request, post_id):
    try:
        personal = Personal.objects.select_related('user').get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'details':'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    post = get_object_or_404(Post, id=post_id)
    shares = Share.objects.filter(personal=personal, post=post)
    if not shares.exists():
        shared_post = Share.objects.create(personal=personal, post=post)
        Reaction.objects.create(personal=personal, post=post, share=shared_post, type=Reactions.SHARE)
        serializer = ShareSerializer(shared_post)
        return Response(serializer.data)
    return Response({'detail':'You are already shared this post.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def delete_shared_post(request, pk):
    share = get_object_or_404(Share, id=pk)
    if share.personal.user != request.user:
        return Response({"error":"Sorry you can't delete this shared post."}, status=status.HTTP_403_FORBIDDEN)
            
    Reaction.objects.filter(share= share).delete()
    share.delete()
    
    return Response({"details":"Delete shared post is done."}, status=status.HTTP_200_OK)    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def like_post(request, post_id):
    try:
        personal = Personal.objects.select_related('user').get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'details':'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    post = get_object_or_404(Post, id=post_id)
    likes = Like.objects.filter(personal=personal, post=post)
    if not likes.exists():
        like = Like.objects.create(personal=personal, post=post)
        Reaction.objects.create(personal=personal, post=post, like=like, type=Reactions.LIKE)
        serializer = LikeSerializer(like)
        return Response(serializer.data)
    return Response({'detail':'You are already liked this post.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def delete_like(request, pk):
    like = get_object_or_404(Like, id=pk)
    if like.personal.user != request.user:
        return Response({"error":"Sorry you can't delete this reaction"}, status=status.HTTP_403_FORBIDDEN)
            
    Reaction.objects.filter(like= like).delete()
    like.delete()
    
    return Response({"details":"Delete reaction is done"}, status=status.HTTP_200_OK)    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def comment_on_post(request, post_id):
    try:
        personal = Personal.objects.select_related('user').get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'details':'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    post = get_object_or_404(Post, id=post_id)
    data = request.data.copy()
    data['personal'] = personal.id
    serializer = CommentSerializer(data=data)

    if serializer.is_valid():
        image_file = request.FILES.get('image')
        if image_file:
            validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
            try:
                validator(image_file)
            except ValidationError:
                return Response({"error": "Invalid file format. Only JPG, JPEG, PNG, and GIF formats are supported for the image."}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(post=post)
        Reaction.objects.create(personal=personal, post=post, type=Reactions.COMMENT)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def reply_to_comment(request, comment_id):
    try:
        personal = Personal.objects.select_related('user').get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'details':'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    parent_comment = get_object_or_404(Comment, id=comment_id)
    data = request.data.copy()
    data['personal'] = personal.id
    data['post'] = parent_comment.post.id
    data['parent_comment'] = parent_comment.id
    serializer = CommentSerializer(data=data)

    if serializer.is_valid():
        image_file = request.FILES.get('image')
        if image_file:
            validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
            try:
                validator(image_file)
            except ValidationError:
                return Response({"error": "Invalid file format. Only JPG, JPEG, PNG, and GIF formats are supported for the image."}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        Reaction.objects.create(personal=personal, comment=parent_comment, post=parent_comment.post, type=Reactions.COMMENT)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def update_comment(request, pk):
    comment = get_object_or_404(Comment, id=pk)
    if comment.personal.user != request.user:
        return Response({"error":"Sorry you can't update this comment"}, status=status.HTTP_403_FORBIDDEN)
    
    data = request.data
    comment = CommentSerializer(instance= comment, data= data, partial= True)
    
    if comment.is_valid():
        image_file = request.FILES.get('image')
        if image_file:
            validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
            try:
                validator(image_file)
            except ValidationError:
                return Response({"error": "Invalid file format. Only JPG, JPEG, PNG, and GIF formats are supported for the image."}, status=status.HTTP_400_BAD_REQUEST)
        
        res = comment.save()
        serializer = CommentSerializer(res, many= False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(comment.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, id=pk)

    if comment.personal.user != request.user:
        return Response({"error":"Sorry you can't delete this comment"}, status=status.HTTP_403_FORBIDDEN)
            
    Comment.objects.filter(parent_comment=comment).delete()
    Reaction.objects.filter(comment= comment).delete()
    comment.delete()
    
    return Response({"details":"Delete comment is done"}, status=status.HTTP_200_OK)   

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def like_comment(request, comment_id):
    try:
        personal = Personal.objects.select_related('user').get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'details':'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    comment = get_object_or_404(Comment, id=comment_id)
    likes = Like.objects.filter(personal=personal, comment=comment)
    if not likes.exists():
        like = Like.objects.create(personal=personal, comment=comment)
        Reaction.objects.create(personal=personal, comment=comment, like=like, type=Reactions.LIKE)
        serializer = LikeSerializer(like)
        return Response(serializer.data)
    return Response({'detail':'You are already liked this comment.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def send_friendship_invitation(request, to_personal_id):
    try:
        personal = Personal.objects.select_related('user').get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'details':'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    to_personal = get_object_or_404(Personal, id=to_personal_id)
    
    if Friendship.objects.filter(personal=personal, friend=to_personal).exists() or Friendship.objects.filter(personal=to_personal, friend=personal).exists():
        return Response({'details': 'You are already friends.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if Invitation.objects.filter(from_personal=personal, to_personal=to_personal, type=Invitations.FRIENDSHIP, status=Replies.PENDING).exists():
        return Response({'details': 'Friendship invitation already sent.'}, status=status.HTTP_400_BAD_REQUEST)
    
    invitation = Invitation.objects.create(from_personal=personal, to_personal=to_personal, type=Invitations.FRIENDSHIP)
    serializer = InvitationSerializer(invitation)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def send_following_invitation(request, to_personal_id):
    try:
        personal = Personal.objects.select_related('user').get(user=request.user)
    except Personal.DoesNotExist:
        return Response({'details':'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    followed_personal = get_object_or_404(Personal, id=to_personal_id)
    if Following.objects.filter(follower=personal, followed_personal=followed_personal).exists() or Following.objects.filter(follower=followed_personal, followed_personal=personal).exists():
        return Response({'details': 'You are already following him.'}, status=status.HTTP_400_BAD_REQUEST)
    if Invitation.objects.filter(from_personal=personal, to_personal=followed_personal, type=Invitations.FOLLOWING, status=Replies.PENDING).exists():
        return Response({'details': 'Following invitation already sent.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not followed_personal.locked:
        Following.objects.create(follower=personal, followed_personal=followed_personal)
        invitation = Invitation.objects.create(from_personal=personal, to_personal=followed_personal, type=Invitations.FOLLOWING, status=Replies.ACCEPTED)
    else:
        invitation = Invitation.objects.create(from_personal=personal, to_personal=followed_personal, type=Invitations.FOLLOWING)
    
    serializer = InvitationSerializer(invitation)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def manage_invitation(request, invitation_id):
    action = request.data.get('action')
    if action not in [Replies.ACCEPTED, Replies.REJECTED]:
        return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        invitation = Invitation.objects.get(id=invitation_id, to_personal__user=request.user)
    except Invitation.DoesNotExist:
        return Response({"error": "Invitation not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if action == Replies.ACCEPTED:
        invitation.status = Replies.ACCEPTED
        if invitation.type == Invitations.FRIENDSHIP:
            Friendship.objects.create(personal=invitation.from_personal, friend=invitation.to_personal, queue_token=get_random_string(40))
            Friendship.objects.create(personal=invitation.to_personal, friend=invitation.from_personal, queue_token=get_random_string(40))
        elif invitation.type == Invitations.FOLLOWING:
            Following.objects.create(follower=invitation.from_personal, followed_personal=invitation.to_personal)
    else:
        invitation.status = Replies.REJECTED
    
    invitation.save()
    return Response({"detail": f"Invitation {action} successfully."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def get_invitations(request):
    action = request.data.get('action')
    if action not in ['sent', 'received']:
        return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)
    
    if action == 'sent':
        invitations = Invitation.objects.filter(from_personal__user=request.user)
    elif action == 'received':
        invitations = Invitation.objects.filter(to_personal__user=request.user)

    if invitations.exists():
        filterset = InvitationFilter(request.GET, queryset=invitations.order_by('-created_at'))
        count = filterset.qs.count()
        resPage = 15
        paginator = PageNumberPagination()
        paginator.page_size = resPage

        queryset = paginator.paginate_queryset(filterset.qs, request)
        serializer = InvitationSerializer(queryset, many=True)
        return Response({"invitations": serializer.data, "per page": resPage, "count": count})
    else:
        return Response({"details": "There are no invitations."}, status=status.HTTP_200_OK)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def list_relations(request):
    try:
        personal = Personal.objects.get(user=request.user)
    except Personal.DoesNotExist:
        return Response({"error": "Personal profile not found."}, status=status.HTTP_404_NOT_FOUND)

    # Amis
    friends = Friendship.objects.filter(personal=personal)
    friends_data = [{"id": f.friend.id, "name": f.friend.user.get_full_name()} for f in friends]

    # Suivis
    following = Following.objects.filter(follower=personal)
    following_data = [{"id": f.followed_personal.id, "name": f.followed_personal.user.get_full_name()} for f in following]

    # Followers
    followers = Following.objects.filter(followed_personal=personal)
    followers_data = [{"id": f.follower.id, "name": f.follower.user.get_full_name()} for f in followers]

    return Response({
        "friends": friends_data,
        "following": following_data,
        "followers": followers_data,
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def delete_invitation(request, pk):
    invitation = get_object_or_404(Invitation, id=pk)
    if invitation.from_personal.user != request.user and invitation.to_personal.user != request.user and invitation.status != Replies.PENDING:
        return Response({"error":"Sorry you can't delete this invitation."}, status=status.HTTP_403_FORBIDDEN)
            
    invitation.delete()
    return Response({"details": "Invitation deleted successfully."}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def unfollow_person(request, personal_id):
    try:
        personal = Personal.objects.get(user=request.user)
        followed_person = Personal.objects.get(id=personal_id)
        following_relation = Following.objects.get(follower=personal, followed_personal=followed_person)
        following_relation.delete()
        return Response({"details": "Unfollowed successfully."}, status=status.HTTP_200_OK)
    except (Personal.DoesNotExist, Following.DoesNotExist):
        return Response({"error": "Following relation not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def remove_follower(request, personal_id):
    try:
        personal = Personal.objects.get(user=request.user)
        follower_person = Personal.objects.get(id=personal_id)
        follower_relation = Following.objects.get(follower=follower_person, followed_personal=personal)
        follower_relation.delete()
        return Response({"details": "Follower removed successfully."}, status=status.HTTP_200_OK)
    except (Personal.DoesNotExist, Following.DoesNotExist):
        return Response({"error": "Follower relation not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def get_my_followers(request):
    followings = Following.objects.filter(followed_personal__user=request.user)
    if followings.exists():
        follower_ids = [following.follower.id for following in followings]
        followers_queryset = Personal.objects.filter(id__in=follower_ids)
        if followers_queryset.exists():
            filterset = PersonalFilter(request.GET, queryset=followers_queryset.order_by('posts'))
            count = filterset.qs.count()
            resPage = 15
            paginator = PageNumberPagination()
            paginator.page_size = resPage

            queryset = paginator.paginate_queryset(filterset.qs, request)
            serializer = PersonalSerializer(queryset, many=True)
            return Response({"followers": serializer.data, "per page": resPage, "count": count})
        else:
            return Response({"details": "There are no followers."}, status=status.HTTP_200_OK)
    else:
        return Response({"details": "There are no followings."}, status=status.HTTP_200_OK)
      
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def get_followers_of(request, pk):   
    try:
        friend = get_object_or_404(Personal, id=pk)
        if friend.locked:
            personal = Personal.objects.select_related('user').get(user=request.user)
            Friendship.objects.get(personal=personal, friend=friend)
        
        followings = Following.objects.filter(follower__user=request.user)
        if followings.exists():
            follower_ids = [following.follower.id for following in followings]
            followers_queryset = Personal.objects.filter(id__in=follower_ids)
            if followers_queryset.exists():
                filterset = PersonalFilter(request.GET, queryset=followers_queryset.order_by('posts'))
                count = filterset.qs.count()
                resPage = 15
                paginator = PageNumberPagination()
                paginator.page_size = resPage

                queryset = paginator.paginate_queryset(filterset.qs, request)
                serializer = PersonalSerializer(queryset, many=True)
                return Response({"followers": serializer.data, "per page": resPage, "count": count})
            else:
                return Response({"details": "There are no followers."}, status=status.HTTP_200_OK)
        else:
            return Response({"details": "There are no followings."}, status=status.HTTP_200_OK)
    except Personal.DoesNotExist:
        return Response({"error": "Friend not found."}, status=status.HTTP_404_NOT_FOUND)
    except Friendship.DoesNotExist:
        return Response({"error": "Friendship not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def get_my_followups(request):
    followings = Following.objects.filter(follower__user=request.user)
    if followings.exists():
        followup_ids = [following.followed_personal.id for following in followings]
        followups_queryset = Personal.objects.filter(id__in=followup_ids)
        if followups_queryset.exists():
            filterset = PersonalFilter(request.GET, queryset=followups_queryset.order_by('posts'))
            count = filterset.qs.count()
            resPage = 15
            paginator = PageNumberPagination()
            paginator.page_size = resPage

            queryset = paginator.paginate_queryset(filterset.qs, request)
            serializer = PersonalSerializer(queryset, many=True)
            return Response({"follow_ups": serializer.data, "per page": resPage, "count": count})
        else:
            return Response({"details": "There are no follow_ups."}, status=status.HTTP_200_OK)
    else:
        return Response({"details": "There are no followings."}, status=status.HTTP_200_OK)
      
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def get_followups_of(request, pk):   
    try:
        friend = get_object_or_404(Personal, id=pk)
        if friend.locked:
            personal = Personal.objects.select_related('user').get(user=request.user)
            Friendship.objects.get(personal=personal, friend=friend)
        
        followings = Following.objects.filter(follower__user=friend.user)
        if followings.exists():
            followup_ids = [following.followed_personal.id for following in followings]
            followups_queryset = Personal.objects.filter(id__in=followup_ids)
            if followups_queryset.exists():
                filterset = PersonalFilter(request.GET, queryset=followups_queryset.order_by('posts'))
                count = filterset.qs.count()
                resPage = 15
                paginator = PageNumberPagination()
                paginator.page_size = resPage

                queryset = paginator.paginate_queryset(filterset.qs, request)
                serializer = PersonalSerializer(queryset, many=True)
                return Response({"follow_ups": serializer.data, "per page": resPage, "count": count})
            else:
                return Response({"details": "There are no follow_ups."}, status=status.HTTP_200_OK)
        else:
            return Response({"details": "There are no followings."}, status=status.HTTP_200_OK)
    except Personal.DoesNotExist:
        return Response({"error": "Friend not found."}, status=status.HTTP_404_NOT_FOUND)
    except Friendship.DoesNotExist:
        return Response({"error": "Friendship not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
          
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def delete_friend(request, friend_id):
    try:
        personal = Personal.objects.get(user=request.user)
        friendship_sender = Friendship.objects.get(personal=personal, friend__id=friend_id)
        friendship_sender.delete()
        friendship_receiver = Friendship.objects.get(personal__id=friend_id, friend=personal)
        friendship_receiver.delete()
        return Response({"details": "Friend deleted successfully."}, status=status.HTTP_200_OK)
    except (Personal.DoesNotExist, Friendship.DoesNotExist):
        return Response({"error": "Friendship not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def get_my_friends(request):
    friendships = Friendship.objects.filter(personal__user=request.user)
    if friendships.exists():
        freind_ids = [friendship.friend.id for friendship in friendships]
        friends_queryset = Personal.objects.filter(id__in=freind_ids)
        if friends_queryset.exists():
            filterset = PersonalFilter(request.GET, queryset=friends_queryset.order_by('posts'))
            count = filterset.qs.count()
            resPage = 15
            paginator = PageNumberPagination()
            paginator.page_size = resPage

            queryset = paginator.paginate_queryset(filterset.qs, request)
            serializer = PersonalSerializer(queryset, many=True)
            return Response({"friends":serializer.data, "per page":resPage, "count":count}) 
        else:
            return Response({"details":"There are no friends."}, status=status.HTTP_200_OK) 
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.ADMIN)
def get_friends_of(request, pk):   
    try:
        friend = get_object_or_404(Personal, id=pk)
        if friend.locked:
            personal = Personal.objects.select_related('user').get(user=request.user)
            Friendship.objects.get(personal=personal, friend=friend)
        
        friendships = Friendship.objects.filter(personal=friend)
        if friendships.exists():
            freind_ids = [friendship.friend.id for friendship in friendships]
            friends_queryset = Personal.objects.filter(id__in=freind_ids)
            if friends_queryset.exists():
                filterset = PersonalFilter(request.GET, queryset=friends_queryset.order_by('posts'))
                count = filterset.qs.count()
                resPage = 15
                paginator = PageNumberPagination()
                paginator.page_size = resPage

                queryset = paginator.paginate_queryset(filterset.qs, request)
                serializer = PersonalSerializer(queryset, many=True)
                return Response({"friends":serializer.data, "per page":resPage, "count":count})
            else:
                return Response({"details": "There are no friends."}, status=status.HTTP_200_OK)
        else:
            return Response({"details": "There are no friendships."}, status=status.HTTP_200_OK)
    except Personal.DoesNotExist:
        return Response({"error": "personal not found."}, status=status.HTTP_404_NOT_FOUND)
    except Friendship.DoesNotExist:
        return Response({"error": "Friendship not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
