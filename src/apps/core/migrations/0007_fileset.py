# Generated by Django 3.2.18 on 2023-04-26 12:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0006_auto_20230526_1606'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileSet',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('removal_date', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('dataset', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='file_set', to='core.dataset')),
                ('file_storage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file_sets', to='files.filestorage')),
                ('files', models.ManyToManyField(related_name='file_sets', to='files.File')),
                ('system_creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='core_filesets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created'],
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FileSetFileMetadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dataset_metadata', to='files.file')),
                ('file_set', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='file_metadata', to='core.fileset')),
                ('file_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.filetype')),
                ('use_category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.usecategory')),
            ],
            options={
                'unique_together': {('file_set', 'file')},
            },
        ),
        migrations.CreateModel(
            name='FileSetDirectoryMetadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('directory_path', models.TextField(db_index=True)),
                ('title', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('file_set', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='directory_metadata', to='core.fileset')),
                ('file_storage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='files.filestorage')),
                ('use_category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.usecategory')),
            ],
            options={
                'unique_together': {('file_set', 'directory_path')},
            },
        ),
    ]
