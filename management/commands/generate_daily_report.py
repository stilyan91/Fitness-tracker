from django.core.management.base import BaseCommand
from django.utils import timezone

from fitnes_tracker.accounts.models import FitnessUser, DailyUserReport, DailyCalorieIntake


class Command(BaseCommand):
    help = "Generate daily report for all users"

    def handle(self, *args, **options):
        today = timezone.now().date()

        for user in FitnessUser.objects.all():
            user_intake_calories = DailyCalorieIntake.objects.get(user=user, date=today)
            if not DailyUserReport.objects.filter(user=user, date=today).exist():
                DailyUserReport.objects.create(
                    user=user_intake_calories,
                    date=user_intake_calories,
                    daily_intake_calories=user_intake_calories.total_calories,
                    daily_protein_intake=user_intake_calories.total_protein,
                    daily_carbs_intake=user_intake_calories.total_carbs,
                    daily_fats_intake=user_intake_calories.total_fats,
                    weight=user_intake_calories.weight
                )

            self.stdout.write(self.style.SUCCESS('Succesfully generated daily report!'))
