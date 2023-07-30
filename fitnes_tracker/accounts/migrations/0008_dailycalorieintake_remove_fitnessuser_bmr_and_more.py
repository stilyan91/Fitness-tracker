# Generated by Django 4.2.3 on 2023-07-25 19:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_fitnessuser_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyCalorieIntake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('total_calories', models.IntegerField(default=0)),
                ('afternoon_snack', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='afternoon_snack_meals', to='accounts.meal')),
                ('breakfast', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='breakfast_meals', to='accounts.meal')),
                ('dinner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dinner_meals', to='accounts.meal')),
                ('evening_snack', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='evening_snack_meals', to='accounts.meal')),
                ('lunch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lunch_meals', to='accounts.meal')),
                ('morning_snack', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='morning_snack_meals', to='accounts.meal')),
            ],
        ),
        migrations.RemoveField(
            model_name='fitnessuser',
            name='bmr',
        ),
        migrations.AddField(
            model_name='fitnessuser',
            name='maintenance_calories',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='fitnessuser',
            name='target_calories',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='fitnessuser',
            name='weight_change_intensity',
            field=models.CharField(choices=[('LIGHT', '0.2 kg per week'), ('MODERATE', '0.5 kg per week'), ('HIGH', '1 kg per week')], default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='DailyUserReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('daily_intake_calories', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.dailycalorieintake')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='dailycalorieintake',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
