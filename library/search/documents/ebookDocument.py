from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
import ssl
import certifi

from ebook.models import EBook

# Configuration SSL pour accepter les certificats auto-signés
context = ssl.create_default_context(cafile=certifi.where())

@registry.register_document
class EbookDocument(Document):
    author = fields.ObjectField(properties={
        "id": fields.IntegerField(),
        "first_name": fields.TextField(),
        "last_name": fields.TextField(),
    })

    class Index:
        name = 'ebooks'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    url = fields.TextField(attr='get_absolute_url')
    
    class Django:
        model = EBook
        fields = ['id', 'title', 'summary', 'category', 'content_txt']

    def get_queryset(self):
        return super(EbookDocument, self).get_queryset().select_related('author')
