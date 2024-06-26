from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
# from django.utils.text import slugify
from slugify import slugify
from django.views import View

from .models import Post, Comment, Vote
from .forms import PostCreateUpdateForm, CommentForm, CommentReplyForm, PostSearchForm


class HomeView(View):
    form_class = PostSearchForm

    def get(self, request):
        posts = Post.objects.all()

        if request.GET.get('search'):
            posts = posts.filter(body__icontains=request.GET['search'])

        return render(request, 'home/index.html', {'posts': posts, 'form': self.form_class})


class PostDetailView(View):
    form_class = CommentForm
    form_class_reply = CommentReplyForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(
            Post, pk=kwargs['pk'], slug=kwargs['slug'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, pk, slug):
        can_like = False
        if request.user.is_authenticated and self.post_instance.user_can_like(request.user):
            can_like = True

        comments = self.post_instance.pcomments.filter(is_reply=False)
        return render(request, 'home/detail.html',
                      {'post': self.post_instance, 'comments': comments, 'form': self.form_class,
                       'reply_form': self.form_class_reply, 'can_like': can_like})

    @method_decorator(login_required)
    def post(self, request, pk, slug):
        form = self.form_class(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.post_instance
            comment.user = request.user
            comment.save()
            messages.success(
                request, 'نظر شما با موفقیت ذخیره شد', extra_tags='success')
            return redirect('home:post-detail', pk=self.post_instance.pk, slug=self.post_instance.slug)
        else:
            comments = self.post_instance.pcomments.filter(is_reply=False)
            messages.warning(
                request, '.لطفا درست و حسابی فرم رو پر کن', extra_tags='warning')
        return render(request, 'home/detail.html', {'post': self.post_instance, 'form': form, 'comments': comments})


class PostDeleteView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])

        if not post.user.id == request.user.id:
            messages.error(
                request, 'شما اجازه حذف این پست رو ندارید', extra_tags='danger')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        return render(request, 'home/post_confirm_delete.html', {'post': post})

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        messages.success(request, 'پست شما با موفقیت حذف شد',
                         extra_tags='success')
        return redirect('home:home')


class PostUpdateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['pk'])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        post = self.post_instance
        if not post.user.id == request.user.id:
            messages.error(
                request, 'شما اجازه بروزرسانی پست رو ندارید', extra_tags='danger')
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

            messages.success(
                request, 'اطلاعات پست با موفقیت تغییر کرد', extra_tags='success')
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
            messages.success(
                request, 'پست شما با موفقیت ذخیره شد', extra_tags='success')
            return redirect('home:post-detail', new_post.id, new_post.slug)

        return render(request, 'home/create.html', {'form': form})


class PostAddReplyView(LoginRequiredMixin, View):
    form_class = CommentReplyForm

    def post(self, request, post_pk, commet_pk):
        post = get_object_or_404(Post, pk=post_pk)
        comment = get_object_or_404(Comment, pk=commet_pk)
        form = self.form_class(request.POST)

        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.reply = comment
            reply.is_reply = True
            reply.save()
            messages.success(
                request, 'نظر شما با موفقیت ثبت شد', extra_tags='success')
        return redirect('home:post-detail', post.pk, post.slug)


class PostLikeView(LoginRequiredMixin, View):

    # def dispatch(self, request, *args, **kwargs):
    #     post = get_object_or_404(Post, pk=kwargs['pk'])
    #     vote = Vote.objects.filter(post=post, user=request.user)
    #
    #     if vote.exists():
    #         if vote.first().user == request.user:
    #             messages.error(request, 'شما قبلاً این پست را لایک کرده‌اید', extra_tags='danger')
    #             return redirect('home:home')
    #
    #     return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like = Vote.objects.filter(post=post, user=request.user)

        if like.exists():
            messages.error(request, 'شما این پست رو قبلا لایک کردید', extra_tags='danger')
        else:
            Vote.objects.create(post=post, user=request.user)
            messages.success(request, 'شما این پست رو لایک کردید', extra_tags='success')
        return redirect('home:post-detail', post.pk, post.slug)
