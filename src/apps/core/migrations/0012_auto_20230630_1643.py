# Generated by Django 3.2.19 on 2023-06-30 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20230630_1035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='temporal',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='temporal',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
