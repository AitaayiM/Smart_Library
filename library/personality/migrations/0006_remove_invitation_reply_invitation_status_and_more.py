# Generated by Django 5.0.3 on 2024-05-23 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personality', '0005_reaction_like'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invitation',
            name='reply',
        ),
        migrations.AddField(
            model_name='invitation',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Pending', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='personal',
            name='bio',
            field=models.TextField(blank=True, default='', max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='personal',
            name='isbn',
            field=models.CharField(default='', max_length=40, null=True, unique=True),
        ),
    ]
