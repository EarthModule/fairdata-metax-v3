# Generated by Django 3.2.16 on 2023-01-26 08:04

import apps.core.helpers
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import simple_history.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FileStorage',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('removal_date', models.DateTimeField(blank=True, null=True)),
                ('id', models.CharField(help_text='A unique id of the data storage', max_length=255, primary_key=True, serialize=False)),
                ('endpoint_url', models.URLField(help_text='The root location or primary endpoint of the service (a Web-resolvable IRI).')),
                ('endpoint_description', models.TextField(help_text='A description of the services available via the end-points, including their operations, parameters etc.')),
                ('system_creator', models.ForeignKey(default=apps.core.helpers.get_technical_metax_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files_filestorages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created'],
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StorageProject',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('removal_date', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('project_identifier', models.CharField(max_length=200)),
                ('file_storage', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='files.filestorage')),
                ('system_creator', models.ForeignKey(default=apps.core.helpers.get_technical_metax_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files_storageprojects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('project_identifier', 'file_storage')},
            },
        ),
        migrations.CreateModel(
            name='HistoricalFileStorage',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('removal_date', models.DateTimeField(blank=True, null=True)),
                ('id', models.CharField(db_index=True, help_text='A unique id of the data storage', max_length=255)),
                ('endpoint_url', models.URLField(help_text='The root location or primary endpoint of the service (a Web-resolvable IRI).')),
                ('endpoint_description', models.TextField(help_text='A description of the services available via the end-points, including their operations, parameters etc.')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('system_creator', models.ForeignKey(blank=True, db_constraint=False, default=apps.core.helpers.get_technical_metax_user, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical file storage',
                'verbose_name_plural': 'historical file storages',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('removal_date', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file_name', models.TextField()),
                ('directory_path', models.TextField(db_index=True)),
                ('byte_size', models.BigIntegerField(default=0)),
                ('checksum_algorithm', models.CharField(choices=[('SHA-256', 'SHA-256'), ('MD5', 'MD5'), ('SHA-512', 'SHA-512')], max_length=200)),
                ('checksum_checked', models.DateTimeField()),
                ('checksum_value', models.TextField()),
                ('file_frozen', models.DateTimeField(blank=True, null=True)),
                ('file_deleted', models.DateTimeField(null=True)),
                ('file_modified', models.DateTimeField()),
                ('file_uploaded', models.DateTimeField()),
                ('pas_compatible', models.BooleanField(default=True)),
                ('storage_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='files.storageproject')),
                ('system_creator', models.ForeignKey(default=apps.core.helpers.get_technical_metax_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files_files', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['directory_path', 'file_name'],
            },
        ),
        migrations.AddConstraint(
            model_name='file',
            constraint=models.CheckConstraint(check=models.Q(('file_name', ''), _negated=True), name='files_file_require_file_name'),
        ),
        migrations.AddConstraint(
            model_name='file',
            constraint=models.CheckConstraint(check=models.Q(('directory_path__startswith', '/'), ('directory_path__endswith', '/')), name='files_file_require_dir_slash'),
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together={('file_name', 'directory_path', 'storage_project')},
        ),
        migrations.AlterIndexTogether(
            name='file',
            index_together={('directory_path', 'storage_project'), ('directory_path', 'file_name')},
        ),
    ]
