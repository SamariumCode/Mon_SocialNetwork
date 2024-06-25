from django.urls import path
from . import views


app_name = 'home'


urlpatterns = [

    path('', views.HomeView.as_view(), name='home'),
    path('post/<int:pk>/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/delete/<int:pk>/', views.PostDeleteView.as_view(), name='post-delete'),
    path('post/update/<int:pk>/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/create/', views.PostCreateView.as_view(), name='post-create'),
    path('reply/<int:post_pk>/<int:commet_pk>/', views.PostAddReplyView.as_view(), name='add-reply'),
    path('like/<int:pk>/', views.PostLikeView.as_view(), name='post-like'),

]
