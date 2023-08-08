from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import FitnessUser, Meal, DailyCalorieIntake, DailyUserReport

UserModel = get_user_model()


@admin.register(FitnessUser)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'age', 'gender']
    search_fields = ['username', 'first_name', 'last_name', 'age', 'gender', 'user_role', 'user_level', 'user_goal',
                     'user_activity']
    list_filter = ['username', 'first_name', 'last_name', 'age', 'gender', 'user_role', 'user_level', 'user_goal',
                   'user_activity']
    ordering = ['username']


@admin.register(Meal)
class MealModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_calories', 'list_of_ingredients', 'total_protein', 'total_carbs', 'total_fats',
                    'user']
    search_fields = ['name', 'user', 'total_calories']


@admin.register(DailyCalorieIntake)
class DailyCaloriesAdmin(admin.ModelAdmin):
    list_display = ['date', 'user', 'breakfast', 'morning_snack', 'lunch', 'afternoon_snack', 'dinner', 'evening_snack',
                    'total_calories', 'total_protein', 'total_carbs', 'total_fats']

    search_fields = ['date', 'user', 'breakfast', 'morning_snack', 'lunch', 'afternoon_snack', 'dinner',
                     'evening_snack',
                     'total_calories', 'total_protein', 'total_carbs', 'total_fats']


@admin.register(DailyUserReport)
class DailyUserReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'daily_intake_calories', 'daily_protein_intake', 'daily_carbs_intake',
                    'daily_fats_intake', 'weight']
