from datetime import timedelta, datetime
from enum import Enum

from django.core.validators import MinValueValidator, MinLengthValidator
from django.db import models

from django.contrib.auth import models as auth_models, get_user_model
from django.utils import timezone


class ChoicesMixin(Enum):
    @classmethod
    def choice(cls):
        return [(choice.name, choice.value) for choice in cls]

    @classmethod
    def max_length(cls):
        return max(len(choice.value) for choice in cls)


class GENDER(ChoicesMixin, Enum):
    MALE = "Male"
    FEMALE = "Female"


class WeightChangeIntensity(models.TextChoices):
    LIGHT = 'LIGHT', ('0.2 kg per week')
    MODERATE = 'MODERATE', ('0.5 kg per week')
    HIGH = 'HIGH', ('1 kg per week')


class UserRole(ChoicesMixin, Enum):
    TRAINER = "Fitness Trainer"
    FITNESS_ENTHUSIAST = "Fitness Enthusiast"


class UserLevel(ChoicesMixin, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class UserGoals(ChoicesMixin, Enum):
    lose_weight = "Lose weight"
    gain_muscle = "Gain muscle"
    maintain_weight = "Maintain_weight"


class UserActivity(ChoicesMixin, Enum):
    SEDENTARY = "Sedentary (little to no exercise)"
    LIGHT_ACTIVE = "Lightly active (light exercise/sports 1-3 days/week)"
    MODERATELY_ACTIVE = "Moderately active (moderate exercise/sports 3-5 days/week)"
    VERY_ACTIVE = "Very active (hard exercise/sports 6-7 days/week)"
    EXTRA_ACTIVE = "Extra active (very hard exercise/sports and a physical job)"


class FitnessUser(auth_models.AbstractUser):
    ACTIVITY_LEVELS = {
        'SEDENTARY': 1.2,
        'LIGHT_ACTIVE': 1.375,
        'MODERATELY_ACTIVE': 1.55,
        'VERY_ACTIVE': 1.725,
        'EXTRA_ACTIVE': 1.9,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field('username').help_text = ''

    age = models.PositiveIntegerField(default=0, blank=False, null=False, validators=[MinValueValidator(0)])
    profile_picture = models.ImageField(upload_to='profile_pictures/',
                                        null=True,
                                        blank=True,
                                        max_length=500,
                                        validators=[]
                                        )
    height = models.IntegerField(
        verbose_name='Height in sm',
        default=0,
        blank=False,
        null=False,
        validators=[MinValueValidator(50)]
    )
    weight = models.FloatField(
        verbose_name='Weight in kgs',
        default=0.00,
        blank=False,
        null=False,
        validators=[MinValueValidator(20)]
    )

    gender = models.CharField(
        choices=GENDER.choice(),
        max_length=GENDER.max_length(),
        blank=False,
        null=False,
    )
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
    )
    user_role = models.CharField(
        choices=UserRole.choice(),
        max_length=UserRole.max_length(),
    )
    user_level = models.CharField(
        choices=UserLevel.choice(),
        max_length=UserLevel.max_length(),
    )
    user_goal = models.CharField(
        choices=UserGoals.choice(),
        max_length=UserGoals.max_length()
    )
    user_activity = models.CharField(
        choices=UserActivity.choice(),
        max_length=UserActivity.max_length(),
    )

    weight_change_intensity = models.CharField(
        choices=WeightChangeIntensity.choices,
        max_length=20,
    )

    maintenance_calories = models.IntegerField(default=0)
    target_calories = models.IntegerField(default=0)

    def calculate_bmr(self):
        if self.gender == GENDER.MALE.value:
            return 88.362 + (13.397 * float(self.weight)) + (4.799 * float(self.height)) - (5.677 * self.age)
        else:
            return 447.593 + (9.247 * float(self.weight)) + (3.098 * float(self.height)) - (4.330 * self.age)

    def calculate_daily_calories_maintenance(self):
        if self.user_activity == '' or self.calculate_bmr() is None:
            return self.maintenance_calories
        else:
            activity_level = self.ACTIVITY_LEVELS.get(self.user_activity)
            self.maintenance_calories = int(self.calculate_bmr() * float(activity_level))
            return self.maintenance_calories

    def calculate_target_calories(self):
        if self.weight_change_intensity == WeightChangeIntensity.LIGHT:
            self.target_calories = self.maintenance_calories - 300
        elif self.weight_change_intensity == WeightChangeIntensity.MODERATE:
            self.target_calories = self.maintenance_calories - 500
        elif self.weight_change_intensity == WeightChangeIntensity.HIGH:
            self.target_calories = self.maintenance_calories - 1000
        return self.target_calories

    def save(self, *args, **kwargs):
        if self.age is not None and self.weight is not None and self.height is not None:
            self.maintenance_calories = self.calculate_daily_calories_maintenance()
            self.target_calories = self.calculate_target_calories()
        super().save(*args, **kwargs)


UserModel = get_user_model()


class Ingredients(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(null=True, blank=True)
    calories = models.IntegerField(null=True, blank=True)
    protein = models.IntegerField(null=True, blank=True, verbose_name='protein grams')
    carbohydrates = models.IntegerField(null=True, blank=True, verbose_name='carbohydrate grams')
    fats = models.IntegerField(null=True, blank=True, verbose_name='fat grams')
    quantity = models.IntegerField(null=True, blank=True, verbose_name='quantity', validators=[MinValueValidator(0)])

    def __str__(self):
        return f'{self.name} - Calories: {self.calories}, Protein: {self.protein}, Carbs: {self.carbohydrates}, Fats: {self.fats}'


class Meal(models.Model):
    name = models.CharField(max_length=30, validators=[MinLengthValidator(4)])
    total_calories = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    list_of_ingredients = models.JSONField(default=list, blank=True, null=True)
    total_protein = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    total_carbs = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    total_fats = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['name', 'user']]

    def save(self, *args, **kwargs):
        self.name = f"{self.name} by {self.user.username}"
        return super().save(*args, **kwargs)


class MealPlan(models.Model):
    title = models.CharField(max_length=100, )
    description = models.TextField()
    meals = models.ManyToManyField(Meal)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Exercise(models.Model):
    name = models.CharField(max_length=30)
    muscle_group = models.CharField(max_length=30)
    description = models.TextField()
    video_link = models.URLField(null=True, blank=True)


class Workout(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    created_by = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    exercises = models.ManyToManyField(Exercise, blank=True, null=True)

    def __str__(self):
        return self.name


class Plan(models.Model):
    name = models.CharField(max_length=30)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    workouts = models.ManyToManyField(Workout)
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    duration = models.IntegerField(verbose_name='Duration (in weeks)')
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

    def save(self, *args, **kwargs):
        self.start_date = self.start_date or datetime.now().date()
        self.end_date = self.start_date + timedelta(weeks=self.duration)
        super().save(*args, **kwargs)


class Progress(models.Model):
    current_plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    weight = models.FloatField(verbose_name='Weight in kgs')
    current_week = models.DateField(null=True, blank=True)
    body_fat_percentage = models.IntegerField(blank=True, null=True)

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return self.user.get_full_name()
        else:
            return self.user.username

    def calc_current_week(self):
        self.current_week = timedelta(weeks=datetime.now().date() - self.current_plan.start_time)
        return self.current_week


class ArticleModel(models.Model):
    title = models.CharField(max_length=30)
    article_content = models.TextField()
    created_by = models.ForeignKey(UserModel, models.CASCADE)
    date = models.DateField(auto_now_add=True)


class DailyCalorieIntake(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    breakfast = models.ForeignKey(Meal, related_name='breakfast_meals', null=True, blank=True,
                                  on_delete=models.SET_NULL)
    morning_snack = models.ForeignKey(Meal, related_name='morning_snack_meals', null=True, blank=True,
                                      on_delete=models.SET_NULL)
    lunch = models.ForeignKey(Meal, related_name='lunch_meals', null=True, blank=True, on_delete=models.SET_NULL)
    afternoon_snack = models.ForeignKey(Meal, related_name='afternoon_snack_meals', null=True, blank=True,
                                        on_delete=models.SET_NULL)
    dinner = models.ForeignKey(Meal, related_name='dinner_meals', null=True, blank=True, on_delete=models.SET_NULL)
    evening_snack = models.ForeignKey(Meal, related_name='evening_snack_meals', null=True, blank=True,
                                      on_delete=models.SET_NULL)
    total_calories = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s calorie intake for {self.date}"

    def calculate_total_calories(self):
        meals = [self.breakfast, self.morning_snack, self.lunch, self.afternoon_snack, self.dinner, self.evening_snack]
        return sum(meal.calories for meal in meals if meal is not None)

    def save(self, *args, **kwargs):
        self.total_calories = self.calculate_total_calories()
        super().save(*args, **kwargs)


class DailyUserReport(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    daily_intake_calories = models.ForeignKey(DailyCalorieIntake, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s report for {self.date}"

    @property
    def intaked_calories(self):
        return self.daily_intake_calories.total_calories

    @property
    def target_calories(self):
        return self.user.target_calories

    @property
    def weight(self):
        return self.user.weight
