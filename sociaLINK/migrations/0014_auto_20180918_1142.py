# Generated by Django 2.1 on 2018-09-18 04:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sociaLINK', '0013_myuser_blocknoti'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=300)),
                ('banned', models.ManyToManyField(blank=True, null=True, related_name='banned', to=settings.AUTH_USER_MODEL)),
                ('founder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('member', models.ManyToManyField(blank=True, null=True, related_name='members', to=settings.AUTH_USER_MODEL)),
                ('mod', models.ManyToManyField(blank=True, null=True, related_name='mods', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sociaLINK.MyGroup'),
        ),
    ]
