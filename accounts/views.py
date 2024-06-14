from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages


from . forms import UserRegisterForm


class RegisterView(View):

    form_class = UserRegisterForm
    template_name = 'accounts/register.html'

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
