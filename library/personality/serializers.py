from datetime import datetime
from rest_framework import serializers
from .models import Personal, Post, Comment, Share, Reaction, Invitation, Friendship, Following, Like
from identity.models import Roles

class PersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personal
        fields = '__all__'
        read_only_fields = ['books_published', 'bio', 'isbn']  

    def update(self, instance, validated_data):
        instance.updated_at = datetime.now()
        user = self.context['request'].user
        if not user.roles.filter(name__in=[Roles.WRITER, Roles.ADMIN]).exists():
            validated_data.pop('bio', None)
            validated_data.pop('isbn', None)
            validated_data.pop('books_published', None)
        return super().update(instance, validated_data)

class PersonalMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Personal
        fields = ['id', 'full_name', 'image']

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

class ShareMiniSerializer(serializers.ModelSerializer):
    personal = PersonalMiniSerializer(read_only=True)

    class Meta:
        model = Share
        fields = ['personal', 'created_at']

class PostSerializer(serializers.ModelSerializer):
        
    personal = PersonalMiniSerializer(read_only=True)
    comment = serializers.SerializerMethodField(method_name='get_comments', read_only=True)
    like = serializers.SerializerMethodField(method_name='get_likes', read_only=True)
    share = serializers.SerializerMethodField(method_name='get_shares', read_only=True)

    class Meta:
        model = Post
        fields = '__all__'

    def get_comments(self, obj):
        comments = obj.comment.all()
        serializer = CommentSerializer(comments, many=True)
        return serializer.data
    
    def get_likes(self, obj):
        likes = obj.like.all()
        serializer = LikeSerializer(likes, many=True)
        return serializer.data
    
    def get_shares(self, obj):
        shares = obj.share.all()
        serializer = ShareMiniSerializer(shares, many=True)
        return serializer.data

    def create(self, validated_data):
        instance = super().create(validated_data)
        if instance.published_at is None:
            instance.published_at = datetime.now()
            instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.updated_at = datetime.now()
        return super().update(instance, validated_data)

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField(method_name='get_replies', read_only=True)
    like = serializers.SerializerMethodField(method_name='get_likes', read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'

    def get_replies(self, obj):
        replies = obj.replies.all()
        serializer = CommentSerializer(replies, many=True)
        return serializer.data
    
    def get_likes(self, obj):
        likes = obj.like.all()
        serializer = LikeSerializer(likes, many=True)
        return serializer.data

    def update(self, instance, validated_data):
        instance.updated_at = datetime.now()
        return super().update(instance, validated_data)

class ShareSerializer(serializers.ModelSerializer):
    class PersonalMiniSerializer(serializers.ModelSerializer):
        full_name = serializers.SerializerMethodField()

        class Meta:
            model = Personal
            fields = ['id', 'full_name', 'image']

        def get_full_name(self, obj):
            return f"{obj.user.first_name} {obj.user.last_name}"
        
    personal = PersonalMiniSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    
    class Meta:
        model = Share
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = '__all__'

class InvitationSerializer(serializers.ModelSerializer):

    class PersonalMiniSerializer(serializers.ModelSerializer):
        full_name = serializers.SerializerMethodField()

        class Meta:
            model = Personal
            fields = ['id', 'full_name', 'image']

        def get_full_name(self, obj):
            return f"{obj.user.first_name} {obj.user.last_name}"
        
    from_personal = PersonalMiniSerializer(read_only=True)
    to_personal = PersonalMiniSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = '__all__'

class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = '__all__'

class FollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Following
        fields = '__all__'
