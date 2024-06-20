from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [

    path('register/', views.UserRegisterView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutView.as_view(), name='user-logout'),
    path('profile/<int:pk>/', views.UserProfileView.as_view(), name='user-profile'),
    path('reset/', views.UserPasswordResetView.as_view(), name='reset-password'),
    path('reset/done/', views.UserPasswordResetDone.as_view(), name='password-reset-done'),

]
