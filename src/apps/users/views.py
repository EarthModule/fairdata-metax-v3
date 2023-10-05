import logging

from django.contrib.auth import get_user_model, logout
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework import exceptions, mixins, status, viewsets
from rest_framework.renderers import AdminRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.responses import HttpResponseSeeOther
from apps.common.views import CommonReadOnlyModelViewSet
from apps.users.authentication import SSOAuthentication
from apps.users.serializers import (
    AuthenticatedUserInfoSerializer,
    TokenSerializer,
    UserInfoSerializer,
)

logger = logging.getLogger(__name__)


class LoginView(APIView):
    @method_decorator(never_cache)
    def get(self, request):
        authentication = SSOAuthentication()
        if not authentication.is_sso_enabled():
            raise exceptions.MethodNotAllowed(method=request.method)

        url = authentication.sso_login_url(request)
        return redirect(url)


class LogoutView(APIView):
    @method_decorator(never_cache)
    def post(self, request):
        logout(request)  # Clear DRF login session if it exists

        # Redirect to SSO logout if using SSO login
        authenticator = request.successful_authenticator
        if isinstance(request.successful_authenticator, SSOAuthentication):
            url = authenticator.sso_logout_url(request)
            return redirect(url)

        return redirect("/")


class AuthenticatedUserView(APIView):
    @method_decorator(never_cache)
    def get(self, request):
        """Return user session information."""
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()

        serializer = AuthenticatedUserInfoSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class TokenListRenderer(AdminRenderer):
    template = "users/tokens.html"


class APITokenListView(KnoxLoginView):
    """View for managing API tokens.

    Allows following methods:
    * GET will return list of tokens for logged in user.
    * POST with an empty body will create a new token (inherited from KnoxLoginView).
    * DELETE with `?prefix=x` parameter will delete corresponding token from the user.

    Provides a UI for creating and deleting API tokens.
    JSON style responses are also supported.
    """

    name = _("API Tokens")

    description = _(
        "API tokens are used for bearer token authentication.\n\n"
        "To make an authenticated request, include "
        "`Authorization: Bearer <token>` in the request headers."
    )

    renderer_classes = [JSONRenderer, TokenListRenderer]

    def get_post_response_data(self, request, token, instance):
        data = super().get_post_response_data(request, token, instance)
        data = {
            "created": self.format_expiry_datetime(instance.created),
            **data,
            "prefix": instance.token_key,
        }
        return data

    def get_queryset(self):
        auth_token_set = getattr(self.request.user, "auth_token_set", None)
        if auth_token_set:
            return self.request.user.auth_token_set.all()
        else:
            return AuthToken.objects.none()

    @method_decorator(never_cache)
    def get(self, request):
        return Response(TokenSerializer(instance=self.get_queryset(), many=True).data)

    @method_decorator(never_cache)
    def delete(self, request):
        token_key = request.query_params.get("prefix")
        qs = self.get_queryset()
        if token_key and qs:
            qs.filter(token_key=token_key).delete()

        return HttpResponseSeeOther(reverse("tokens"))


class UserViewSet(CommonReadOnlyModelViewSet):
    """API for listing and deleting users. Not for production use."""

    queryset = get_user_model().objects.all()
    serializer_class = UserInfoSerializer
    lookup_field = "username"

    def destroy(self, request, *args, **kwargs):
        """Delete user and related data. Not for production use."""
        username = kwargs[self.lookup_field]
        logger.info(f"Deleting user {username} on the request of user: {request.user.username}")

        user = self.get_object()
        dataset_count = user.metadataprovider_set.count()
        user.delete(soft=False)  # cascade delete will remove datasets and their linked filesets
        new_dataset_count = user.metadataprovider_set.count()

        logger.info(
            f"Permanently deleted {dataset_count - new_dataset_count} datasets created by user {user}"
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
