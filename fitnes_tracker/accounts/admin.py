from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import FitnessUser, MealPlan, Meal, Progress, Plan, Workout, Exercise

UserModel = get_user_model()


@admin.register(FitnessUser)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'age', 'gender']
    search_fields = ['username', 'first_name', 'last_name', 'age', 'gender', 'user_role', 'user_level', 'user_goal',
                     'user_activity']
    list_filter = ['username', 'first_name', 'last_name', 'age', 'gender', 'user_role', 'user_level', 'user_goal',
                   'user_activity']
    ordering = ['username']


@admin.register(MealPlan)
class MealPlanModeAdmin(admin.ModelAdmin):
    search_fields = ['title', 'description', ]
    list_display = ['title', 'description', ]
    list_filter = ['title']
    filter_horizontal = ['meals'] \

@admin.register(Exercise)
class ExercisesModelAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'description', 'muscle_group']
    list_filter = ['name', 'muscle_group']

    def __str__(self):
        return self.name


@admin.register(Workout)
class WorkoutsModelAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name', 'created_by', ]
    search_fields = ['name', 'created_by', 'exercises']
    filter_horizontal = ['exercises']


@admin.register(Plan)
class PlanModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']
    filter_horizontal = ['workouts']
    list_select_related = ['user']
    readonly_fields = ['end_date']


@admin.register(Progress)
class ProgressAdminModel(admin.ModelAdmin):
    list_display = ['user']
    readonly_fields = ['current_week']
