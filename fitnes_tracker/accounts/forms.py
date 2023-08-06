from django import forms
from django.contrib.auth import models as auth_models, get_user_model
from django.contrib.auth import forms as auth_forms
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from fitnes_tracker.accounts.models import GENDER, UserRole, UserLevel, UserActivity, UserGoals, Meal, Ingredients, \
    DailyCalorieIntake

UserModel = get_user_model()


class RegisterUserForm(auth_forms.UserCreationForm):
    class Meta(auth_forms.UserCreationForm.Meta):
        model = UserModel
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class UserDetailsForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-username-input",
        "placeholder": "Change your username",
        "help_text": '',
    }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-user-first-name",
        "placeholder": "Enter your first name",
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-user-last-name",
        "placeholder": "Enter your last name",
    }))
    age = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={
        "class": "form-user-age",
        "placeholder": "Enter your age",
    }))
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        "class": "form-user-picture",
        "placeholder": "Upload your profile picture",
    }))
    height = forms.FloatField(required=True, widget=forms.NumberInput(attrs={
        'step': "0.01",
        "class": "form-user-height",
        "placeholder": "Enter your height",
    }))
    weight = forms.FloatField(required=True, widget=forms.NumberInput(attrs={
        'step': "0.01",
        "class": "form-user-weight",
        "placeholder": "Enter your weight",
    }))
    gender = forms.ChoiceField(required=True, choices=GENDER.choice(), widget=forms.Select(attrs={
        "class": "form-user-gender",
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-user-email",
        "placeholder": "Enter your email",
    }))
    user_role = forms.ChoiceField(choices=UserRole.choice(), widget=forms.Select(attrs={
        "class": "form-user-role",
    }),
                                  initial=UserRole.FITNESS_ENTHUSIAST)

    user_level = forms.ChoiceField(choices=UserLevel.choice(), widget=forms.Select(attrs={
        "class": "form-user-level"
    }),
                                   initial=UserLevel.BEGINNER)

    user_activity = forms.ChoiceField(required=True, choices=UserActivity.choice(), widget=forms.Select(attrs={
        "class": "form-user-activity",
    }),
                                      initial=UserActivity.SEDENTARY)
    user_goal = forms.ChoiceField(choices=UserGoals.choice(), widget=forms.Select(attrs={
        "class": "form-user-goals",
    }))

    class Meta:
        model = UserModel
        fields = ['username', 'first_name', 'last_name', 'email', 'profile_picture',
                  'height', 'weight', 'gender', 'age', 'user_role',
                  'user_level', 'user_activity', 'user_goal']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('profile_picture'):
            instance.profile_picture = self.cleaned_data['profile_picture']
        if commit:
            instance.save()
        return instance


class LoginUserForm(auth_forms.AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            "placeholder": "Enter your Username",
            "class": "login-user"})
        self.fields['username'].error_messages = {'required': 'Please enter your username',
                                                  'invalid': 'Invalid username'}
        self.fields['password'].widget.attrs.update({
            "placeholder": "Enter your Password",
            "class": "login-password",
        })
        self.fields['password'].error_messages = {'required': 'Please enter your password',
                                                  'invalid': 'Invalid password'}


class MealForm(forms.ModelForm):
    class Meta:
        model = Ingredients
        fields = '__all__'
        exclude = ['description']
        labels = {
            'name': 'Meal name',
            'calories': 'Calories - kcal/100g',
            'protein': 'Protein - g/100g',
            'carbohydrates': 'Carbohydrates - g/100g',
            'fats': 'Fats - g/100g',
            'quantity': "Quantity in grams"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'id': 'mealName', 'placeholder': 'Food'})
        self.fields['calories'].widget.attrs.update(
            {'id': 'id_calories', 'placeholder': 'calories', 'readonly': 'readonly'})
        self.fields['protein'].widget.attrs.update(
            {'id': 'id_protein', 'placeholder': 'protein', 'readonly': 'readonly'})
        self.fields['carbohydrates'].widget.attrs.update(
            {'id': 'id_carbohydrates', 'placeholder': 'carbs', 'readonly': 'readonly'})
        self.fields['fats'].widget.attrs.update({'id': 'id_fats', 'placeholder': 'fats', 'readonly': 'readonly'})
        self.fields['quantity'].widget.attrs.update({'id': 'id_quantity', 'placeholder': 'quantity'})


class CreateMealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = '__all__'
        labels = {
            'name': 'Name',
            'list_of_ingredients': 'Ingredients:',
            "total_protein": 'Total protein - grams:',
            'total_carbs': 'Total carbs - grams:',
            'total_fats': 'Total fats - grams:',
            'total_calories': 'Total calories - kcal:',
            'user': 'Created by:',
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields.pop('list_of_ingredients')
        if self.request.user.is_authenticated:
            self.fields['user'].initial = self.request.user
            self.fields['user'].widget = forms.HiddenInput()
        self.fields['username'] = forms.CharField(initial=self.request.user.username,
                                                  widget=forms.TextInput(attrs={'readonly': 'readonly'}))
        for field_name in self.fields:
            if self.fields[field_name] != self.fields['name']:
                self.fields[field_name].widget.attrs.update({'class': 'create-meal-form', 'readonly': 'readonly'})


class DailyCalorieIntakeForm(forms.ModelForm):
    class Meta:
        model = DailyCalorieIntake
        fields = ['breakfast', 'morning_snack', 'lunch', 'afternoon_snack', 'dinner', 'evening_snack']

        breakfast = forms.ModelChoiceField(
            queryset=Meal.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control', }),
            required=False,
        )
        morning_snack = forms.ModelChoiceField(
            queryset=Meal.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control', }),
            required=False,
        )

        lunch = forms.ModelChoiceField(
            queryset=Meal.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control', }),
            required=False,
        )
        afternoon_snack = forms.ModelChoiceField(
            queryset=Meal.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control', }),
            required=False,
        )

        dinner = forms.ModelChoiceField(
            queryset=Meal.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control', }),
            required=False,
        )

        evening_snack = forms.ModelChoiceField(
            queryset=Meal.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control', }),
            required=False,
        )
