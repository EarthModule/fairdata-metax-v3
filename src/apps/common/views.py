from rest_access_policy import AccessViewSetMixin
from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.common.permissions import BaseAccessPolicy


class SystemCreatorViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    access_policy = BaseAccessPolicy

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            raise NotAuthenticated("You must be authenticated to perform this action.")
        serializer.save(system_creator=self.request.user)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class PatchModelMixin:
    """ViewSet mixin for patch support in partial update.

    The ViewSet needs to use a serializer based on PatchModelSerializer.
    Otherwise the serializer raises an error about unexpected 'patch' argument.
    """

    def update(self, request, *args, **kwargs):
        """Like UpdateModelMixin.update but with support for 'patch' kwarg."""
        patch = kwargs.pop("patch", False)
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, patch=patch)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs["patch"] = True
        return self.update(request, *args, **kwargs)


class QueryParamsMixin(viewsets.ViewSet):
    """ViewSet mixin for parsing query params with serializers.

    Provides `query_params` attribute that validates query parameters
    using serializers assigned to the view action.

    The serializers are configured with the
    added query_serializers ViewSet class attribute.
    The query_serializers attribute should be a list of dicts with
    - `class`: Serializer class used for parsing query parameters.
    - `actions`: Optional list to limit the ViewSet actions the serializer applies to.

    Example:
    ```
    class SomeView(ViewSet):
        query_serializers = [
            {"class": SomeQueryParamsSerializer, "actions": ["list"]}
        ]

        def list(self, request, *args, **kwargs):
            params = self.query_params
            ...
    ```

    The query serializers are also used for generating swagger docs.
    See the inspectors.ExtendedSwaggerAutoSchema.get_query_parameters method for details.
    """

    query_serializers = []

    query_params = {}

    def initial(self, request, *args, **kwargs):
        """Initialization before method handler is called."""
        super().initial(request, *args, **kwargs)
        self.validate_query_params()

    def get_query_serializer_classes(self):
        """Get query serializer classes for current action."""
        classes = []
        for serializer_info in getattr(self, "query_serializers", []):
            actions = serializer_info.get("actions")
            if actions and self.action not in actions:
                continue
            classes.append(serializer_info["class"])
        return classes

    def validate_query_params(self):
        """Validate query parameters for current action, assign to self.query_params."""
        params = {}
        for serializer_class in self.get_query_serializer_classes():
            serializer = serializer_class(data=self.request.query_params)
            serializer.is_valid(raise_exception=True)
            params.update(serializer.validated_data)
        self.query_params = params


class NonFilteringGetObjectMixin:
    """ViewSet mixin that doesn't call filter_queryset in get_object.

    Normally, e.g. `/datasets/<id>?title=something` will
    return 404 if the title does not contain 'something'.
    This is counterintuitive since it's not anywhere in
    the Swagger docs. Disabling the feature should be
    ok since we're not using django-filters for enforcing
    permissions.
    """

    def get_object(self):
        """Identical to GenericAPIView.get_object but doesn't use filter_queryset."""
        queryset = self.get_queryset()  # removed filter_queryset here

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly." % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class CommonModelViewSet(
    QueryParamsMixin, NonFilteringGetObjectMixin, PatchModelMixin, SystemCreatorViewSet
):
    """ViewSet with common functionality."""


class CommonReadOnlyModelViewSet(
    QueryParamsMixin, NonFilteringGetObjectMixin, viewsets.ReadOnlyModelViewSet
):
    """ViewSet with common functionality for read only models."""
