# Generated by Django 3.2.22 on 2024-02-20 13:51

import django.contrib.postgres.fields.hstore
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20240216_0801'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accessrights',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id'], 'verbose_name_plural': 'Access rights'},
        ),
        migrations.AlterModelOptions(
            name='cataloghomepage',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='catalogrecord',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='contract',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='datacatalog',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='dataset',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='datasetproject',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='datasetpublisher',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='datasetversions',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='entity',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id'], 'verbose_name_plural': 'Entities'},
        ),
        migrations.AlterModelOptions(
            name='entityrelation',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='fileset',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='filesetdirectorymetadata',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='filesetfilemetadata',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='funder',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='funding',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='legacydataset',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='metadataprovider',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='otheridentifier',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='preservation',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='provenance',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='provenancevariable',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='remoteresource',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='spatial',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.AlterModelOptions(
            name='temporal',
            options={'get_latest_by': 'modified', 'ordering': ['created', 'id']},
        ),
        migrations.RemoveField(
            model_name='datacatalog',
            name='access_rights',
        ),
        migrations.RemoveField(
            model_name='historicaldatacatalog',
            name='access_rights',
        ),
        migrations.AddField(
            model_name='datacatalog',
            name='description',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, help_text='example: {"en":"description", "fi":"kuvaus"}', null=True),
        ),
        migrations.AddField(
            model_name='historicaldatacatalog',
            name='description',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, help_text='example: {"en":"description", "fi":"kuvaus"}', null=True),
        ),
    ]
