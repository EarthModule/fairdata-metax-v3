# Generated by Django 3.2.22 on 2023-10-24 13:08

import apps.core.models.concepts
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('refdata', '0010_auto_20230928_1442'),
        ('core', '0026_auto_20231024_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='RestrictionGrounds',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=(apps.core.models.concepts.ConceptProxyMixin, 'refdata.restrictiongrounds'),
        ),
        migrations.DeleteModel(
            name='AccessRightsRestrictionGrounds',
        ),
        migrations.AddField(
            model_name='accessrights',
            name='restriction_grounds',
            field=models.ManyToManyField(related_name='access_rights', to='core.RestrictionGrounds'),
        ),
    ]
