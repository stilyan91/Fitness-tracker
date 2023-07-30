import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.utils import timezone

from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import generic as views, View
from django.contrib.auth import models as auth_model
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormMixin
from django.contrib.auth import views as auth_views
from django.http import JsonResponse

from rest_framework.views import APIView

from fitnes_tracker.accounts.forms import RegisterUserForm, UserDetailsForm, LoginUserForm, MealForm, CreateMealForm
from fitnes_tracker.accounts.models import ArticleModel, FitnessUser, DailyUserReport, DailyCalorieIntake, Meal, \
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
    model = ArticleModel


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


@login_required
def generate_daily_report(request, pk):
    user = request.user
    today = timezone.now().date()
    if not DailyCalorieIntake.objects.filter(user=user, date=today).exists():
        return render(request, 'accounts/daily_report.html')  # !!!!!!!!!!!!!!!!!! to fix redirect !!!!!!!!!!!!!!
    else:
        intake_calories_today = DailyCalorieIntake.objects.get(user=user, date=today)

    if not DailyUserReport.objects.filter(user=user, date=today).exists():
        DailyUserReport.objects.create(
            user=user,
            date=today,
            daily_intake_calories=intake_calories_today,
            target_calories=user.target_calories,
            weigth=user.weigth
        )
    daily_report_last = DailyUserReport.objects.filter(user=user).lastest('date')
    daily_reports = DailyUserReport.objects.all()

    context = {
        'daily_report': daily_report_last,
        'daily_reports': daily_reports,
    }
    return render(request, 'accounts/daily_report.html', context=context)


class DailyCaloriesIntake(LoginRequiredMixin, views.CreateView):
    pass


class DashboardUserView(LoginRequiredMixin, views.TemplateView):
    login_url = 'account login'
    template_name = 'home/dashboard.html'


class GetFoodInfoView(View):
    def get(self, request, *args, **kwargs):
        form = MealForm()
        context = {
            'form': form,
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

        if not meal_name:
            return JsonResponse({'error': 'No meal name provided'}, status=400)

        data = edamam.get_food_data(meal_name)
        foods = data.get('hints', [])
        food_types = [food['food']['label'] for food in foods]
        if foods:
            selected_food = foods[selected_index].get('food', {})
            nutrients = selected_food.get('nutrients', {})

            ingredient = Ingredients.objects.create(
                quantity=self.request.POST.get('quantity', 0),
                name=selected_food.get('label', 'Unknown'),
                calories=int(float(nutrients.get('ENERC_KCAL', 0))),
                protein=int(float(nutrients.get('PROCNT', 0))),
                carbohydrates=int(float(nutrients.get('CHOCDF', 0))),
                fats=int(float(nutrients.get('FAT', 0))),

            )
            meal_dict = model_to_dict(ingredient)
            meal_dict["food_types"] = food_types

            return JsonResponse(meal_dict)

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


class CreateMealView(LoginRequiredMixin,views.CreateView):
    template_name = 'home/create_meal.html'
    form_class = CreateMealForm
    queryset = []
