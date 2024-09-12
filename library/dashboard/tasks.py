from celery import shared_task
from personality.models import Post, Comment, Like, Share, Personal, Friendship, Following
from identity.models import User
from ebook.models import EBook, Review
from personality.serializers import CommentSerializer
from identity.serializers import UserSerializer
from ebook.serializers import EbookSerializer, ReviewSerializer
from django.db.models import Count, Avg, Sum, F, Q
from django.utils import timezone
from identity.models import User
from django.shortcuts import get_object_or_404
from django.db.models.functions import TruncDate


@shared_task
def get_admin_dashboard_data():
    user_count = User.objects.count()
    active_user_count = User.objects.filter(is_active=True).count()
    user_roles = User.objects.values('roles__name').annotate(count=Count('roles'))
    gender_distribution = User.objects.values('gender').annotate(count=Count('gender'))
    country_distribution = Personal.objects.values('country').annotate(count=Count('country'))
    ebook_count = EBook.objects.count()
    review_count = Review.objects.count()
    category_count = EBook.objects.values('category').annotate(count=Count('category'))
    post_count = Post.objects.count()
    comment_count = Comment.objects.count()
    like_count = Like.objects.count()
    share_count = Share.objects.count()
    latest_users = User.objects.order_by('-date_joined')[:5]
    latest_ebooks = EBook.objects.order_by('-created_at')[:5]
    latest_reviews = Review.objects.order_by('-created_at')[:5]

    country_percentage = [{item['country']: (item['count'] / user_count) * 100} for item in country_distribution]
    total_gender_users = User.objects.exclude(gender='').count()
    gender_percentage = [{item['gender']: (item['count'] / total_gender_users) * 100} for item in gender_distribution]
    category_percentage = [{item['category']: (item['count'] / ebook_count) * 100} for item in category_count]
    total_users_with_roles = User.objects.filter(roles__isnull=False).count()
    roles_percentage = [{item['roles__name']: (item['count'] / total_users_with_roles) * 100} for item in user_roles]

    data = {
        'user_count': user_count,
        'active_user_count': active_user_count,
        'user_roles': list(user_roles),
        'gender_distribution': list(gender_distribution),
        'country_distribution': list(country_distribution),
        'country_percentage': country_percentage,
        'gender_percentage': gender_percentage,
        'ebook_count': ebook_count,
        'review_count': review_count,
        'category_count': list(category_count),
        'category_percentage': category_percentage,
        'post_count': post_count,
        'comment_count': comment_count,
        'like_count': like_count,
        'share_count': share_count,
        'latest_users': UserSerializer(latest_users, many=True).data,
        'latest_ebooks': EbookSerializer(latest_ebooks, many=True).data,
        'latest_reviews': ReviewSerializer(latest_reviews, many=True).data,
        'roles_percentage': roles_percentage,
    }
    return data



@shared_task
def get_writer_dashboard_data(user_id):
    user = User.objects.get(id=user_id)
    ebooks = EBook.objects.filter(author=user)
    ebook_count = ebooks.count()
    average_rating = ebooks.aggregate(avg_ratings=Avg('ratings'))['avg_ratings']
    total_reviews = Review.objects.filter(ebook__in=ebooks).count()
    ebook_performance = ebooks.annotate(
        views=Count('id'),
        downloads=Sum('review_count'),
        avg_ratings=Avg('ratings')
    )
    post_count = Post.objects.filter(personal__user=user).count()
    comment_count = Comment.objects.filter(personal__user=user).count()
    like_count = Like.objects.filter(personal__user=user).count()
    latest_reviews = Review.objects.filter(ebook__in=ebooks).order_by('-created_at')[:5]
    latest_comments = Comment.objects.filter(personal__user=user).order_by('-created_at')[:5]
    reviews = Review.objects.filter(ebook__in=ebooks)

    personal = Personal.objects.filter(user=user).first()
    data = {}
    if personal:
        comments = Comment.objects.filter(post__personal=personal)
        likes = Like.objects.filter(post__personal=personal)

        comment_ids = comments.values_list('personal_id', flat=True)
        like_ids = likes.values_list('personal_id', flat=True)

        commenters = Personal.objects.filter(id__in=comment_ids)
        likers = Personal.objects.filter(id__in=like_ids)
        reactors = set(comment_ids).union(like_ids)

        friends = Friendship.objects.filter(personal=personal).values_list('friend_id', flat=True)
        followers = Following.objects.filter(followed_personal=personal).values_list('follower_id', flat=True)
        
        friends_reactors = reactors.intersection(set(friends))
        followers_reactors = reactors.intersection(set(followers))
        neither_reactors = reactors - friends_reactors - followers_reactors

        total_reactors = len(reactors)
        friends_percentage = (len(friends_reactors) / total_reactors) * 100 if total_reactors else 0
        followers_percentage = (len(followers_reactors) / total_reactors) * 100 if total_reactors else 0
        neither_percentage = (len(neither_reactors) / total_reactors) * 100 if total_reactors else 0

        def calculate_percentage(distribution, total):
            return [{'value': item['user__gender'] if 'user__gender' in item else item['country'], 'count': item['count'], 'percentage': (item['count'] / total) * 100} for item in distribution] if total else []

        personal_commenters = Personal.objects.filter(id__in=comment_ids)
        gender_distribution_commenters = calculate_percentage(personal_commenters.values('user__gender').annotate(count=Count('user__gender')), commenters.count())
        country_distribution_commenters = calculate_percentage(personal_commenters.values('country').annotate(count=Count('country')), commenters.count())

        personal_likers = Personal.objects.filter(id__in=like_ids)
        gender_distribution_likers = calculate_percentage(personal_likers.values('user__gender').annotate(count=Count('user__gender')), likers.count())
        country_distribution_likers = calculate_percentage(personal_likers.values('country').annotate(count=Count('country')), likers.count())

        non_reactors = Personal.objects.filter(Q(followers_relations__follower=personal) | Q(friend__personal=personal)).exclude(id__in=reactors)
        gender_distribution_non_reactors = calculate_percentage(non_reactors.values('user__gender').annotate(count=Count('user__gender')), non_reactors.count())
        country_distribution_non_reactors = calculate_percentage(non_reactors.values('country').annotate(count=Count('country')), non_reactors.count())

        countries = []
        if reviews.exists():
            for review in reviews:
                reader = Personal.objects.filter(user=review.user).first()
                if reader:
                    countries.append(reader.country)

        ebook_details = []
        for ebook in ebooks:
            reviews = Review.objects.filter(ebook=ebook)
            reviewers = User.objects.filter(reviews__ebook=ebook).distinct()
            total_readers = reviewers.count()
            review_percentage = (reviews.count() / total_readers) * 100 if total_readers > 0 else 0

            gender_distribution = reviewers.values('gender').annotate(count=Count('gender'))
            age_distribution = reviewers.annotate(age=timezone.now().year - F('date_of_birth__year')).values('age').annotate(count=Count('age'))
            country_distribution = reviewers.values('personal__country').annotate(count=Count('personal__country'))

            ebook_details.append({
                'ebook': EbookSerializer(ebook).data,
                'reviews': ReviewSerializer(reviews, many=True).data,
                'reviewers_count': total_readers,
                'review_percentage': review_percentage,
                'gender_distribution': gender_distribution,
                'age_distribution': age_distribution,
                'country_distribution': country_distribution,
            })

        data = {
            'ebook_count': ebook_count,
            'average_rating': average_rating,
            'total_reviews': total_reviews,
            'ebook_performance': EbookSerializer(ebook_performance, many=True).data,
            'post_count': post_count,
            'comment_count': comment_count,
            'like_count': like_count,
            'latest_reviews': ReviewSerializer(latest_reviews, many=True).data,
            'latest_comments': CommentSerializer(latest_comments, many=True).data,
            'reader_countries': list(countries),
            'ebook_details': ebook_details,
            'gender_distribution_likers': gender_distribution_likers,
            'country_distribution_likers': country_distribution_likers,
            'gender_distribution_commenters': gender_distribution_commenters,
            'country_distribution_commenters': country_distribution_commenters,
            'gender_distribution_non_reactors': gender_distribution_non_reactors,
            'country_distribution_non_reactors': country_distribution_non_reactors,
            'friends_percentage': friends_percentage,
            'followers_percentage': followers_percentage,
            'neither_percentage': neither_percentage,
        }
    return data



@shared_task
def get_post_dashboard_data(user_id, post_id):
    user = Personal.objects.get(user__id=user_id)
    post = get_object_or_404(Post, id=post_id)
    comment_count = Comment.objects.filter(post=post).count()
    like_count = Like.objects.filter(post=post).count()
    latest_comments = Comment.objects.filter(post=post).order_by('-created_at')[:5]

    data = {}
    if user:
        comment_ids = Comment.objects.filter(post=post).values_list('personal_id', flat=True)
        like_ids = Like.objects.filter(post=post).values_list('personal_id', flat=True)

        commenters = Personal.objects.filter(id__in=comment_ids)
        likers = Personal.objects.filter(id__in=like_ids)
        reactors = set(comment_ids).union(like_ids)

        friends = Friendship.objects.filter(personal=user).values_list('friend_id', flat=True)
        followers = Following.objects.filter(followed_personal=user).values_list('follower_id', flat=True)
        
        friends_reactors = reactors.intersection(set(friends))
        followers_reactors = reactors.intersection(set(followers))
        neither_reactors = reactors - friends_reactors - followers_reactors

        total_reactors = len(reactors)
        friends_percentage = (len(friends_reactors) / total_reactors) * 100 if total_reactors else 0
        followers_percentage = (len(followers_reactors) / total_reactors) * 100 if total_reactors else 0
        neither_percentage = (len(neither_reactors) / total_reactors) * 100 if total_reactors else 0

        def calculate_percentage(distribution, total):
            return [{'value': item['user__gender'] if 'user__gender' in item else item['country'], 'count': item['count'], 'percentage': (item['count'] / total) * 100} for item in distribution] if total else []

        personal_commenters = Personal.objects.filter(id__in=comment_ids)
        gender_distribution_commenters = calculate_percentage(personal_commenters.values('user__gender').annotate(count=Count('user__gender')), commenters.count())
        country_distribution_commenters = calculate_percentage(personal_commenters.values('country').annotate(count=Count('country')), commenters.count())

        personal_likers = Personal.objects.filter(id__in=like_ids)
        gender_distribution_likers = calculate_percentage(personal_likers.values('user__gender').annotate(count=Count('user__gender')), likers.count())
        country_distribution_likers = calculate_percentage(personal_likers.values('country').annotate(count=Count('country')), likers.count())

        non_reactors = Personal.objects.filter(Q(followers_relations__follower=user) | Q(friend__personal=user)).exclude(id__in=reactors)
        gender_distribution_non_reactors = calculate_percentage(non_reactors.values('user__gender').annotate(count=Count('user__gender')), non_reactors.count())
        country_distribution_non_reactors = calculate_percentage(non_reactors.values('country').annotate(count=Count('country')), non_reactors.count())
   
        data = {
            'comment_count': comment_count,
            'like_count': like_count,
            'latest_comments': CommentSerializer(latest_comments, many=True).data,
            'gender_distribution_likers': gender_distribution_likers,
            'country_distribution_likers': country_distribution_likers,
            'gender_distribution_commenters': gender_distribution_commenters,
            'country_distribution_commenters': country_distribution_commenters,
            'gender_distribution_non_reactors': gender_distribution_non_reactors,
            'country_distribution_non_reactors': country_distribution_non_reactors,
            'friends_percentage': friends_percentage,
            'followers_percentage': followers_percentage,
            'neither_percentage': neither_percentage,
        }
    return data



@shared_task
def get_friends_followers_dashboard_data(user_id):
    personal = Personal.objects.filter(user__id=user_id).first()
    if not personal:
        return {'error': 'User not found'}

    friends = Friendship.objects.filter(personal=personal).values_list('friend_id', flat=True)
    followers = Following.objects.filter(followed_personal=personal).values_list('follower_id', flat=True)

    def calculate_percentage(distribution, total):
        return [{'value': item['user__gender'] if 'user__gender' in item else item['country'], 'count': item['count'], 'percentage': (item['count'] / total) * 100} for item in distribution] if total else []

    # For friends
    friends_distribution = calculate_percentage(Personal.objects.filter(id__in=friends).values('user__gender').annotate(count=Count('user__gender')), len(friends))
    friends_country_distribution = calculate_percentage(Personal.objects.filter(id__in=friends).values('country').annotate(count=Count('country')), len(friends))

    # For followers
    followers_distribution = calculate_percentage(Personal.objects.filter(id__in=followers).values('user__gender').annotate(count=Count('user__gender')), len(followers))
    followers_country_distribution = calculate_percentage(Personal.objects.filter(id__in=followers).values('country').annotate(count=Count('country')), len(followers))

    data = {
        'friends_distribution': friends_distribution,
        'friends_country_distribution': friends_country_distribution,
        'followers_distribution': followers_distribution,
        'followers_country_distribution': followers_country_distribution,
    }

    return data



@shared_task
def get_reaction_variation_data(user_id):
    personal = Personal.objects.filter(user__id=user_id).first()
    if not personal:
        return {'error': 'User not found'}

    posts = Post.objects.filter(personal=personal)

    # Likes per day
    likes_per_day = Like.objects.filter(post__in=posts).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    likes_data = {entry['date']: entry['count'] for entry in likes_per_day}

    # Comments per day
    comments_per_day = Comment.objects.filter(post__in=posts).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    comments_data = {entry['date']: entry['count'] for entry in comments_per_day}

    # Shares per day
    shares_per_day = Share.objects.filter(post__in=posts).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    shares_data = {entry['date']: entry['count'] for entry in shares_per_day}

    # Combine data
    reaction_variation = []
    dates = set(likes_data.keys()).union(comments_data.keys()).union(shares_data.keys())
    for date in sorted(dates):
        reaction_variation.append({
            'date': date,
            'likes': likes_data.get(date, 0),
            'comments': comments_data.get(date, 0),
            'shares': shares_data.get(date, 0),
        })

    return {'reaction_variation': reaction_variation}



@shared_task
def get_followers_friends_variation_data(user_id):
    personal = Personal.objects.filter(user__id=user_id).first()
    if not personal:
        return {'error': 'User not found'}

    # Followers per day
    followers_per_day = Following.objects.filter(followed_personal=personal).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    followers_data = {entry['date']: entry['count'] for entry in followers_per_day}

    # Friends per day
    friends_per_day = Friendship.objects.filter(personal=personal).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    friends_data = {entry['date']: entry['count'] for entry in friends_per_day}

    # Combine data
    variation_data = []
    dates = set(followers_data.keys()).union(friends_data.keys())
    for date in sorted(dates):
        variation_data.append({
            'date': date,
            'followers': followers_data.get(date, 0),
            'friends': friends_data.get(date, 0),
        })

    return {'variation_data': variation_data}



@shared_task
def get_admin_variation_data():
    # EBooks per day
    ebooks_per_day = EBook.objects.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    ebooks_data = {entry['date']: entry['count'] for entry in ebooks_per_day}

    # Posts per day
    posts_per_day = Post.objects.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    posts_data = {entry['date']: entry['count'] for entry in posts_per_day}

    # Users per day
    users_per_day = User.objects.annotate(date=TruncDate('date_joined')).values('date').annotate(count=Count('id')).order_by('date')
    users_data = {entry['date']: entry['count'] for entry in users_per_day}

    # Personals per day
    personals_per_day = Personal.objects.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    personals_data = {entry['date']: entry['count'] for entry in personals_per_day}

    # Combine data
    variation_data = []
    dates = set(ebooks_data.keys()).union(posts_data.keys()).union(users_data.keys()).union(personals_data.keys())
    for date in sorted(dates):
        variation_data.append({
            'date': date,
            'ebooks': ebooks_data.get(date, 0),
            'posts': posts_data.get(date, 0),
            'users': users_data.get(date, 0),
            'personals': personals_data.get(date, 0),
        })

    return {'variation_data': variation_data}
