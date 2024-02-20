import logging

import requests
from django.conf import settings
from django.utils import timezone

from apps.users.models import MetaxUser

_logger = logging.getLogger(__name__)


class SSOClient:
    """Client for synchronizing user data using Fairdata SSO."""

    def __init__(self):
        self.enabled = settings.ENABLE_SSO_AUTH
        self.host = settings.SSO_HOST
        self.trusted_service_token = settings.SSO_TRUSTED_SERVICE_TOKEN
        if self.enabled and not (self.trusted_service_token and self.host):
            self.enabled = False
            _logger.warning(
                "User sync disabled due to missing SSO_TRUSTED_SERVICE_TOKEN or SSO_HOST."
            )

    def sync_user(self, user: MetaxUser) -> bool:
        """Sync user from SSO if necessary."""
        if not self.enabled:
            return False

        if not getattr(user, "fairdata_username", None):
            return False  # Non-fairdata user, no need to sync

        # No need to sync active user if synced recently
        now = timezone.now()
        if user.is_active and user.synced and (now - user.synced < timezone.timedelta(hours=8)):
            return False

        payload = {
            "id": user.username,
            "token": self.trusted_service_token,
        }
        url = f"{self.host}/user_status"
        res = requests.post(url, payload)
        if res.status_code != 200:
            _logger.warning("User sync error. Failed to get user data from {url}: {res.text} ")
            return False

        # Update user
        data = res.json()
        user.synced = now
        user.is_active = not data["locked"]
        user.csc_projects = data["projects"]
        user.save()
        return True
