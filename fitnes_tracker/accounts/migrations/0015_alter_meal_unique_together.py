# Generated by Django 4.2.3 on 2023-08-05 20:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_alter_meal_list_of_ingredients_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='meal',
            unique_together={('name', 'user')},
        ),
    ]
