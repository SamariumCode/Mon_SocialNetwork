from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
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


class PostDeleteView(LoginRequiredMixin, View):

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.user.id == request.user.id:
            return render(request, 'home/post_confirm_delete.html', {'post': post})
        else:
            return redirect('home:home')

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.user.id == request.user.id:
            post.delete()
            messages.success(request, 'پست شما با موفقیت حذف شد', extra_tags='success')
        else:
            messages.error(request, 'شما اجازه ندارید این پست رو حذف کنید', extra_tags='danger')
        return redirect('home:home')
