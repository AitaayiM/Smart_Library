from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
import ssl
import certifi

from identity.models import User

# Configuration SSL pour accepter les certificats auto-signés
context = ssl.create_default_context(cafile=certifi.where())

@registry.register_document
class UserDocument(Document):

    roles = fields.ObjectField(properties={
        "id": fields.IntegerField(),
        "name": fields.TextField(),
    })

    class Index:
        name = 'users'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    url = fields.TextField(attr='get_absolute_url')
    
    class Django:
        model = User
        fields = ['id', 'first_name', 'last_name', 'date_of_birth', 'gender']

    def get_queryset(self):
        return super(UserDocument, self).get_queryset().select_related('roles')

