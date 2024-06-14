from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import View

from .models import Post


class HomeView(View):
    def get(self, request):
        posts = Post.objects.all()
        return render(request, 'home/index.html', {'posts': posts})


class PostDetailView(View):
    def get(self, request, pk, slug):
        post = get_object_or_404(Post, pk=pk, slug=slug)
        return render(request, 'home/detail.html', {'post': post})
