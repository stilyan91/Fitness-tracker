# Generated by Django 4.2.3 on 2023-08-06 07:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_dailycalorieintake_total_carbs_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyuserreport',
            name='daily_carbs_intake',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='daily_intake_carbs_report', to='accounts.dailycalorieintake'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dailyuserreport',
            name='daily_fats_intake',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='daily_intake_fats_report', to='accounts.dailycalorieintake'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dailyuserreport',
            name='daily_protein_intake',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='daily_intake_protein_report', to='accounts.dailycalorieintake'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dailyuserreport',
            name='daily_intake_calories',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_intake_calories_report', to='accounts.dailycalorieintake'),
        ),
    ]
