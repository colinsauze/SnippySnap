from django.db import models
from django.db import connections
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.db.models.sql.compiler import SQLCompiler
from rest_framework import serializers
from api.models import BaseModel
from transcriptions.models import Work as BiblicalWork
from simple_history.models import HistoricalRecords


"""This contains all the models used by our citation system.

The three classes at the top are used to redefine the SQL Manager to make sure null values always come last when sorting
I have not yet found an equivalent way of making empty strings which is annoying and would be good for the future

The model classes have some static variables which are used elsewhere (to reduce hardcoding in the views for example)
This is a list of all possible and required static variables and what they do.

* LIST_FIELDS           required for models to be displayed in the list view
                        A list of fields to display in the 'list view' of the model
                        A dictionary can be used if the database field name is different from the column label for display and/or the search string required (for example when searching related models or array fields)
                        or the sort string for the arrows at the top of the columns
                        keys for dictionary are 'id', 'label', 'sort' and 'search' respectively. 'label', 'sort' and 'search' will default to 'id' if not provided
                        If all three values are the same a string can be provided instead of a dictionary

* RELATED_KEYS          advised for models which contain foreign key relations as it reduces database calls
                        A list of all fields that are foreign keys in this model

* PREFETCH_KEYS         advised for models with many to many or one to many relations (these may be declared with a foreign key in the related model only) as it reduces database calls
                        A list of all many-to-many or one-to-many keys in the model

* SERIALIZER            required for all models
                        A string representing the serializer class for this model (must also be added to the ciations.serializers file)

* REQUIRED_FIELDS       required for all models (that need to be created via the api)
                        A list of the fields required to be present when an item of this model is created


"""



#these first three classes redefine the SQL Manager so that nulls always come last when sorting
#code from http://stackoverflow.com/a/35494930/6047232
#I would like something similar for empty strings but have not found anything
class NullsLastSQLCompiler(SQLCompiler):
    def get_order_by(self):
        result = super().get_order_by()
        if result and self.connection.vendor == 'postgresql':
            return [(expr, (sql + ' NULLS LAST', params, is_ref))
                    for (expr, (sql, params, is_ref)) in result]
        return result


class NullsLastQuery(models.sql.query.Query):
    """Use a custom compiler to inject 'NULLS LAST' (for PostgreSQL)."""

    def get_compiler(self, using=None, connection=None):
        if using is None and connection is None:
            raise ValueError("Need either using or connection")
        if using:
            connection = connections[using]
        return NullsLastSQLCompiler(self, connection, using)


class NullsLastQuerySet(models.QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self.query = query or NullsLastQuery(self.model)

#     def __str__(self):
#         return "%s: %s" % (self.abbreviation, self.full_name)


class Author (BaseModel):
    """A Patristic Author"""

    AVAILABILITY =  'public'

    LIST_FIELDS = [
                   'abbreviation',
                   {'id': 'full_name', 'label': 'Full Name'},
                   'clavis',
                   {'id': 'century_active', 'label': 'Century Active'},
                   'pseudonymous',
                   {'id': 'anonymous_collective', 'label': 'Anonymous'},
                   {'id': 'translated_source', 'label': 'Translated'},
                    'obsolete'
                    ]

    ITEM_FIELDS = ['full_name', 'abbreviation', 'biblindex_identifiers', 'place', 'born', 'died', 'century_active',
                   'clavis', 'language', 'pseudonymous', 'anonymous_collective', 'transmitted_by_another',
                   'translated_source', 'comments']

    SERIALIZER = 'AuthorSerializer'
    REQUIRED_FIELDS = ['abbreviation', 'language']

    #PREFETCH_KEYS = ['works']

    identifier = models.TextField('Identifier', blank=True)
    abbreviation = models.TextField('Abbreviation', unique=True)
    biblindex_identifiers = ArrayField(models.TextField(), null=True, verbose_name='Biblindex identifiers')
    biblia_patristica_identifiers = ArrayField(models.TextField(), null=True, verbose_name='Biblia patristica identifiers')
    full_name = models.TextField('Full Name', blank=True)
    born = models.IntegerField('Born', null=True)
    born_is_approximate = models.NullBooleanField('Born approximate')
    died = models.IntegerField('Died', null=True)
    died_is_approximate = models.NullBooleanField('Died approximate')
    language = models.TextField('Language', choices=(('grc', 'Greek'), ('lat', 'Latin')) )
    century_active = models.IntegerField('Century Active', null=True)
    clavis = models.TextField('Clavis', blank=True)
    place = models.TextField('Place', blank=True)
    pseudonymous = models.NullBooleanField('Pseudonymous')
    anonymous_collective = models.NullBooleanField('Anonymous')
    transmitted_by_another = models.NullBooleanField('Transmitted in Another')
    translated_source = models.NullBooleanField('Translated')
    obsolete = models.NullBooleanField('Obsolete')
    comments = models.TextField('Comments', blank=True)
    created_for_biblindex = models.NullBooleanField('created_for_biblindex')
    history = HistoricalRecords()

    def getSerializationFields():
        fields = '__all__'
        return fields

    def __str__(self):
        if len(self.abbreviation) > 0 and len(self.full_name) > 0:
            return '%s: %s' % (self.abbreviation, self.full_name)
        else:
            return self.abbreviation

    def get_abbreviation(self):
        return self.abbreviation

    class Meta:
        ordering = ['abbreviation']

    def get_fields():
        data = {}
        fields = list(Author._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

    def get_search_fields(inc_related=False):
        search_fields = ['abbreviation', 'biblindex_identifiers', 'full_name',
                         'clavis', 'century_active', 'language', 'place',
                         'pseudonymous', 'anonymous_collective',
                         'transmitted_by_another', 'translated_source']
        fields = list(Author._meta.get_fields())
        data = []
        for field in fields:
            if field.name in search_fields:
                data.append({'id': field.name,
                             'label': field.verbose_name,
                             'field_type': field.get_internal_type(),
                             'position': search_fields.index(field.name)})
        return sorted(data, key=lambda k: k['position'])

    def get_row_dict(self):
        return [{'label': field.verbose_name, 'value': field.value_from_object(self), 'id': field.name, 'field_type': field.get_internal_type()} for field in Author._meta.fields]

    #use the redefined SQL Manager
    objects = NullsLastQuerySet.as_manager()

#to access reverse relations such as all the works by the current author do
#author.work_set.all() this gives you a query set (and can be filtered etc like the other query sets


class Work (BaseModel):
    """A Patristic Work"""

    AVAILABILITY =  'public'

    LIST_FIELDS = [
                   {'id': 'author', 'search': 'author__abbreviation', 'sort': 'author__abbreviation', 'label': 'Author'},
                   'abbreviation', 'title', 'clavis', 'obsolete',
                   ]

    ITEM_FIELDS = ['author', 'abbreviation', 'title', 'biblindex_identifiers', 'clavis', 'language',
                   'year', 'translated_source', 'transmitted_in_another', 'comments']

    RELATED_KEYS = ['author']
    PREFETCH_KEYS = ['citations', 'citations__biblical_work']

    SERIALIZER = 'WorkSerializer'
    REQUIRED_FIELDS = ['abbreviation', 'language', 'other_possible_authors']

    identifier = models.TextField('Identifier', blank=True)
    abbreviation = models.TextField('Abbreviation')
    biblindex_identifiers = ArrayField(models.TextField(), null=True, verbose_name='Biblindex identifiers')
    biblia_patristica_identifiers = ArrayField(models.TextField(), null=True, verbose_name='Biblica patristica identifiers')
    author = models.ForeignKey("Author", on_delete=models.PROTECT, verbose_name='Author', related_name='works')
    other_possible_authors = models.ManyToManyField(Author, blank=True, related_name='Authors', verbose_name='Other Possible Authors')
    title = models.TextField('Title', blank=True)
    language = models.TextField('Language', choices=(('grc', 'Greek'), ('lat', 'Latin')) )
    year = models.IntegerField('Year', null=True)
    year_is_approximate = models.NullBooleanField('Year approximate')
    clavis = models.TextField('Clavis', blank=True)
    translated_source = models.NullBooleanField('Translated')
    transmitted_in_another = models.NullBooleanField('Transmitted in Another')
    obsolete = models.NullBooleanField('Obsolete')
    comments = models.TextField('Comments', blank=True)
    created_for_biblindex = models.NullBooleanField('created_for_biblindex')
    history = HistoricalRecords()

    class Meta:
        ordering = ['abbreviation']

    def getSerializationFields():
        fields = '__all__'
        return fields

    def __str__(self):
        if len(self.abbreviation) > 0 and len(self.title) > 0:
            return '%s: %s' % (self.abbreviation, self.title)
        elif len(self.abbreviation) > 0:
            return self.abbreviation
        elif len(self.title) > 0:
            return self.title
        else:
            return str(self.id)

    def get_row_dict(self):
        data = []
        for field in Work._meta.fields:
            if field.is_relation:
                value = getattr(self, field.name)
            else:
                value = field.value_from_object(self)
            data.append({'label': field.verbose_name,
                         'value': value,
                         'id': field.name,
                         'field_type': field.get_internal_type()})
        return data

    def get_fields():
        data = {}
        fields = list(Work._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

    def get_search_fields(inc_related=False):
        #this search fields list must be maximal including all related in order as the position is used for sorting and also we filter on this below
        search_fields = ['abbreviation', 'author__abbreviation',
                         'author__full_name', 'author__century_active',
                         'biblindex_identifiers', 'title', 'clavis', 'language',
                         'year', 'translated_source', 'transmitted_in_another']
        fields = list(Work._meta.get_fields())
        data = []
        for field in fields:
            if field.name in search_fields:
                data.append({'id': field.name,
                             'label': field.verbose_name,
                             'field_type': field.get_internal_type(),
                             'position': search_fields.index(field.name)})
        if inc_related:
            related_fields = Author.get_search_fields()
            for field in related_fields:
                #filter so we only get sensible ones
                if 'author__%s' % field['id'] in search_fields:
                    data.append({'id': 'author__%s' % field['id'],
                                 'label': 'Author, ' + field['label'],
                                 'field_type': field['field_type'],
                                 'position': search_fields.index('author__%s' % field['id'])})
        return sorted(data, key=lambda k: k['position'])

    objects = NullsLastQuerySet.as_manager()


class Series (BaseModel):

    AVAILABILITY =  'public'

    LIST_FIELDS = [
                   'abbreviation', 'title'
                   ]

    ITEM_FIELDS = [
                   'abbreviation', 'title', 'comments'
                   ]

    SERIALIZER = 'SeriesSerializer'
    REQUIRED_FIELDS = ['abbreviation']

    PREFETCH_KEYS = ['editions', 'editions__work']

    identifier = models.TextField('Identifier')
    abbreviation = models.TextField('Abbreviation')
    title = models.TextField('Title', blank=True)
    comments = models.TextField('Comments', blank=True)
    history = HistoricalRecords()

    def getSerializationFields():
        fields = '__all__'
        return fields

    def __str__(self):
        if self.abbreviation != '':
            return self.abbreviation
        else:
            return self.title

    class Meta:
        ordering = ['abbreviation']

    def get_row_dict(self):
        data = []
        for field in Series._meta.fields:

            data.append({'label': field.verbose_name,
                            'value': field.value_from_object(self),
                            'id': field.name,
                            'field_type': field.get_internal_type()})
        return data

    def get_fields():
        data = {}
        fields = list(Series._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

    def get_search_fields(inc_related=False):
        search_fields = ['abbreviation', 'title']
        fields = list(Series._meta.get_fields())
        data = []
        for field in fields:
            if field.name in search_fields:
                data.append({'id': field.name,
                             'label': field.verbose_name,
                             'field_type': field.get_internal_type(),
                             'position': search_fields.index(field.name)})
        return sorted(data, key=lambda k: k['position'])

    objects = NullsLastQuerySet.as_manager()


class OnlineCorpus (BaseModel):

    AVAILABILITY =  'public'

    LIST_FIELDS = [
                   'abbreviation', 'title', 'url', 'access'
                   ]

    ITEM_FIELDS = [
                   'abbreviation', 'title', 'url', 'access', 'comments'
                   ]

    SERIALIZER = 'OnlineCorpusSerializer'
    REQUIRED_FIELDS = ['abbreviation']

    PREFETCH_KEYS = ['editions', 'citations']

    identifier = models.TextField('Identifier')
    abbreviation = models.TextField('Abbreviation')
    title = models.TextField('Title', blank=True)
    url = models.TextField('URL', blank=True)
    access = models.TextField('Access', blank=True)
    comments = models.TextField('Comments', blank=True)
    history = HistoricalRecords()

    def __str__(self):
        if self.abbreviation != '':
            return self.abbreviation
        else:
            return self.title

    class Meta:
        ordering = ['abbreviation']

    def getSerializationFields():
        fields = '__all__'
        return fields

    def get_row_dict(self):
        return [{'label': field.verbose_name, 'value': field.value_from_object(self), 'id': field.name, 'field_type': field.get_internal_type()} for field in OnlineCorpus._meta.fields]

    def get_fields():
        data = {}
        fields = list(OnlineCorpus._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

    objects = NullsLastQuerySet.as_manager()


class Edition (BaseModel):

    AVAILABILITY =  'public'

    LIST_FIELDS = [
                   {'id': 'work__author', 'search': 'work__author__abbreviation', 'sort': 'work__author__abbreviation', 'label': 'Author'},
                   {'id': 'work', 'search': 'work__abbreviation', 'sort': 'work__abbreviation'},
                   'year', 'editor',
                   {'id': 'series', 'search': 'series__abbreviation', 'sort': 'series__abbreviation'}, 'volume',
                   {'id': 'independent_title', 'label': 'Title'}
                   ]

    ITEM_FIELDS = ['work', 'editor', 'year', 'place', 'independent_title', 'series', 'volume',
                   'onlinecorpus', 'page_information', 'legacy_edition', 'superseded', 'comments']

    RELATED_KEYS = ['work__author', 'work', 'series', 'onlinecorpus']

    SERIALIZER = 'EditionSerializer'
    REQUIRED_FIELDS = ['work', 'onlinecorpus', 'series']

    PREFETCH_KEYS = ['citations', 'citations__biblical_work', 'citations__work', 'citations__work__author']

    """An Edition of a Patristic Work"""
    identifier = models.TextField('Identifier', blank=True)
    work = models.ForeignKey("Work", models.PROTECT, verbose_name='Work', related_name='editions')
    series = models.ForeignKey("Series", models.PROTECT, null=True, verbose_name='Series', related_name='editions')
    onlinecorpus = models.ForeignKey("OnlineCorpus", models.PROTECT,  null=True, verbose_name='OnlineCorpus', related_name='editions')
    editor = models.TextField('Editor', blank=True)
    year = models.IntegerField('Year', null=True)
    place = models.TextField('Place', blank=True)
    volume = models.TextField('Volume', blank=True)
    independent_title = models.TextField('Title', blank=True)
    superseded = models.NullBooleanField('Superseded')
    page_information = models.TextField('Page', blank=True)
    bham_shelfmark = models.TextField('Bham Shelfmark', blank=True)
    legacy_edition = models.TextField('Edition (legacy format)', blank=True)
    comments = models.TextField('Comments', blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['identifier']

    def getSerializationFields():
        fields = '__all__'
        return fields

    def __str__(self):
        edition_list = []
        #edition_list.append(self.work.__str__())
        if self.editor != '':
            edition_list.append(self.editor)
        if self.year:
            edition_list.append('(%s)' % self.year)
        if self.independent_title != '':
            edition_list.append('%s.' % self.independent_title)
        if self.place != '':
            edition_list.append('%s.' % self.place)
        series_string = self.series.__str__()
        if series_string != '' and series_string.lower() != 'no series' and series_string.lower() != 'not in a series':
            if self.volume != '':
                edition_list.append('%s:%s' % (series_string, self.volume))
            else:
                edition_list.append(series_string)
        if self.superseded:
            edition_list.append('(superseded)')
        if len(edition_list) == 0:
            edition_list.append(self.identifier)
        return ' '.join(edition_list)

    def get_row_dict(self):
        data = []
        for field in Edition._meta.fields:
            if field.is_relation:
                value = getattr(self, field.name)
            else:
                value = field.value_from_object(self)
            data.append({'label': field.verbose_name,
                         'value': value,
                         'id': field.name,
                         'field_type': field.get_internal_type()})
        return data

    def get_fields():
        data = {}
        fields = list(Edition._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

    def get_search_fields(inc_related=False):
        search_fields = ['editor', 'independent_title', 'year',
                         'work__author__abbreviation',
                         'work__author__full_name',
                         'work__abbreviation', 'work__title',
                         'work__clavis', 'work__language', 'series__abbreviation',
                         'series__title']
        fields = list(Edition._meta.get_fields())
        data = []
        for field in fields:
            if field.name in search_fields:
                data.append({'id': field.name,
                             'label': field.verbose_name,
                             'field_type': field.get_internal_type(),
                             'position': search_fields.index(field.name)})
        if inc_related:
            related_fields = Author.get_search_fields(False)
            for field in related_fields:
                if 'work__author__%s' % field['id'] in search_fields:
                    data.append({'id': 'work__author__%s' % field['id'],
                                 'label': 'Author, ' + field['label'],
                                 'field_type': field['field_type'],
                                 'position': search_fields.index('work__author__%s' % field['id'])})
            related_fields = Work.get_search_fields(False)
            for field in related_fields:
                if 'work__%s' % field['id'] in search_fields:
                    data.append({'id': 'work__' + field['id'],
                                 'label': 'Work, ' + field['label'],
                                 'field_type': field['field_type'],
                                 'position': search_fields.index('work__%s' % field['id'])})
            related_fields = Series.get_search_fields(False)
            for field in related_fields:
                if 'series__%s' % field['id'] in search_fields:
                    data.append({'id': 'series__' + field['id'],
                                 'label': 'Series, ' + field['label'],
                                 'field_type': field['field_type'],
                                 'position': search_fields.index('series__%s' % field['id'])})
        return sorted(data, key=lambda k: k['position'])

    objects = NullsLastQuerySet.as_manager()


class Project (models.Model):

    AVAILABILITY =  'public'

    identifier = models.TextField('Identifier', unique=True)
    name = models.TextField('Name')
    biblical_work = models.ForeignKey(BiblicalWork, on_delete=models.PROTECT, verbose_name='Biblical work', null=True)
    language = models.TextField('Language')
    author_ids = models.ManyToManyField(Author)
    form_settings = JSONField(null=True)
    submit_settings = JSONField(null=True)
    edition_lookup = JSONField(null=True)
    preselects = JSONField(null=True)
    base_text_siglum = models.TextField('Base text siglum')
    base_text_label = models.TextField('Base text label')
    online_transcribers = models.ManyToManyField(User, related_name='online_transcribers')
    edition_transcribers = models.ManyToManyField(User, related_name='edition_transcribers')
    public = models.BooleanField('Public')
    sources = ArrayField(models.TextField(), null=True, verbose_name='Sources')

    def getSerializationFields():
        fields = '__all__'
        return fields

    def get_fields():
        data = {}
        fields = list(Project._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data


class Citation (BaseModel):

    AVAILABILITY = 'public'

    LIST_FIELDS = [
                   {'id': 'biblical_reference', 'label': 'Ref', 'search': 'biblical_reference', 'sort': 'biblical_reference_sortable'},
                   {'id': 'work__author', 'search': 'work__author__abbreviation', 'sort': 'work__author__abbreviation', 'label': 'Author'},
                   {'id': 'work', 'search': 'work__abbreviation'},
                   {'id': 'work_reference', 'label': 'Work Ref'},
                   {'id': 'page_reference', 'label': 'Page'},
                   {'id': 'line_reference', 'label': 'Line'},
                   {'id': 'citation_text', 'label': 'Text'},
                   'comments'
                   ]

    ITEM_FIELDS = ['biblical_reference', 'work', 'work_reference', 'citation_text', 'citation_type', 'citation_reference_type',
                   'edition', 'page_reference', 'line_reference', 'onlinecorpus',  'manuscript_info', 'manuscript_variants',
                   'biblical_catena', 'biblical_parallels', 'status', 'sources', 'comments', 'dependencies_string']

    RELATED_KEYS = ['work', 'onlinecorpus', 'work__author', 'edition', 'biblical_work']
    PREFETCH_KEYS = ['dependencies']

    SERIALIZER = 'CitationSerializer'
    REQUIRED_FIELDS = ['work', 'language', 'biblical_work', 'chapter', 'verse', 'biblical_reference']

    language = models.TextField('Language', choices = (('grc', 'Greek'), ('lat', 'Latin')) )
    biblical_work = models.ForeignKey(BiblicalWork, on_delete=models.PROTECT, verbose_name='Biblical work')
    chapter = models.IntegerField('Chapter')
    verse = models.IntegerField('Verse')
    #this next two fields are not edited or even stored in the editing form they are generated when the form is serialised
    biblical_reference = models.TextField('Ref')
    biblical_reference_sortable = models.IntegerField('Sortable Ref')
    work = models.ForeignKey("Work", on_delete=models.PROTECT, verbose_name='Work', related_name='citations')
    work_reference = models.TextField('Work ref', blank=True)
    edition = models.ForeignKey("Edition", on_delete=models.PROTECT, null=True, verbose_name='Edition', related_name='citations')
    page_reference = models.TextField('Page', blank=True)
    line_reference = models.TextField('Line', blank=True)
    onlinecorpus = models.ForeignKey("OnlineCorpus", on_delete=models.PROTECT, null=True, verbose_name='OnlineCorpus', related_name='citations')
    citation_type = models.TextField('Citation type') #'ALL', u'CAPITULUM', u'LEMMA', u'CIT', u'ADAPT', u'REM'
    citation_reference_type = models.TextField('Reference type', blank=True)#reference, possible reference, no reference, reference not found
    citation_text = models.TextField('Citation text', blank=True)
    search_string = models.TextField('Search string', blank=True)
    #this is a legacy protection field which should never be created in new data
    #for existing Latin it may slowly be replaced with manuscript_variants
    #existing greek transcriptions were multi-transcribed for each MSS witness so this will remain for them
    manuscript_info = models.TextField('MS info', blank=True)
    manuscript_variants = JSONField('MS variants', null=True)

    #ordered
    biblical_catena = ArrayField(models.TextField(), null = True, verbose_name='Biblical catena')

    #this is a legacy protection field which should never be created in new data
    #and may gradually become replaced with dependencies for old data too
    dependencies_string = models.TextField('Dependencies string', blank=True)
    #dependencies ManyToMany see dependency object

    #unordered
    biblical_parallels = ArrayField(models.TextField(), null = True, verbose_name='Biblical parallels') #BKV for new ones on drop downs
    work_reference_sortable = models.BigIntegerField('work_reference_sortable', null=True) #puts things in right order for printed output
    comments = models.TextField('Comments', blank=True)
    status = models.TextField('Status')
    sources = ArrayField(models.TextField(), null=True, verbose_name='Sources')

    corrections_required = models.NullBooleanField('Corrections required')
    correction_notes = models.TextField('Correction notes', blank=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ['biblical_work__sort_value', 'chapter',
                    'verse', 'work__author__identifier',
                    'work__identifier', 'id']

    def __str__(self):
        return '%s %s:%s in %s, %s' % (self.biblical_work.name, self.chapter, self.verse, self.work.author, self.work)

    def getSerializationFields():
        fields = '__all__'
        return fields

    def get_row_dict(self):
        data = []
        for field in Citation._meta.fields:
            if field.is_relation:
                value = getattr(self, field.name)
            else:
                value = field.value_from_object(self)
            data.append({'label': field.verbose_name,
                         'value': value,
                         'id': field.name,
                         'field_type': field.get_internal_type()})
        return data

    def get_fields():
        data = {}
        fields = list(Citation._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

    def get_search_fields(inc_related=False):
        search_fields = [ 'biblical_work__identifier',
                         'chapter', 'verse',
                         'language', 'citation_text',
                         'work__author__abbreviation',
                         'work__author__full_name',
                         'work__abbreviation', 'work__title', 'work__clavis']
        fields = list(Citation._meta.get_fields())
        data = []
        data.append({'id': 'biblical_work__identifier',
                    'label': 'Biblical book',
                    'field_type': 'IntegerField',
                    'position': search_fields.index('biblical_work__identifier')})
        for field in fields:
            if field.name in search_fields:
                data.append({'id': field.name,
                             'label': field.verbose_name,
                             'field_type': field.get_internal_type(),
                             'position': search_fields.index(field.name)})
        if inc_related:
            related_fields = Author.get_search_fields(False)
            for field in related_fields:
                if 'work__author__%s' % field['id'] in search_fields:
                    data.append({'id': 'work__author__' + field['id'],
                             'label': 'Author, ' + field['label'],
                             'field_type': field['field_type'],
                             'position': search_fields.index('work__author__%s' % field['id'])})
            related_fields = Work.get_search_fields(False)
            for field in related_fields:
                if 'work__%s' % field['id'] in search_fields:
                    data.append({'id': 'work__' + field['id'],
                             'label': 'Work, ' + field['label'],
                             'field_type': field['field_type'],
                             'position': search_fields.index('work__%s' % field['id'])})
#             related_fields = Edition.get_search_fields(False)
#             for field in related_fields:
#                 if 'edition__%s' % field['id'] in search_fields:
#                     data.append({'id': 'edition__' + field['id'],
#                              'label': 'Edition, ' + field['label'],
#                              'field_type': field['field_type']})
        return sorted(data, key=lambda k: k['position'])



class Dependency (models.Model):

    AVAILABILITY =  'public'

    SERIALIZER = 'DependencySerializer'

    relation_type = models.TextField('Relation type', blank=True)
    author = models.ForeignKey("Author", on_delete=models.PROTECT,  verbose_name='Author', null=True)
    work = models.ForeignKey("Work", on_delete=models.PROTECT, verbose_name='Work', null=True, blank=True)
    work_reference = models.TextField('Work ref', blank=True)
    #we can cascade this one because if we delete the citation that it is part of we no longer need the dependency
    citation = models.ForeignKey(Citation, on_delete=models.CASCADE, related_name="dependencies", null=True)
    history = HistoricalRecords()

    def __str__(self):
        return '%s %s in %s, %s' % (self.relation_type, self.author, self.work, self.work_reference)

class PrivateCitation (BaseModel):

    AVAILABILITY =  'private'

    LIST_FIELDS = [
                   {'id': 'biblical_reference', 'label': 'Ref', 'search': 'biblical_reference', 'sort': 'biblical_reference_sortable'},
                   {'id': 'author', 'search': 'work__author__abbreviation', 'sort': 'work__author__abbreviation'},
                   {'id': 'work', 'search': 'work__abbreviation', 'sort': 'work__abbreviation'},
                   {'id': 'work_reference', 'label': 'Work Ref' },
                   {'id': 'page_reference', 'label': 'Page'},
                   {'id': 'line_reference', 'label': 'Line'},
                   {'id': 'citation_text', 'label': 'Text'},
                   'comments', 'status',
                   {'id': 'created_by', 'label': 'Transcriber'},
                   {'id': 'created_time', 'label': 'Date'}
                   ]
    RELATED_KEYS = ['work', 'onlinecorpus']
    PREFETCH_KEYS = ['dependencies']

    SERIALIZER = 'PrivateCitationSerializer'
    REQUIRED_FIELDS = ['work', 'language', 'biblical_work', 'chapter', 'verse', 'biblical_reference']

    ITEM_FIELDS = ['biblical_reference', 'work', 'work_reference', 'citation_text', 'citation_type', 'citation_reference_type',
                   'edition', 'page_reference', 'line_reference', 'onlinecorpus',  'manuscript_info', 'manuscript_variants',
                   'biblical_catena', 'biblical_parallels', 'status', 'sources', 'comments', 'private_comments', 'dependencies_string']


    language = models.TextField('Language', choices = (('grc', 'Greek'), ('lat', 'Latin')) )
    biblical_work = models.ForeignKey(BiblicalWork, on_delete=models.PROTECT, verbose_name='Biblical work')
    chapter = models.IntegerField('Chapter')
    verse = models.IntegerField('Verse')
    #this next two fields are not edited or even stored in the editing form they are generated when the form is serialised
    biblical_reference = models.TextField('Ref')
    biblical_reference_sortable = models.IntegerField('Sortable Ref')
    work = models.ForeignKey("Work", on_delete=models.PROTECT, verbose_name='Work')
    work_reference = models.TextField('Work ref', blank=True)
    edition = models.ForeignKey("Edition", on_delete=models.PROTECT, null=True, verbose_name='Edition')
    page_reference = models.TextField('Page', blank=True)
    line_reference = models.TextField('Line', blank=True)
    onlinecorpus = models.ForeignKey("OnlineCorpus", on_delete=models.PROTECT, null=True, verbose_name='OnlineCorpus')
    citation_type = models.TextField('Citation type') #'ALL', u'CAPITULUM', u'LEMMA', u'CIT', u'ADAPT', u'REM'
    citation_reference_type = models.TextField('Reference type', blank=True)#reference, possible reference, no reference, reference not found
    citation_text = models.TextField('Citation text', blank=True)
    search_string = models.TextField('Search string', blank=True)
    #this is a legacy protection field which should never be created in new data
    #for existing Latin it may slowly be replaced with manuscript_variants
    #existing greek transcriptions were multi-transcribed for each MSS witness so this will remain for them
    manuscript_info = models.TextField('MS info', blank=True)
    manuscript_variants = JSONField('MS variants', null=True)

    #ordered
    biblical_catena = ArrayField(models.TextField(), null=True, verbose_name='Biblical catena')

    #this is a legacy protection field which should never be created in new data
    #and may gradually become replaced with dependencies for old data too
    dependencies_string = models.TextField('Dependencies string', blank=True)

    #unordered
    biblical_parallels = ArrayField(models.TextField(), null=True, verbose_name='Biblical catena') #BKV for new ones on drop downs

    work_reference_sortable = models.BigIntegerField('work_reference_sortable', null=True) #puts things in right order for printed output

    comments = models.TextField('Comments', blank=True)
    private_comments = models.TextField('Private comments', blank=True)
    status = models.TextField('status')
    sources = ArrayField(models.TextField(), null=True, verbose_name='Sources')
    project = models.ForeignKey(Project, models.PROTECT)
    copied_to_private_time = models.DateTimeField('Copied to private time', null=True, blank=True)
    id_of_public_version = models.IntegerField('ID of public version', null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ['biblical_work__sort_value', 'chapter', 'verse', 'work__author__identifier', 'work__identifier', 'id']

    def getSerializationFields():
        fields = '__all__'
        return fields

    def get_row_dict(self):
        data = []
        for field in PrivateCitation._meta.fields:
            if field.is_relation:
                value = getattr(self, field.name)
            else:
                value = field.value_from_object(self)
            data.append({'label': field.verbose_name,
                         'value': value,
                         'id': field.name,
                         'field_type': field.get_internal_type()})
        return data

    def get_fields():
        data = {}
        fields = list(PrivateCitation._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

    def __str__(self):
        return '%s %s:%s %s' % (self.biblical_work.name, self.chapter, self.verse, self.citation_text)


class PrivateDependency (models.Model):

    AVAILABILITY =  'private'

    SERIALIZER = 'PrivateDependencySerializer'

    relation_type = models.TextField('Relation type', blank=True)
    author = models.ForeignKey("Author", on_delete=models.PROTECT,  verbose_name='Author', null=True)
    work = models.ForeignKey("Work", on_delete=models.PROTECT, verbose_name='Work', null=True, blank=True)
    work_reference = models.TextField('Work ref', blank=True)
    #we can cascade this one because if we delete the citation that it is part of we no longer need the dependency
    citation = models.ForeignKey(PrivateCitation, on_delete=models.CASCADE, related_name="dependencies", null=True)
    history = HistoricalRecords()

    def __str__(self):
        return '%s %s in %s, %s' % (self.relation_type, self.author, self.work, self.work_reference)




#     def getSerializationFields():
#         fields = ['work', 'author', 'relation_type', 'work_reference']
#         return fields

# class Comcitation (models.Model):
#     LIST_FIELDS = [
#                    'book', 'chapter', 'verse',  'work', 'status', 'transcriber', 'biblical_reference',
#                    ]
#
#     identifier = models.CharField('Identifier', max_length = 50, unique=True)
#     language = models.CharField('Language', max_length = 20, choices = (('grc', 'Greek'), ('lat', 'Latin')) )
#     transcriber = models.CharField('Transcriber', max_length = 10)
#     transcription_date =
#
#         'transcription_date': {'field': 'DateTime',
#                                'required': False},
#         'book': {'field': 'Integer'},
#         'chapter': {'field': 'Integer'},
#         'verse': {'field': 'Integer'},
#         'biblical_reference' : {'field': 'Char'},
#         'author_id': {'field': 'Char'},
#         'work_id': {'field': 'Char'},
#         'work_reference': {'field': 'Char',
#                          'required': False},
#         'edition_id': {'field': 'Char',
#                        'required': False},
#         'page_reference': {'field': 'Char',
#                          'required': False},
#         'ms_siglum': {'field': 'Char',
#                          'required': False},
#         'lemma': {'field': 'Dict',
#                   'required' : False},
#         'exegesis_quotation_type': {'field': 'Dict',
#                            'required' : False},
#         'exegesis_quotation_text': {'field': 'Dict',
#                            'required' : False},
#         'exegesis_text' : {'field': 'Char',
#                              'required' : False},
#         'lemma_exegesis_diffs': {'field': 'List',
#                             'required' : False},
#         'other_references': {'field': 'List',
#                           'required' : False},
#         'cross_refs' : {'field': 'Char',
#                         'required' : False},
#         'textual_comments': {'field': 'Text',
#                      'required': False},
#         'comments': {'field': 'Text',
#                      'required': False},
#         'status': {'field': 'Char',
#                    'required': False},
#         },
#

#
# class Biblindexcitation (models.Model):
#     {'_id': 'cit_biblindex_citation',
#      'modeldescription': 'a model for adding text to biblindex citations',
#      '_model': '_model',
#      '_applications': ['citations'],
#      '_permissions': {'read': False, 'create': False, 'update': False, 'delete': False,
#                          'required' : False},
#      '_view': {'sort': '_id',
#               'list' : {'read' : [{'type': 'link',
#                                         'href': '/citations/biblindex_citation/',
#                                         'text': 'view',
#                                         'params': {'biblindex_citation': 'VAR-_id'}}, {'id':'_id', 'label': 'ID'}, {'id': 'AUCT', 'label': 'Author'}, {'id': 'ChapterValidity_ChapterNum', 'label': 'Chapter'},  {'id': 'VerseValidity_VerseNumber_start', 'label': 'Start verse'}, {'id': 'VerseValidity_VerseNumber_end', 'label': 'End verse'}, 'citation_text'],
#                             'update' : [{'type': 'link',
#                                         'href': '/citations/biblindex_citation/',
#                                         'text': 'view',
#                                         'params': {'biblindex_citation': 'VAR-_id'}}, {'id': '_id', 'label': 'ID'},
#                                         {'id': 'AUCT', 'label': 'Author'}, {'id': 'ChapterValidity_ChapterNum', 'label': 'Chapter'},  {'id': 'VerseValidity_VerseNumber_start', 'label': 'Start verse'}, {'id': 'VerseValidity_VerseNumber_end', 'label': 'End verse'}, 'citation_text',
#                                         'correction_required', 'correction_notes',
#                                         'transcriber', {'id': 'transcription_date', 'label': 'entry date'},
#                                         {'type': 'link',
#                                          'href': '/citations/biblindex_citation/edit/',
#                                          'text': 'edit',
#                                          'back': True,
#                                          'params': {'biblindex_citation': 'VAR-_id'}},
#                                         ]},
#                   'required': False},
#      'AUCT': {'field': 'Char',
#               'required': False},
#      'CLAV': {'field': 'Char',
#               'required': False},
#      'OPUS': {'field': 'Char',
#               'required': False},
#      'TX_CADP_OVR': {'field': 'Char',
#                      'required': False},
#      'TX_VERIFICATION_CIT': {'field': 'Char',
#                              'required': False},
#      'TX_INSTANCE_VALIDATION_CIT': {'field': 'Char',
#                                     'required': False},
#      'TX_LIB_PAT': {'field': 'Char',
#                   'required': False},
#      'TX_CHA_PAT': {'field': 'Char',
#                   'required': False},
#      'TX_PAR_PAT': {'field': 'Char',
#                   'required': False},
#      'TX_PAG_PAT': {'field': 'Char',
#                   'required': False},
#      'TX_SUBPAG_PAT': {'field': 'Char',
#                   'required': False},
#      'TX_LIG_PAT': {'field': 'Char',
#                   'required': False},
#      'TX_ABREV_BPR': {'field': 'Char',
#                   'required': False},
#      'BibleValidity_Abbreviation': {'field': 'Char'},
#      'BookLabel_Abbreviation': {'field': 'Char'},
#      'ChapterValidity_ChapterNum': {'field': 'Integer'},
#      'VerseValidity_VerseNumber_start': {'field': 'Integer'},
#      'VerseValidity_VerseNumber_end': {'field': 'Integer'},
#      'citation_text': {'field': 'Text',
#                   'required': False},
#      'corrections_required': {'field': 'Boolean',
#                   'required': False},
#      'correction_notes': {'field': 'Text',
#                   'required': False},
#      'comments': {'field': 'Text',
#                   'required': False},
#      'language': {'field': 'Char'},
#      'book_number': {'field': 'Integer'},
#      'transcriber': {'field': 'Char', 'required': False},
#      'transcription_date': {'field': 'DateTime', 'required': False},
#
#      },
