# Generated by Django 2.1 on 2018-09-18 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sociaLINK', '0016_auto_20180918_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='mygroup',
            name='uniqueId',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]