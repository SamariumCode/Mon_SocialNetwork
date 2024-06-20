from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse, reverse_lazy
from django.views import View

from .forms import UserRegisterForm, UserLoginForm, UserProfileForm
from home.models import Post


class UserRegisterView(View):
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(
                username=cd['username'], email=cd['email'], password=cd['password1'])
            messages.success(
                request, 'شما با موفقیت ثبت نام شدید', extra_tags='success')
            return redirect('home:home')
        return render(request, self.template_name, {'form': form})


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'کاربر گرامی شما با موفقیت وارد شدید', extra_tags='success')
                return redirect('home:home')
            messages.error(request, 'ایمیل یا رمز عبور شما درست وارد نشده است', extra_tags='warning')
        return render(request, self.template_name, {'form': form})


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'شما با موفقیت خارج شدید', extra_tags='success')
        return redirect('home:home')


class UserProfileView(LoginRequiredMixin, View):
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'

    def dispatch(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs['pk'])
        if request.user.id != user.id:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = self.form_class(instance=user)
        post = Post.objects.filter(user=user)
        # post = get_list_or_404(Post, user=user)  if the user does not have a post, return page 404
        return render(request, self.template_name, {'user': user, 'form': form, 'posts': post})

    def post(self, request, pk):
        user = User.objects.get(pk=pk)
        form = self.form_class(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات شما با موفقیت تغییر کرد', extra_tags='success')
            return redirect('home:home')
        return render(request, self.template_name, {'form': form})


class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'

