import json
import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.forms import model_to_dict
from django.utils import timezone

from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import generic as views, View
from django.contrib.auth import models as auth_model
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormMixin
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from rest_framework import serializers, status
from rest_framework.generics import UpdateAPIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from rest_framework.views import APIView

from fitnes_tracker.accounts.forms import RegisterUserForm, UserDetailsForm, LoginUserForm, MealForm, CreateMealForm, \
    DailyCalorieIntakeForm
from fitnes_tracker.accounts.models import FitnessUser, DailyUserReport, DailyCalorieIntake, Meal, \
    Ingredients

import requests

from fitnes_tracker.accounts.utilis import Edamam

UserModel = get_user_model()


class OnlyNotRegisteredUsers:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponse(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)


class HomePageView(views.ListView):
    template_name = 'home/index.html'
    model = Meal
    context_object_name = 'meals'
    paginate_by = 12
    ordering = ['name']


class RegisterAccountView(OnlyNotRegisteredUsers, views.CreateView):
    template_name = 'accounts/register_account.html'
    form_class = RegisterUserForm

    def get_success_url(self):
        return reverse_lazy('account details', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        result = super().form_valid(form)
        login(self.request, self.object)
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next')
        return context


class ProfileUpdateView(LoginRequiredMixin, views.UpdateView):
    login_url = 'account login'
    template_name = 'accounts/update_account.html'
    model = UserModel
    form_class = UserDetailsForm
    success_url = reverse_lazy('account details')

    def get_success_url(self):
        return reverse_lazy('account details', kwargs={'pk': self.request.user.pk})


class ProfileDetailsView(LoginRequiredMixin, views.DetailView):
    login_url = 'account login'
    model = UserModel
    template_name = 'accounts/details_account.html'
    form_class = UserDetailsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class LoginUserView(auth_views.LoginView):
    form_class = LoginUserForm
    template_name = 'accounts/login_account.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('account details', kwargs={'pk': self.request.user.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next')
        return context

    def form_valid(self, form):
        login(self.request, form.get_user())
        if not self.request.user.weight or not self.request.user.height or not self.request.user.user_activity:
            return redirect('account update', pk=self.request.user.pk)
        next_url = self.request.POST.get('next')
        if next_url == 'None':
            next_url = 'account login'
        return redirect(next_url)


class LogoutUserView(auth_views.LogoutView):
    next_page = reverse_lazy('home page')


class GetFoodInfoView(View):
    def get(self, request, *args, **kwargs):
        form = MealForm()
        meal_id = request.session.get('meal_id')
        coming_from_details = request.session.get('coming_from_details', False)
        request.session['coming_from_details'] = False
        request.session.modified = True
        if meal_id is not None:
            meal = get_object_or_404(Meal, id=meal_id)
            context = {
                'form': form,
                'meal': meal,
                'meal_id': meal_id,
                'show_add_ingredient_button': coming_from_details,
            }
        else:
            context = {
                'form': form,
                'meal_id': None,
                'show_add_ingredient_button': coming_from_details,
            }

        return render(request, 'home/get_food_info.html', context=context)

    def post(self, request, *args, **kwargs):

        edamam = Edamam()
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}
        meal_name = data.get('food')
        selected_index = int(data.get('index', 0))
        meal_id = request.session.get('meal_id')

        if not meal_name:
            return JsonResponse({'error': 'No meal name provided'}, status=400)

        data = edamam.get_food_data(meal_name)
        foods = data.get('hints', [])
        food_types = [food['food']['label'] for food in foods]
        if foods:
            selected_food = foods[selected_index].get('food', {})
            nutrients = selected_food.get('nutrients', {})

            ingredient = {
                'quantity': self.request.POST.get('quantity', 0),
                'name': selected_food.get('label', 'Unknown'),
                'calories': int(float(nutrients.get('ENERC_KCAL', 0))),
                'protein': int(float(nutrients.get('PROCNT', 0))),
                'carbohydrates': int(float(nutrients.get('CHOCDF', 0))),
                'fats': int(float(nutrients.get('FAT', 0))),
                'food_types': food_types,
                'meal_id': meal_id,
            }
            # meal_dict = model_to_dict(ingredient)
            # meal_dict["food_types"] = food_types

            return JsonResponse(ingredient)

        return JsonResponse({'error': 'No food item found'}, status=404)


class GetFoodVarietiesView(View):
    def post(self, request, *args, **kwargs):
        edamam = Edamam()
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}
        meal_name = data.get('food')

        if not meal_name:
            return JsonResponse({'error': 'No meal name provided'}, status=400)

        data = edamam.get_food_data(meal_name)
        foods = data.get('hints', [])
        food_varieties = [food['food']['label'] for food in foods]

        return JsonResponse({'varieties': food_varieties})


class CreateMealView(LoginRequiredMixin, views.CreateView):
    template_name = 'Meal/create_meal.html'
    form_class = CreateMealForm
    model = Meal
    success_url = reverse_lazy('details meal')
    exclude = ['list_of_ingredients']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_success_url(self):
        return reverse_lazy('details meal', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class MealDetailsView(views.DetailView):
    template_name = 'Meal/details_meal.html'
    model = Meal

    def get(self, request, *args, **kwargs):
        request.session['coming_from_details'] = True
        meal = self.get_object()
        request.session['meal_id'] = meal.id
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meal_dict'] = model_to_dict(self.object)
        context['meal_id'] = self.object.id
        return context


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ['name', 'quantity', 'calories', 'protein', 'carbohydrates', 'fats']


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = '__all__'


class AddIngredientToMealView(LoginRequiredMixin, UpdateAPIView):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer

    def post(self, request, *args, **kwargs):
        meal = self.get_object()
        selected_ingredient = request.data.get('selectedIngredient')

        if selected_ingredient:
            ingredient, created = Ingredients.objects.get_or_create(
                name=selected_ingredient['name'],
                quantity=selected_ingredient['quantity'],
                calories=float(selected_ingredient['calories']),
                protein=float(selected_ingredient['protein']),
                carbohydrates=float(selected_ingredient['carbohydrates']),
                fats=float(selected_ingredient['fats']),
            )
            ingredient_serializer = IngredientsSerializer(ingredient)
            ingredient_data = ingredient_serializer.data
            ingredient_data.pop('id', None)
            ingredient_data = {str(key).replace("'", ""): str(value).replace("'", "") for key, value in
                               ingredient_data.items()}
            meal.list_of_ingredients.append(ingredient_data)

        meal.total_calories += float(selected_ingredient['calories'])
        meal.total_carbs += float(selected_ingredient['carbohydrates'])
        meal.total_fats += float(selected_ingredient['fats'])
        meal.total_protein += float(selected_ingredient['protein'])
        meal.save()

        meal_serializer = self.get_serializer(meal)
        return Response(meal_serializer.data, status=status.HTTP_200_OK)


class MealEditView(LoginRequiredMixin, views.UpdateView):
    model = Meal
    fields = '__all__'
    template_name = 'Meal/edit_meal.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        meal = get_object_or_404(Meal, pk=pk)
        if self.request.user != meal.user:
            raise PermissionDenied
        return meal

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        data_as_text = data['name']

        name_match = re.search(r'\s*(.*?)\s*-', data_as_text)
        quantity_match = re.search(r'(\d+)\s*', data_as_text)
        calories_match = re.search(r"Calories: (\d+)", data_as_text)
        protein_match = re.search(r"Protein: (\d+)", data_as_text)
        carbs_match = re.search(r"Carbs: (\d+)", data_as_text)
        fats_match = re.search(r"Fats: (\d+)", data_as_text)
        nutrition_info = {
            'fats': str(int(fats_match.group(1))) if fats_match else 0,
            'name': name_match.group(1) if name_match else None,
            'protein': str(int(protein_match.group(1))) if protein_match else 0,
            'calories': str(int(calories_match.group(1))) if calories_match else 0,
            'quantity': str(int(quantity_match.group(1))) if quantity_match else 0,
            'carbohydrates': str(int(carbs_match.group(1))) if carbs_match else 0,
        }

        meal = self.get_object()
        matched_ingredients = [ingredient for ingredient in meal.list_of_ingredients if
                               ingredient != nutrition_info]

        meal.total_fats -= int(nutrition_info['fats'])
        meal.total_protein -= int(nutrition_info['protein'])
        meal.total_carbs -= int(nutrition_info['carbohydrates'])
        meal.total_calories -= int(nutrition_info['calories'])

        meal.list_of_ingredients = matched_ingredients
        meal.save()

        return JsonResponse({'status': 'success'})


@method_decorator(login_required, name='dispatch')
class DeleteMealView(LoginRequiredMixin, views.DeleteView):
    model = Meal
    template_name = 'Meal/delete_meal.html'
    success_url = reverse_lazy('home page')

    def get_object(self, queryset=None):
        obj = super().get_object()
        if not obj.user == self.request.user:
            raise Http404
        else:
            return obj


class DailyCaloriesIntake(LoginRequiredMixin,views.UpdateView):
    model = DailyCalorieIntake
    form_class = DailyCalorieIntakeForm
    template_name = 'reports/daily_calories_intakes.html'


    def get_object(self, queryset=None):
        try:
            return DailyCalorieIntake.objects.get(user=self.request.user, date=timezone.now().date())
        except DailyCalorieIntake.DoesNotExist:
            return DailyCalorieIntake(user=self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        daily_report, created = DailyCalorieIntake.objects.get_or_create(user=self.request.user,
                                                                  date=timezone.now().date())

        # Update the respective meal in daily report
        for key in form.cleaned_data.keys():
            if hasattr(daily_report,key):
                setattr(daily_report,key,form.cleaned_data[key])
        daily_report.save()
        return response



    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account login')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('daily_calorie_intake', kwargs={'pk': self.request.user.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['daily_report'] = self.get_object()
        return context

class DailyReportListView(LoginRequiredMixin, views.ListView):
    model = DailyUserReport
    template_name = 'reports/daily_reports_list.html'
    context_object_name = 'reports'


@login_required
def generate_daily_report(request, pk):
    user = request.user
    today = timezone.now().date()
    if not DailyCalorieIntake.objects.filter(user=user, date=today).exists():
        return render(request, 'reports/daily_calories_intakes.html')
    else:
        data = DailyCalorieIntake.objects.get(user=user, date=today)

    if not DailyUserReport.objects.filter(user=user, date=today).exists():
        DailyUserReport.objects.create(
            user=data.user,
            date=data.today,
            daily_intake_calories=data.total_calories,
            daily_protein_intake=data.total_protein,
            daily_carbs_intake=data.total_carbs,
            daily_fats_intake=data.total_fats,
            weight=user.weight,
        )
    daily_report_last = DailyUserReport.objects.filter(user=user, date=today)

    context = {
        'daily_report': daily_report_last,
    }
    return render(request, 'reports/daily_calories_intakes.html', context=context)
