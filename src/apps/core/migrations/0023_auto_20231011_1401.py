# Generated by Django 3.2.21 on 2023-10-11 11:01

from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_merge_0020_remoteresource_0021_alter_dataset_previous'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datasetlicense',
            options={'ordering': ['created']},
        ),
        migrations.RenameField(
            model_name='dataset',
            old_name='published_version',
            new_name='published_revision',
        ),
        migrations.RenameField(
            model_name='historicaldataset',
            old_name='published_version',
            new_name='published_revision',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='first',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='last',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='previous',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='replaces',
        ),
        migrations.RemoveField(
            model_name='historicaldataset',
            name='first',
        ),
        migrations.RemoveField(
            model_name='historicaldataset',
            name='last',
        ),
        migrations.RemoveField(
            model_name='historicaldataset',
            name='previous',
        ),
        migrations.RemoveField(
            model_name='historicaldataset',
            name='replaces',
        ),
        migrations.AddField(
            model_name='dataset',
            name='draft_revision',
            field=models.IntegerField(blank=True, default=0, editable=False),
        ),
        migrations.AddField(
            model_name='dataset',
            name='other_versions',
            field=models.ManyToManyField(db_index=True, related_name='_core_dataset_other_versions_+', to='core.Dataset'),
        ),
        migrations.AddField(
            model_name='historicaldataset',
            name='draft_revision',
            field=models.IntegerField(blank=True, default=0, editable=False),
        ),
        migrations.CreateModel(
            name='HistoricalDataset_other_identifiers',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('m2m_history_id', models.AutoField(primary_key=True, serialize=False)),
                ('dataset', models.ForeignKey(blank=True, db_constraint=False, db_tablespace='', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.dataset')),
                ('history', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='core.historicaldataset')),
                ('otheridentifier', models.ForeignKey(blank=True, db_constraint=False, db_tablespace='', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.otheridentifier')),
            ],
            options={
                'verbose_name': 'HistoricalDataset_other_identifiers',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalDataset_infrastructure',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('m2m_history_id', models.AutoField(primary_key=True, serialize=False)),
                ('dataset', models.ForeignKey(blank=True, db_constraint=False, db_tablespace='', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.dataset')),
                ('history', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='core.historicaldataset')),
                ('researchinfra', models.ForeignKey(blank=True, db_constraint=False, db_tablespace='', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.researchinfra')),
            ],
            options={
                'verbose_name': 'HistoricalDataset_infrastructure',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
