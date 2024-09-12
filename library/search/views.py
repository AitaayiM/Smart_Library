from rest_framework.decorators import api_view
from rest_framework.response import Response
from ebook.serializers import EbookSerializer
from identity.serializers import UserSerializer
from ebook.models import EBook
from identity.models import User, Roles
from identity.utils import role_required
from .search import lookup
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from .filters.ebookFilters import EbookFilter
from .filters.userFilters import UserFilter
from rest_framework.pagination import PageNumberPagination
from .filters.personalFilters import PersonalFilter
from personality.models import Personal
from personality.serializers import PersonalMiniSerializer

@api_view(['GET'])
def search_ebooks(request):
    keyword = request.GET.get("keyword")
    if not keyword:
        return Response("At least one keyword is required", status=status.HTTP_400_BAD_REQUEST)
    
    query_params = request.GET
    if query_params:
        filter_params = {}
        if 'published_at' in query_params:
            filter_params['published_at'] = query_params['published_at']
        if 'minRating' in query_params:
            filter_params['minRating'] = query_params['minRating']
        if 'maxRating' in query_params:
            filter_params['maxRating'] = query_params['maxRating']
        if 'minPage' in query_params:
            filter_params['minPage'] = query_params['minPage']
        if 'maxPage' in query_params:
            filter_params['maxPage'] = query_params['maxPage']
    
    results = lookup(query=keyword,
                            index='ebooks',
                            fields=["title", "summary", "category", "content_text"])

    ebook_ids = [hit.id for hit in results]
    ebooks = EBook.objects.filter(id__in=ebook_ids)
    
    filterset = EbookFilter(query_params, queryset=ebooks)
    count = filterset.qs.count()
    resPage = 15
    paginator = PageNumberPagination()
    paginator.page_size = resPage

    queryset = paginator.paginate_queryset(filterset.qs, request)

    serializer = EbookSerializer(queryset, many=True)
    return Response({"ebooks": serializer.data, "per page": resPage, "count": count})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.GUEST, Roles.ADMIN)
def search_users(request):
    query = request.GET.get('keyword')
    if not query:
        return Response("At least one keyword is required", status=status.HTTP_400_BAD_REQUEST)
    
    query_params = request.GET
    if query_params:
        filter_params = {}
        if 'roles' in query_params:
            filter_params['roles'] = query_params['roles']
        if 'gender' in query_params:
            filter_params['gender'] = query_params['gender']
        if 'date_of_birth' in query_params:
            filter_params['date_of_birth'] = query_params['date_of_birth']

    results = lookup( query=query,
            index='users',
            fields=[
                "first_name",
                "last_name"
            ])
    
    user_ids = [hit.id for hit in results]
    users = User.objects.filter(id__in=user_ids)

    filterset = UserFilter(query_params, queryset=users)
    count = filterset.qs.count()
    resPage = 15
    paginator = PageNumberPagination()
    paginator.page_size = resPage

    queryset = paginator.paginate_queryset(filterset.qs, request)

    serializer = UserSerializer(queryset, many=True)
    return Response({"users": serializer.data, "per page": resPage, "count": count})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.GUEST, Roles.ADMIN)
def search_personals(request):
    query = request.GET.get('keyword')
    if not query:
        return Response("At least one keyword is required", status=status.HTTP_400_BAD_REQUEST)
    
    query_params = request.GET
    filter_params = {}
    if query_params:
        if 'gender' in query_params:
            filter_params['gender'] = query_params['gender']
        if 'date_of_birth' in query_params:
            filter_params['date_of_birth'] = query_params['date_of_birth']
        if 'country' in query_params:
            filter_params['country'] = query_params['country']

    results = lookup(
        query=query,
        index='personals',
        fields=['user.first_name', 'user.last_name', "phone", "about_us", "country", "bio"]
    )
    
    personal_ids = [hit.id for hit in results]
    personals = Personal.objects.filter(id__in=personal_ids).select_related('user')

    filterset = PersonalFilter(query_params, queryset=personals)
    count = filterset.qs.count()
    resPage = 15
    paginator = PageNumberPagination()
    paginator.page_size = resPage

    queryset = paginator.paginate_queryset(filterset.qs, request)

    serializer = PersonalMiniSerializer(queryset, many=True)
    return Response({"personals": serializer.data, "per page": resPage, "count": count})
