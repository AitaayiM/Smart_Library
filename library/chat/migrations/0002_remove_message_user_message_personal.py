# Generated by Django 5.0.3 on 2024-05-29 19:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
        ('personality', '0008_alter_comment_post_alter_like_comment_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='user',
        ),
        migrations.AddField(
            model_name='message',
            name='personal',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='personality.personal'),
        ),
    ]
