from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
import ssl
import certifi

from personality.models import Personal

# Configuration SSL pour accepter les certificats auto-signés
context = ssl.create_default_context(cafile=certifi.where())

@registry.register_document
class PersonalDocument(Document):
    user = fields.ObjectField(properties={
        "id": fields.IntegerField(),
        "first_name": fields.TextField(),
        "last_name": fields.TextField(),
        "date_of_birth": fields.DateField(),
        "gender": fields.TextField(),
    })

    class Index:
        name = 'personals'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    url = fields.TextField(attr='get_absolute_url')
    
    class Django:
        model = Personal
        fields = ['id', 'phone', 'about_us', 'country', 'bio', 'locked']

    def get_queryset(self):
        return super(PersonalDocument, self).get_queryset().select_related('user')
    