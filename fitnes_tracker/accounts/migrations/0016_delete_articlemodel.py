# Generated by Django 4.2.3 on 2023-08-05 21:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_alter_meal_unique_together'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ArticleModel',
        ),
    ]
