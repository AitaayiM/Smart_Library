# Generated by Django 5.0.3 on 2024-05-18 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ebook', '0002_alter_ebook_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebook',
            name='review_count',
            field=models.IntegerField(default=0),
        ),
    ]
