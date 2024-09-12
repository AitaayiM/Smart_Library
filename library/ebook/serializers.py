from rest_framework import serializers
from datetime import datetime
from .models import EBook, Review
from .utils import calculate_pages, extract_text_from_pdf

class EbookSerializer(serializers.ModelSerializer):

    reviews = serializers.SerializerMethodField(method_name='get_reviews', read_only=True)
    
    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data

    class Meta:
        model = EBook
        fields = ("id", "title", "summary", "category", "pages", "content", "published_at", "review_count", "reviews", "author")
        
    def create(self, validated_data):
        instance = super().create(validated_data)
        if instance.content:
            instance.pages = calculate_pages(instance.content)
            instance.content_txt = extract_text_from_pdf(instance.content)
            instance.save()
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.updated_at = datetime.now()
        if instance.content:
            instance.pages = calculate_pages(instance.content)
            instance.content_txt = extract_text_from_pdf(instance.content)
        return super().update(instance, validated_data)

class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = "__all__"