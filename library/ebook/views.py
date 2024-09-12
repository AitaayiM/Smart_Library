from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date
from .filters import EbookFilter
from rest_framework import status
from .models import EBook, Review
from identity.models import Roles
from identity.utils import role_required
from .serializers import EbookSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg

from rest_framework.parsers import FormParser, MultiPartParser
# Create your views here.

@api_view(['GET'])
def get_all_ebooks(request):
    try:
        filterset = EbookFilter(request.GET, queryset=EBook.objects.all().order_by('published_at'))
        count = filterset.qs.count()
        resPage = 15
        paginator = PageNumberPagination()
        paginator.page_size = resPage

        queryset = paginator.paginate_queryset(filterset.qs, request)
        serializer = EbookSerializer(queryset, many=True)
        return Response({"ebooks":serializer.data, "per page":resPage, "count":count})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.GUEST, Roles.ADMIN)
def get_by_id_ebook(request, pk):
    ebook = get_object_or_404(EBook, id=pk)
    serializer = EbookSerializer(ebook, many=False)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.ADMIN)
@parser_classes([MultiPartParser, FormParser])
def add_ebook(request):
    data = request.data
    if data.get("published_at") is None:
        data["published_at"] = date.today()
    serializer = EbookSerializer(data = data)

    if serializer.is_valid():
        # Extract the file from request.FILES
        content_file = request.FILES.get('content')
        # If a file is provided, assign it to the content field
        if content_file:
            if content_file.content_type not in ['application/pdf', 'application/epub+zip', 'application/vnd.amazon.ebook']:
                return Response({"error": "Invalid file format. Only PDF, EPUB, and MOBI formats are supported."}, status=status.HTTP_400_BAD_REQUEST)

            serializer.validated_data['content'] = content_file
        # Create the Ebook object
        serializer.save(author=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.ADMIN)
@parser_classes([MultiPartParser, FormParser])
def update_ebook(request, pk):
    ebook = get_object_or_404(EBook, id=pk)

    if ebook.author != request.user:
        return Response({"error":"Sorry you can't update this ebook"}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = EbookSerializer(instance=ebook, data=request.data, partial=True)
    if serializer.is_valid():
        # Extract the file from request.FILES
        content_file = request.FILES.get('content')
        if content_file:
            if content_file.content_type not in ['application/pdf', 'application/epub+zip', 'application/vnd.amazon.ebook']:
                return Response({"error": "Invalid file format. Only PDF, EPUB, and MOBI formats are supported."}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.validated_data['content'] = content_file

        updated_ebook = serializer.save()
        res = EbookSerializer(updated_ebook)
        return Response(res.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.ADMIN)
def delete_ebook(request, pk):
    ebook = get_object_or_404(EBook, id=pk)

    if ebook.author != request.user:
        return Response({"error":"Sorry you can't delete this ebook"}, status=status.HTTP_403_FORBIDDEN)
    
    Review.objects.filter(ebook=ebook).delete()
    ebook.delete()

    return Response({"details":"Delete ebook is done"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.GUEST, Roles.ADMIN)
def create_review(request, pk):
    user = request.user
    ebook = get_object_or_404(EBook, id=pk)
    data = request.data
    review = ebook.reviews.filter(user=user)

    if int(data['rating']) <= 0 or int(data['rating']) > 5:
        return Response({"error":"Please select between 10 to 5 only"}, status=status.HTTP_400_BAD_REQUEST)
    elif review.exists():
        new_review = {'rating':data['rating'], 'comment':data['comment']}
        review.update(**new_review)

        rating = ebook.reviews.aggregate(avg_ratings = Avg('rating'))
        ebook.ratings = rating['avg_ratings']
        ebook.save()
        return Response({"details":"Ebook review updated"})
    else:
        Review.objects.create(
            user= user,
            ebook= ebook,
            rating= data['rating'],
            comment= data['comment']
        )
        rating = ebook.reviews.aggregate(avg_ratings = Avg('rating'))
        ebook.ratings = rating['avg_ratings']
        ebook.save()
        return Response({'details':'Ebook review created'})
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@role_required(Roles.WRITER, Roles.READER, Roles.GUEST, Roles.ADMIN)
def delete_review(request, pk):
    user = request.user
    ebook = get_object_or_404(EBook, id=pk)
    review = ebook.reviews.filter(user=user)

    if review.exists():
        review.delete()
        rating = ebook.reviews.aggregate(avg_ratings = Avg('rating'))
        if rating['avg_ratings'] is None:
            rating['avg_ratings'] = 0
            ebook.ratings = rating['avg_ratings']
            ebook.save()
            return Response({'details':'Ebook review deleted'})
    else:
        return Response({'error':'Review not found'}, status=status.HTTP_404_NOT_FOUND)
    

