# This file is part of the Metax API service
#
# Copyright 2017-2022 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: MIT
import logging

from rest_framework import serializers

from apps.core.models import Dataset
from apps.core.models.concepts import FieldOfScience, Language, Theme
from apps.core.serializers.common_serializers import AccessRightsModelSerializer

logger = logging.getLogger(__name__)


class DatasetSerializer(serializers.ModelSerializer):
    access_rights = AccessRightsModelSerializer(required=False)
    language = Language.get_serializer()(required=False, many=True)
    theme = Theme.get_serializer()(required=False, many=True)
    field_of_science = FieldOfScience.get_serializer()(required=False, many=True)

    class Meta:
        model = Dataset
        fields = (
            "persistent_identifier",
            "issued",
            "title",
            "description",
            "theme",
            "language",
            "data_catalog",
            "access_rights",
            "field_of_science",
            # read only
            "id",
            "first",
            "last",
            "previous",
            "replaces",
            "is_deprecated",
            "is_removed",
            "removal_date",
            "cumulation_started",
            "created",
            "modified",
        )
        read_only_fields = (
            "id",
            "first",
            "last",
            "previous",
            "replaces",
            "is_deprecated",
            "is_removed",
            "removal_date",
            "cumulation_started",
            "created",
            "modified",
        )

    def create(self, validated_data):
        languages = validated_data.pop("language", [])
        themes = validated_data.pop("theme", [])
        fields_of_science = validated_data.pop("field_of_science", [])

        access_rights_serializer: AccessRightsModelSerializer = self.fields["access_rights"]
        access_rights = None
        if access_rights_data := validated_data.pop("access_rights", None):
            access_rights = access_rights_serializer.create(access_rights_data)

        dataset = Dataset.objects.create(**validated_data, access_rights=access_rights)

        dataset.language.set(languages)
        dataset.theme.set(themes)
        dataset.field_of_science.set(fields_of_science)
        return dataset

    def update(self, instance, validated_data):
        languages = validated_data.pop("language", [])
        themes = validated_data.pop("theme", [])
        fields_of_science = validated_data.pop("field_of_science", [])

        access_rights_serializer: AccessRightsModelSerializer = self.fields["access_rights"]
        access_rights = None
        if access_rights_data := validated_data.pop("access_rights", None):
            access_rights = access_rights_serializer.create(access_rights_data)
        instance.access_rights = access_rights

        super().update(instance, validated_data)

        instance.language.set(languages)
        instance.theme.set(themes)
        instance.field_of_science.set(fields_of_science)
        return instance
