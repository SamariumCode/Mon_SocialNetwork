from django.urls import path
from . import views


app_name = 'home'


urlpatterns = [

    path('', views.HomeView.as_view(), name='home'),
    path('post/<int:pk>/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/delete/<int:pk>/', views.PostDeleteView.as_view(), name='post-delete'),

]
