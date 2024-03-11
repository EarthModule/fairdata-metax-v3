# Generated by Django 3.2.22 on 2024-03-11 14:34

from django.conf import settings
import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import simple_history.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('actors', '0004_auto_20240220_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='deprecated',
            field=models.DateTimeField(blank=True, help_text='If set, organization is not shown in organization list by default.', null=True),
        ),
        migrations.CreateModel(
            name='HomePage',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('removed', models.DateTimeField(blank=True, editable=False, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('url', models.URLField(help_text='Link to homepage.', max_length=512)),
                ('title', django.contrib.postgres.fields.hstore.HStoreField(help_text='example: {"en":"title", "fi":"otsikko"}', null=True)),
                ('system_creator', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='actors_homepages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created', 'id'],
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalHomePage',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('removed', models.DateTimeField(blank=True, editable=False, null=True)),
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('url', models.URLField(help_text='Link to homepage.', max_length=512)),
                ('title', django.contrib.postgres.fields.hstore.HStoreField(help_text='example: {"en":"title", "fi":"otsikko"}', null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('system_creator', models.ForeignKey(blank=True, db_constraint=False, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical home page',
                'verbose_name_plural': 'historical home pages',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.RemoveField(
            model_name='organization',
            name='homepage',
        ),
        migrations.AddField(
            model_name='organization',
            name='homepage',
            field=models.OneToOneField(blank=True, help_text='example: {"title": {"en": "webpage"}, "url": "https://example.com"}', null=True, on_delete=django.db.models.deletion.SET_NULL, to='actors.homepage'),
        ),
    ]
