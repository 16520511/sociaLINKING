# Generated by Django 2.1 on 2018-09-18 04:43

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sociaLINK', '0014_auto_20180918_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mygroup',
            name='banned',
            field=models.ManyToManyField(related_name='banned', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='mygroup',
            name='member',
            field=models.ManyToManyField(related_name='members', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='mygroup',
            name='mod',
            field=models.ManyToManyField(related_name='mods', to=settings.AUTH_USER_MODEL),
        ),
    ]
