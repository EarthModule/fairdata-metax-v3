import logging
import uuid
from typing import Dict

from django.conf import settings
from django.contrib.postgres.fields import HStoreField
from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.db.models import Model
from django.utils.translation import gettext as _

from apps.common.copier import ModelCopier
from apps.common.models import AbstractBaseModel

logger = logging.getLogger(__name__)


class OrganizationModelCopier(ModelCopier):
    def copy(self, original: Model, new_values: dict = None, copied_objects: dict = None) -> Model:
        if original.is_reference_data:
            return (
                original  # Reference data organizations should be used as-is instead of copying.
            )
        return super().copy(original, new_values, copied_objects)


class Organization(AbstractBaseModel):
    """
    Base model for Reference Data objects

    Source: skos:Concept
    https://www.w3.org/TR/skos-reference/#concepts
    """

    # Copying a sub-organization in a dataset should also copy its parents
    copier = OrganizationModelCopier(
        copied_relations=["parent"], parent_relations=["actor_organizations", "projects", "agencies"]
    )

    def choose_between(self, other) -> "Organization":
        if isinstance(other, self.__class__):
            if self.parent is None and other.parent is not None:
                return self
            elif self.in_scheme and not other.in_scheme:
                return self
            elif self.code and not other.code:
                return self
            elif self.url and not other.url:
                return self
            elif len(list(self.pref_label.keys())) > len(list(other.pref_label.keys())):
                return self
            else:
                return other

    @classmethod
    def get_instance_from_v2_dictionary(cls, org_obj) -> "Organization":
        """Gets or creates organization for the actor from v2 organization type actor object.

        Args:
            org_obj (): dictionary with organization name in one or many languages.
                Example dictionary could be {"fi":"csc": "en":"csc"}

        Returns:
            Organization: Organization object corresponding to given name dictionary.

        """
        # https://docs.djangoproject.com/en/4.1/ref/contrib/postgres/fields/#values
        # pref_label is HStoreField that serializes into dictionary object.
        # pref_label__values works as normal python dictionary.values()
        # pref_label__values__contains compares if any given value in a list is contained in the pref_label values.
        try:
            org, created = cls.objects.get_or_create(
                pref_label__values__contains=list(org_obj["name"].values()),
                url=org_obj.get("identifier"),
                defaults={
                    "pref_label": org_obj["name"],
                    "homepage": org_obj.get("homepage"),
                    "url": org_obj.get("identifier"),
                    "in_scheme": settings.ORGANIZATION_SCHEME,
                },
            )
            logger.debug(f"{org=}, {created=}")
            return org
        except MultipleObjectsReturned as e:
            orgs = cls.objects.filter(
                pref_label__values__contains=list(org_obj["name"].values()),
                url=org_obj.get("identifier"),
            )
            best_org = orgs[0]
            for org in orgs:
                best_org = org.choose_between(best_org)
            logger.error(
                f"{e}, chose: {best_org.pref_label} from: {[org.pref_label for org in orgs]}"
            )
            return best_org

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=64, null=True)
    in_scheme = models.URLField(max_length=255, null=True, blank=True)
    pref_label = HStoreField(help_text='example: {"en":"title", "fi":"otsikko"}')
    homepage = HStoreField(
        blank=True,
        null=True,
        help_text='example: {"title": {"en": "webpage"}, "identifier": "url"}',
    )
    external_identifier = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        help_text=_("External identifier for the organization."),
    )
    email = models.EmailField(max_length=512, blank=True, null=True)

    parent = models.ForeignKey(
        "self",
        related_name="children",
        blank=True,
        on_delete=models.CASCADE,
        null=True,
    )
    is_reference_data = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["is_reference_data"]),
            models.Index(fields=["url"]),
        ]
        get_latest_by = "modified"
        ordering = ["created"]

        constraints = [
            # Reference organizations should have a URL.
            models.CheckConstraint(
                check=~models.Q(url="") | models.Q(is_reference_data=False),
                name="%(app_label)s_%(class)s_require_url",
            ),
            # Reference organization urls should be unique.
            models.UniqueConstraint(
                fields=["url"],
                condition=models.Q(is_reference_data=True),
                name="%(app_label)s_%(class)s_unique_organization_url",
            ),
            # Reference organizations should have a code.
            models.CheckConstraint(
                check=~models.Q(code="") | models.Q(is_reference_data=False),
                name="%(app_label)s_%(class)s_require_code",
            ),
            # Codes should be unique within reference data.
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(is_reference_data=True),
                name="%(app_label)s_%(class)s_unique_organization_code",
            ),
            # Reference organizations should have a scheme.
            models.CheckConstraint(
                check=(models.Q(in_scheme__isnull=False) & ~models.Q(in_scheme=""))
                | models.Q(is_reference_data=False),
                name="%(app_label)s_%(class)s_require_reference_data_scheme",
            ),
        ]

    def get_label(self):
        pref_label = self.pref_label or {}
        return pref_label.get("en") or pref_label.get("fi") or next(iter(pref_label.values()), "")

    def as_v2_data(self):
        """Returns v2 organization dictionary"""
        data = {}
        data["@type"] = "Organization"
        data["name"] = self.pref_label
        if url := self.url:
            data["identifier"] = url
        if homepage := self.homepage:
            if title := homepage.get("title"):
                if isinstance(title, str):
                    homepage["title"] = eval(title)
            data["homepage"] = homepage
        if parent := self.parent:
            data["is_part_of"] = parent.as_v2_data()
        return data

    def __str__(self):
        return f"{self.id}: {self.get_label()}"


class Person(AbstractBaseModel):
    copier = ModelCopier(copied_relations=[], parent_relations=["part_of_actors"])

    name = models.CharField(max_length=512)
    email = models.EmailField(max_length=512, blank=True, null=True)
    external_identifier = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        help_text=_("External identifier for the actor, usually ORCID or similiar"),
    )

    def __str__(self):
        return str(self.name)


class Actor(AbstractBaseModel):
    """Name of organization or person.

    Different types include e.g. creator, curator, publisher or rights holder.

    Attributes:
        person(Person): Person if any associated with this actor.
        organization(Organization): Organization if any associated with this actor.
    """

    person = models.ForeignKey(
        Person, related_name="part_of_actors", null=True, blank=True, on_delete=models.CASCADE
    )
    organization = models.ForeignKey(
        Organization,
        related_name="actor_organizations",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def as_v2_data(self) -> Dict:
        """Returns v2 actor dictionary."""
        data = {}
        if self.person:
            data["name"] = self.person.name
            data["@type"] = "Person"
            if self.organization:
                data["member_of"] = self.organization.as_v2_data()

        elif self.organization:
            data = self.organization.as_v2_data()
        return data

    def __str__(self):
        if self.person:
            return str(self.person)
        else:
            return str(self.organization)
