from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin

from .forms import UserRegisterForm, UserLoginForm, UserProfileForm
from home.models import Post
from .models import Relation


class UserRegisterView(View):
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'شما در حال حاضر لاگین هستید', extra_tags='info')
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

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

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

                if self.next:
                    return redirect(self.next)
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

    # def dispatch(self, request, *args, **kwargs):
    #     user = get_object_or_404(User, pk=kwargs['pk'])
    #     if request.user.id != user.id:
    #         return redirect('home:home')
    #     return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        is_following = False
        user = get_object_or_404(User, pk=pk)
        form = self.form_class(instance=request.user, initial={
            'age': user.profile.age,
            'bio': user.profile.bio,
        })
        posts = user.posts.all()
        relation = Relation.objects.filter(from_user=request.user, to_user=user)

        if relation.exists():
            is_following = True

        return render(request, self.template_name, {
            'user': user,
            'form': form,
            'posts': posts,
            'is_following': is_following
        })

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = self.form_class(request.POST, instance=user)
        if form.is_valid():
            form.save()
            user.profile.age = form.cleaned_data['age']
            user.profile.bio = form.cleaned_data['bio']
            user.profile.save()
            messages.success(request, 'اطلاعات شما با موفقیت تغییر کرد', extra_tags='success')
            return redirect('home:home')
        return render(request, self.template_name, {'form': form})


class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('accounts:password-reset-done')
    email_template_name = 'accounts/password_reset_email.html'


class UserPasswordResetDone(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password-reset-complete')


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


class UserFollowView(LoginRequiredMixin, View):
    def get(self, request, pk):

        user = get_object_or_404(User, id=pk)
        if request.user == user:
            messages.error(request, 'شما نمی‌توانید خودتان را فالو کنید', extra_tags='error')
            return redirect('accounts:user-profile', user.id)

        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            messages.error(request, 'شما در حال حاضر هم این کاربر فالوو می کنید', extra_tags='error')
        else:
            Relation.objects.create(from_user=request.user, to_user=user)
            messages.success(request, 'شما این کاربر رو با موفقیت فالوو کردید', extra_tags='success')
        return redirect('accounts:user-profile', user.id)


class UserUnFollowView(LoginRequiredMixin, View):
    def get(self, request, pk):
        user = get_object_or_404(User, id=pk)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            relation.delete()
            messages.success(request, 'شما با موفقیت این کاربر رو حذف کردید', extra_tags='success')
        else:
            messages.error(request, 'شما این کاربر رو فالوو ندارید', extra_tags='error')

        return redirect('accounts:user-profile', user.id)
