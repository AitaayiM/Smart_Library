from elasticsearch_dsl import Search
from identity.models import User
from ebook.models import EBook
from elasticsearch_dsl import connections
from elasticsearch.helpers import bulk


def lookup(query, index, fields):
    if not query:
        return []
    # Connexion à Elasticsearch
    es = connections.get_connection()
    # Requête multi_match pour rechercher dans plusieurs champs
    s = Search(using=es, index=index)
    s = s.query("multi_match", query=query, fields=fields, fuzziness='AUTO')
    # Exécuter la recherche et récupérer les résultats
    response = s.execute()
    # Extraire les résultats de la recherche
    hits = response.hits
    return hits
