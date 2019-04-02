from django.db import models
from api.models import BaseModel
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField




class Collection (models.Model):

    AVAILABILITY = 'public'

    SERIALIZER = 'CollectionSerializer'

    identifier = models.TextField('identifier')
    name = models.TextField('name')
    abbreviation = models.TextField('abbreviation')

    def __str__(self):
        return self.abbreviation

    def getSerializationFields():
        fields = '__all__'
        return fields

    def get_fields():
        data = {}
        fields = list(Collection._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

class Work (models.Model):

    AVAILABILITY = 'public'

    SERIALIZER = 'WorkSerializer'

    identifier = models.TextField('identifier')
    name = models.TextField('name')
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, null=True)
    sort_value = models.IntegerField('sort_value')
    abbreviation = models.TextField('abbreviation')

    class Meta:
        ordering = ['sort_value']

    def getSerializationFields():
        fields = '__all__'
        return fields

    def get_fields():
        data = {}
        fields = list(Work._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

class Corpus (models.Model):

    AVAILABILITY = 'public'

    SERIALIZER = 'CorpusSerializer'

    identifier = models.TextField('identifier')
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, null=True)
    language = models.TextField('language')
    works = models.ManyToManyField(Work, through='Structure')

    def getSerializationFields():
        fields = '__all__'
        return fields

    def get_fields():
        data = {}
        fields = list(Corpus._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

class Structure (models.Model):

    AVAILABILITY = 'public'

    SERIALIZER = 'StructureSerializer'

    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    corpus = models.ForeignKey(Corpus, on_delete=models.CASCADE)
    position_in_corpus = models.IntegerField('position_in_corpus')
    total_chapters = models.IntegerField('chapter_total')
    verses_per_chapter = JSONField('verses_per_chapter')
    abbreviation = models.TextField('abbreviation')

    def getSerializationFields():
        fields = '__all__'
        return fields

    def get_fields():
        data = {}
        fields = list(Collection._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data


#TODO: think about how you can have transcriptions of a document and if that is really needed
#TODO: consider if it is safe to expose 'source' in the api
class Transcription (models.Model):

    AVAILABILITY = 'public_or_user'

    PREFETCH_KEYS = ['verses']
    RELATED_KEYS = ['work', 'user']

    SERIALIZER = 'TranscriptionSerializer'

    identifier = models.TextField('identifier', unique=True)
    corpus = models.ForeignKey(Corpus, on_delete=models.PROTECT, null=True)
    document_id = models.CharField('document_id', max_length=25)
    tei = models.TextField('tei')
    source = models.TextField('source')
    siglum = models.CharField('siglum', max_length=25)
    document_type = models.TextField('document_type')
    language = models.CharField('language', max_length=5)
    corrector_order = ArrayField(models.CharField(max_length=50), null=True)
    total_verses = models.IntegerField('total_verses')
    total_unique_verses = models.IntegerField('total_verses')
    user = models.ForeignKey(User, models.PROTECT, null=True)
    work = models.ForeignKey('Work', models.PROTECT, related_name="transcriptions")
    loading_complete = models.NullBooleanField('loading_complete')
    public = models.BooleanField('public')
    #manuscript Foreign key to MS?

    def getSerializationFields():
        fields = '__all__'
        return fields

    def get_fields():
        data = {}
        fields = list(Transcription._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

    def __str__(self):
        return self.identifier

class Verse (models.Model):

    AVAILABILITY = 'public_or_user'

    RELATED_KEYS = ['transcription', 'work', 'user']

    SERIALIZER = 'VerseSerializer'


    identifier = models.TextField('identifier')
    index = models.IntegerField('index')
    document_id = models.CharField('document_id', max_length=25)
    tei = models.TextField('tei')
    context = models.TextField('context')
    reference = models.TextField('reference')
    #book_number = models.IntegerField('book_number')
    chapter_number = models.IntegerField('chapter_number', null=True)
    verse_number = models.IntegerField('verse_number', null=True)
    siglum = models.CharField('siglum', max_length=25)
    document_type = models.TextField('document_type')
    language = models.CharField('language', max_length=5)
    duplicate_position = models.IntegerField('duplicate_position', null=True)
    lection = models.TextField('lection')
    transcription = models.ForeignKey('Transcription', models.CASCADE, related_name="verses")
    transcription_siglum = models.TextField('transcription_siglum')
    transcription_identifier = models.TextField('transcription_identifier')
    user = models.ForeignKey(User, models.PROTECT, null=True)
    work = models.ForeignKey('Work', models.PROTECT, related_name="verse_details")
    inscriptio = models.NullBooleanField('inscriptio')
    subscriptio = models.NullBooleanField('subscriptio')
    witnesses = JSONField(null=True)
    public = models.BooleanField('public')

    class Meta:
        ordering = ['work__sort_value', 'chapter_number', 'verse_number']

    def getSerializationFields():
        fields = '__all__'
        return fields

    def get_fields():
        data = {}
        fields = list(Verse._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

# class PrivateTranscription (models.Model):
#
#     PREFETCH_KEYS = ['verses']
#     RELATED_KEYS = ['work', 'user']
#
#     SERIALIZER = 'TranscriptionSerializer'
#
#     identifier = models.TextField('identifier', unique=True)
#     corpus = models.TextField('corpus')
#     document_id = models.TextField('document_id')
#     tei = models.TextField('tei')
#     source = models.TextField('source')
#     siglum = models.TextField('siglum')
#     document_type = models.TextField('document_type')
#     language = models.CharField('language', max_length=5)
#     corrector_order = ArrayField(models.TextField(), null=True)
#     total_verses = models.IntegerField('total_verses')
#     total_unique_verses = models.IntegerField('total_verses')
#     user = models.ForeignKey(User)
#     work = models.ForeignKey('Work', models.PROTECT, related_name="private_transcriptions")
#     loading_complete = models.NullBooleanField('loading_complete')
#     #manuscript Foreign key to MS?
#
#     def getSerializationFields():
#         fields = '__all__'
#         return fields
#
#     def get_fields():
#         data = {}
#         fields = list(Transcription._meta.get_fields(include_hidden=True))
#         for field in fields:
#             data[field.name] = field.get_internal_type()
#         return data
#
#     def __str__(self):
#         return self.identifier
#
# class PrivateVerse (models.Model):
#
#     RELATED_KEYS = ['transcription', 'work', 'user']
#
#     SERIALIZER = 'VerseSerializer'
#
#
#     identifier = models.TextField('identifier')
#     index = models.IntegerField('index')
#     document_id = models.CharField('document_id', max_length=25)
#     tei = models.TextField('tei')
#     context = models.TextField('context')
#     reference = models.TextField('reference')
#     #book_number = models.IntegerField('book_number')
#     chapter_number = models.IntegerField('chapter_number', null=True)
#     verse_number = models.IntegerField('verse_number', null=True)
#     siglum = models.CharField('siglum', max_length=25)
#     document_type = models.TextField('document_type')
#     language = models.CharField('language', max_length=5)
#     duplicate_position = models.IntegerField('duplicate_position', null=True)
#     lection = models.TextField('lection')
#     transcription = models.ForeignKey('PrivateTranscription', models.CASCADE, related_name="verses")
#     transcription_siglum = models.TextField('transcription_siglum')
#     user = models.ForeignKey(User)
#     work = models.ForeignKey('Work', models.PROTECT, related_name="private_verse_details")
#     inscriptio = models.NullBooleanField('inscriptio')
#     subscriptio = models.NullBooleanField('subscriptio')
#     witnesses = JSONField(null=True)
#
#
#     class Meta:
#         ordering = ['work__book_number', 'chapter_number', 'verse_number']
#
#     def getSerializationFields():
#         fields = '__all__'
#         return fields
#
#     def get_fields():
#         data = {}
#         fields = list(Verse._meta.get_fields(include_hidden=True))
#         for field in fields:
#             data[field.name] = field.get_internal_type()
#         return data

class VerseReading (models.Model):

    AVAILABILITY= 'public'

    RELATED_KEYS = ['verse']

    verse = models.ForeignKey(Verse, models.CASCADE, related_name="verse_readings")
    hand = models.TextField()
    hand_abbreviation = models.TextField()
    reading_text = models.TextField()

    def get_fields():
        data = {}
        fields = list(VerseReading._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data


#also MS and pages need adding and all those links working
