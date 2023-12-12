import logging
from typing import Optional

from apps.actors.models import Organization, Person
from apps.actors.serializers import ActorModelSerializer
from apps.common.serializers.serializers import CommonListSerializer, CommonNestedModelSerializer
from apps.core.models import Dataset, DatasetActor, EventOutcome, LifecycleEvent, Provenance
from apps.core.serializers import (
    DatasetActorProvenanceSerializer,
    SpatialModelSerializer,
    TemporalModelSerializer,
)
from apps.core.serializers.common_serializers import EntitySerializer

logger = logging.getLogger(__name__)


class ProvenanceModelSerializer(CommonNestedModelSerializer):
    spatial = SpatialModelSerializer(required=False, allow_null=True)
    temporal = TemporalModelSerializer(required=False, allow_null=True)
    lifecycle_event = LifecycleEvent.get_serializer_field(required=False, allow_null=True)
    event_outcome = EventOutcome.get_serializer_field(required=False, allow_null=True)
    is_associated_with = DatasetActorProvenanceSerializer(many=True, required=False)
    used_entity = EntitySerializer(many=True, required=False)

    class Meta:
        model = Provenance
        fields = (
            "id",
            "title",
            "description",
            "spatial",
            "temporal",
            "lifecycle_event",
            "event_outcome",
            "outcome_description",
            "is_associated_with",
            "used_entity",
        )
        read_only_fields = ("id",)
        list_serializer_class = CommonListSerializer
