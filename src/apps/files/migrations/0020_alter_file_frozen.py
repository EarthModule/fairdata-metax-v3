# Generated by Django 3.2.22 on 2023-11-21 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0019_merge_0017_auto_20230928_1442_0018_auto_20231019_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='frozen',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]
