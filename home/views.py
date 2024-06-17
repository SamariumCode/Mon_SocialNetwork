from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from django.views import View

from .models import Post
from .forms import PostCreateUpdateForm


class HomeView(View):
    def get(self, request):
        posts = Post.objects.all()
        return render(request, 'home/index.html', {'posts': posts})


class PostDetailView(View):
    def get(self, request, pk, slug):
        post = get_object_or_404(Post, pk=pk, slug=slug)
        return render(request, 'home/detail.html', {'post': post})


class PostDeleteView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])

        if not post.user.id == request.user.id:
            messages.error(request, 'شما اجازه حذف این پست رو ندارید', extra_tags='danger')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        return render(request, 'home/post_confirm_delete.html', {'post': post})

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        messages.success(request, 'پست شما با موفقیت حذف شد', extra_tags='success')
        return redirect('home:home')


class PostUpdateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['pk'])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        post = self.post_instance
        if not post.user.id == request.user.id:
            messages.error(request, 'شما اجازه بروزرسانی پست رو ندارید', extra_tags='danger')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(instance=post)
        return render(request, 'home/update.html', {'post': post, 'form': form})

    def post(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(request.POST, instance=post)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.save()

            messages.success(request, 'اطلاعات پست با موفقیت تغییر کرد', extra_tags='success')
            return redirect('home:post-detail', post.id, post.slug)
        return render(request, 'home/update.html', {'form': form})


class PostCreateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, 'home/create.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.user = request.user
            new_post.save()
            messages.success(request, 'پست شما با موفقیت ذخیره شد', extra_tags='success')
            return redirect('home:post-detail', new_post.id, new_post.slug)

        return render(request, 'home/create.html', {'form': form})
