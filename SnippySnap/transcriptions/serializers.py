from rest_framework import serializers
from api import serializers as api_serializers
from . import models

class CorpusSerializer(api_serializers.BaseModelSerializer):

    class Meta:
        model = models.Corpus

class CollectionSerializer(api_serializers.BaseModelSerializer):

    class Meta:
        model = models.Collection

class StructureSerializer(api_serializers.BaseModelSerializer):

    class Meta:
        model = models.Structure

class WorkSerializer(api_serializers.BaseModelSerializer):

    class Meta:
        model = models.Work

class TranscriptionSerializer(api_serializers.BaseModelSerializer):

    class Meta:
        model = models.Transcription

class VerseSerializer(api_serializers.BaseModelSerializer):

    class Meta:
        model = models.Verse
