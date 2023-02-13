# Generated by Django 3.2.16 on 2023-02-08 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('refdata', '0003_auto_20230119_1253'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fieldofscience',
            options={'get_latest_by': 'modified', 'ordering': ['created'], 'verbose_name': 'field of science', 'verbose_name_plural': 'fields of science'},
        ),
        migrations.AlterModelOptions(
            name='restrictiongrounds',
            options={'get_latest_by': 'modified', 'ordering': ['created'], 'verbose_name': 'restriction grounds', 'verbose_name_plural': 'restriction grounds'},
        ),
        migrations.AddIndex(
            model_name='fieldofscience',
            index=models.Index(fields=['is_reference_data'], name='refdata_fie_is_refe_efdd9f_idx'),
        ),
        migrations.AddIndex(
            model_name='fieldofscience',
            index=models.Index(fields=['url'], name='refdata_fie_url_a5c66a_idx'),
        ),
        migrations.AddIndex(
            model_name='restrictiongrounds',
            index=models.Index(fields=['is_reference_data'], name='refdata_res_is_refe_35cdb5_idx'),
        ),
        migrations.AddIndex(
            model_name='restrictiongrounds',
            index=models.Index(fields=['url'], name='refdata_res_url_2b1384_idx'),
        ),
    ]
