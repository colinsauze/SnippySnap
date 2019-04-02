from rest_framework import serializers
from api import serializers as api_serializers
from collections import OrderedDict
from . import models

# I don't think any of the commented out stuff is needed anymore but you should
#run the tests to check

# from rest_framework.settings import api_settings
# from rest_framework.utils import html, model_meta, representation
# import copy
# from rest_framework.exceptions import ValidationError
# from rest_framework.fields import (  # NOQA # isort:skip
#     CreateOnlyDefault, CurrentUserDefault, SkipField, empty
# )
# from rest_framework.fields import set_value
# import inspect
#
#
#
# ALL_FIELDS = '__all__'
#
# LIST_SERIALIZER_KWARGS = (
#     'read_only', 'write_only', 'required', 'default', 'initial', 'source',
#     'label', 'help_text', 'style', 'error_messages', 'allow_empty',
#     'instance', 'data', 'partial', 'context', 'allow_null'
# )




class DependencySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['work', 'author', 'relation_type', 'work_reference']
        model = models.Dependency



class CitationSerializer(serializers.ModelSerializer):

    dependencies = DependencySerializer(many=True, required=False, allow_null=True)
    onlinecorpus = serializers.SlugRelatedField(
        slug_field='abbreviation',
        queryset = models.OnlineCorpus.objects.all(),
        allow_null=True
    )

    class Meta:
        model = models.Citation
        fields = ()

    def create(self, validated_data):
        dependencies_data = validated_data.pop('dependencies')
        citation = models.Citation.objects.create(**validated_data)
        if dependencies_data != None:
            dependencies = [models.Dependency(citation=citation, **item) for item in dependencies_data]
            models.Dependency.objects.bulk_create(dependencies)
        return citation

    def update(self, instance, validated_data):
        #here we need to explicitly save everything in the Citations
        instance.created_time = validated_data.get('created_time', instance.created_time)
        instance.created_by = validated_data.get('created_by', instance.created_by)
        instance.last_modified_time = validated_data.get('last_modified_time', instance.last_modified_time)
        instance.last_modified_by = validated_data.get('last_modified_by', instance.last_modified_by)
        instance.language = validated_data.get('language', instance.language)
        instance.biblical_work = validated_data.get('biblical_work', instance.biblical_work)
        instance.chapter = validated_data.get('chapter', instance.chapter)
        instance.verse = validated_data.get('verse', instance.verse)
        instance.biblical_reference = validated_data.get('biblical_reference', instance.biblical_reference)
        instance.biblical_reference_sortable = validated_data.get('biblical_reference_sortable', instance.biblical_reference_sortable)
        instance.work = validated_data.get('work', instance.work)
        instance.work_reference = validated_data.get('work_reference', instance.work_reference)
        instance.edition = validated_data.get('edition', instance.edition)
        instance.page_reference = validated_data.get('page_reference', instance.page_reference)
        instance.line_reference = validated_data.get('line_reference', instance.line_reference)
        instance.onlinecorpus = validated_data.get('onlinecorpus', instance.onlinecorpus)
        instance.citation_type = validated_data.get('citation_type', instance.citation_type)
        instance.citation_reference_type = validated_data.get('citation_reference_type', instance.citation_reference_type)
        instance.citation_text = validated_data.get('citation_text', instance.citation_text)
        instance.search_string = validated_data.get('search_string', instance.search_string)
        instance.manuscript_info = validated_data.get('manuscript_info', instance.manuscript_info)
        instance.manuscript_variants = validated_data.get('manuscript_variants', instance.manuscript_variants)
        instance.biblical_catena = validated_data.get('biblical_catena', instance.biblical_catena)
        instance.dependencies_string = validated_data.get('dependencies_string', instance.dependencies_string)
        instance.biblical_parallels = validated_data.get('biblical_parallels', instance.biblical_parallels)
        instance.work_reference_sortable = validated_data.get('work_reference_sortable', instance.work_reference_sortable)
        instance.comments = validated_data.get('comments', instance.comments)
        instance.status = validated_data.get('status', instance.status)
        instance.sources = validated_data.get('sources', instance.sources)
        instance.corrections_required = validated_data.get('corrections_required', instance.corrections_required)
        instance.correction_notes = validated_data.get('correction_notes', instance.correction_notes)
        instance.save()
        #and then decide what to do with the dependencies -I suggest that whatever is in the dependency is overwritten
        #with the stuff provided which really means deleting and resaving all dependencies
        if 'dependencies' in validated_data: #checking this will mean in patch they will not be affected unless supplied
            #delete existing data for this citation
            models.Dependency.objects.all().filter(citation__id=instance.id).delete()
            #replace with this new data (which might be nothing)
            #NB this is not ideal as it means a new id is used every time a citation is saved regardless of whether anything has changed or not
            #but I can't find a way of retaining ids and they are only PKs anyway so it doesn't matter what they actually are.
            if len(validated_data['dependencies']) > 0:
                dependencies = [models.Dependency(citation=instance, **item) for item in validated_data['dependencies']]
                models.Dependency.objects.bulk_create(dependencies)
        return instance


    def __init__(self, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if 'fields' in kwargs:
            self.Meta.fields = kwargs['fields']
        else:
            self.Meta.fields = self.Meta.model.getSerializationFields()

        #the next if statement undeclares the dependencies nested serialization if we haven't
        #asked for it to be returned in the list of fields
        #if we don't do this then the ModelSerializer raises an error
        #self._declared_fields is an OrderedDict as we only have one declared field to worry about here
        #just making it an empty list seems to do the job but only doing it if we are specifying fields
        if 'fields' in kwargs and 'dependencies' not in self.Meta.fields:
            self._declared_fields = OrderedDict([])

        if len(args) > 0 and 'data' in kwargs:
            super(CitationSerializer, self).__init__(instance=args[0], data=kwargs['data'], partial=partial)
        elif len(args) > 0:
            super(CitationSerializer, self).__init__(instance=args[0], partial=partial)
        elif 'data' in kwargs:
            super(CitationSerializer, self).__init__(data=kwargs['data'], partial=partial)


class PrivateDependencySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['work', 'author', 'relation_type', 'work_reference']
        model = models.PrivateDependency


class PrivateCitationSerializer(serializers.ModelSerializer):

    dependencies = PrivateDependencySerializer(many=True, required=False, allow_null=True)
    onlinecorpus = serializers.SlugRelatedField(
        slug_field='abbreviation',
        queryset = models.OnlineCorpus.objects.all(),
        allow_null=True
    )

    class Meta:
        model = models.PrivateCitation
        fields = ()

    def create(self, validated_data):
        dependencies_data = validated_data.pop('dependencies')
        privatecitation = models.PrivateCitation.objects.create(**validated_data)
        if dependencies_data != None:
            dependencies = [models.PrivateDependency(citation=privatecitation, **item) for item in dependencies_data]
            models.PrivateDependency.objects.bulk_create(dependencies)
        return privatecitation

    def update(self, instance, validated_data):
        #here we need to explicitly save everything in the PrivateCitations
        instance.created_time = validated_data.get('created_time', instance.created_time)
        instance.created_by = validated_data.get('created_by', instance.created_by)
        instance.last_modified_time = validated_data.get('last_modified_time', instance.last_modified_time)
        instance.last_modified_by = validated_data.get('last_modified_by', instance.last_modified_by)
        instance.language = validated_data.get('language', instance.language)
        instance.biblical_work = validated_data.get('book_number', instance.biblical_work)
        instance.chapter = validated_data.get('chapter', instance.chapter)
        instance.verse = validated_data.get('verse', instance.verse)
        instance.biblical_reference = validated_data.get('biblical_reference', instance.biblical_reference)
        instance.work = validated_data.get('work', instance.work)
        instance.work_reference = validated_data.get('work_reference', instance.work_reference)
        instance.edition = validated_data.get('edition', instance.edition)
        instance.page_reference = validated_data.get('page_reference', instance.page_reference)
        instance.line_reference = validated_data.get('line_reference', instance.line_reference)
        instance.onlinecorpus = validated_data.get('onlinecorpus', instance.onlinecorpus)
        instance.citation_type = validated_data.get('citation_type', instance.citation_type)
        instance.citation_reference_type = validated_data.get('citation_reference_type', instance.citation_reference_type)
        instance.citation_text = validated_data.get('citation_text', instance.citation_text)
        instance.search_string = validated_data.get('search_string', instance.search_string)
        instance.manuscript_info = validated_data.get('manuscript_info', instance.manuscript_info)
        instance.manuscript_variants = validated_data.get('manuscript_variants', instance.manuscript_variants)
        instance.biblical_catena = validated_data.get('biblical_catena', instance.biblical_catena)
        instance.dependencies_string = validated_data.get('dependencies_string', instance.dependencies_string)
        instance.biblical_parallels = validated_data.get('biblical_parallels', instance.biblical_parallels)
        instance.work_reference_sortable = validated_data.get('work_reference_sortable', instance.work_reference_sortable)
        instance.comments = validated_data.get('comments', instance.comments)
        instance.private_comments = validated_data.get('private_comments', instance.private_comments)
        instance.status = validated_data.get('status', instance.status)
        instance.sources = validated_data.get('sources', instance.sources)
        instance.project = validated_data.get('project', instance.project)
        instance.copied_to_private_time = validated_data.get('copied_to_private_time', instance.copied_to_private_time)
        instance.save()
        #and then decide what to do with the dependencies -I suggest that whatever is in the dependency is overwritten
        #with the stuff provided which really means deleting and resaving all dependencies
        if 'dependencies' in validated_data: #checking this will mean in patch they will not be affected unless supplied
            #delete existing data for this citation
            models.PrivateDependency.objects.all().filter(citation__id=instance.id).delete()
            #replace with this new data (which might be nothing)
            #NB this is not ideal as it means a new id is used every time a citation is saved regardless of whether anything has changed or not
            #but I can't find a way of retaining ids and they are only PKs anyway so it doesn't matter what they actually are.
            if len(validated_data['dependencies']) > 0:
                dependencies = [models.Dependency(citation=instance, **item) for item in validated_data['dependencies']]
                models.Dependency.objects.bulk_create(dependencies)
        return instance


    def __init__(self, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if 'fields' in kwargs:
            self.Meta.fields = kwargs['fields']
        else:
            self.Meta.fields = self.Meta.model.getSerializationFields()

        #the next if statement undeclares the dependencies nested serialization if we haven't
        #asked for it to be returned in the list of fields
        #if we don't do this then the ModelSerializer raises an error
        #self._declared_fields is an OrderedDict as we only have one declared field to worry about here
        #just making it an empty list seems to do the job but only doing it if we are specifying fields
        if 'fields' in kwargs and 'dependencies' not in self.Meta.fields:
            self._declared_fields = OrderedDict([])

        if len(args) > 0 and 'data' in kwargs:
            super(PrivateCitationSerializer, self).__init__(instance=args[0], data=kwargs['data'], partial=partial)
        elif len(args) > 0:
            super(PrivateCitationSerializer, self).__init__(instance=args[0], partial=partial)
        elif 'data' in kwargs:
            super(PrivateCitationSerializer, self).__init__(data=kwargs['data'], partial=partial)



class AuthorSerializer(api_serializers.BaseModelSerializer):

    class Meta:
        model = models.Author

class WorkSerializer(api_serializers.BaseModelSerializer):

    class Meta:
        model = models.Work

class SeriesSerializer(api_serializers.BaseModelSerializer):

    class Meta:
        model = models.Series

class OnlineCorpusSerializer(api_serializers.BaseModelSerializer):

    class Meta:
        model = models.OnlineCorpus

class EditionSerializer(api_serializers.BaseModelSerializer):

    series = serializers.SlugRelatedField(
        slug_field='abbreviation',
        queryset = models.Series.objects.all(),
        allow_null=True
    )
    onlinecorpus = serializers.SlugRelatedField(
        slug_field='abbreviation',
        queryset = models.OnlineCorpus.objects.all(),
        allow_null=True
    )

    class Meta:
        model = models.Edition
