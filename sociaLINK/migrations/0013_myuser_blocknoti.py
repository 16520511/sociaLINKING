# Generated by Django 2.1 on 2018-09-17 12:44

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sociaLINK', '0012_remove_notification_isimpressed'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='blockNoti',
            field=models.ManyToManyField(related_name='blockNotis', to=settings.AUTH_USER_MODEL),
        ),
    ]
