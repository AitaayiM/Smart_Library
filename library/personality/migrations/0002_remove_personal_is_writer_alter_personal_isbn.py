# Generated by Django 5.0.3 on 2024-05-17 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personality', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personal',
            name='is_writer',
        ),
        migrations.AlterField(
            model_name='personal',
            name='isbn',
            field=models.CharField(default='', max_length=40),
        ),
    ]
