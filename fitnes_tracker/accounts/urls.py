from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from fitnes_tracker.accounts.views import RegisterAccountView, HomePageView, ProfileUpdateView, ProfileDetailsView, \
    LoginUserView, LogoutUserView, generate_daily_report, DashboardUserView, GetFoodInfoView, GetFoodVarietiesView, \
    CreateMealView, MealDetailsView, AddIngredientToMealView, MealEditView, DeleteMealView

urlpatterns = [
                  path('', HomePageView.as_view(), name='home page'),
                  path('register/', RegisterAccountView.as_view(), name='account register'),
                  path('<int:pk>/details/', ProfileDetailsView.as_view(), name='account details'),
                  path('<int:pk>/update/', ProfileUpdateView.as_view(), name='account update'),
                  path('login/', LoginUserView.as_view(), name='account login'),
                  path('logout/', LogoutUserView.as_view(), name='account logout'),
                  path('<int:pk>/generate_daily_repot/', generate_daily_report, name='daily_report'),
                  path('<int:pk>/dashboard/', DashboardUserView.as_view(), name='dashboard'),
                  path('api/get_food_info/', GetFoodInfoView.as_view(), name='get_food_info'),
                  path('api/get_food_varieties/', GetFoodVarietiesView.as_view(), name='get_food_varieties'),
                  path('create_meal/', CreateMealView.as_view(), name='create meal'),
                  path('meal_<int:pk>', MealDetailsView.as_view(), name='details meal'),
                  path('meal_<int:pk>/add_food/', AddIngredientToMealView.as_view(), name='add_food_to_meal'),
                  path('meal_<int:pk>/edit/', MealEditView.as_view(), name='edit_meal'),
                  path('meal_<int:pk>/delete/', DeleteMealView.as_view(), name='delete_meal'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
