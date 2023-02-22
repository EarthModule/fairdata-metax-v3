from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from django_filters import rest_framework as filters

from apps.actors.models import Organization
from apps.actors.serializers import OrganizationSerializer


class OrganizationFilterSet(filters.FilterSet):
    pref_label = filters.CharFilter(
        field_name="pref_label__values",
        max_length=255,
        lookup_expr="icontains",
        label="pref_label",
    )


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    filterset_class = OrganizationFilterSet
    serializer_class = OrganizationSerializer

    queryset = Organization.available_objects.filter(
        is_reference_data=True,
    ).prefetch_related("parent", "children", "children__children")

    def get_queryset(self):
        qs = super().get_queryset()

        # hide suborganizations from list view
        if not self.kwargs.get("pk"):
            qs = qs.filter(parent__isnull=True)
        return qs
