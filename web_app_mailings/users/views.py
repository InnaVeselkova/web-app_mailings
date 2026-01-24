from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView, ListView

from .forms import UserRegisterForm
from mailings.models import Mailing, Attempt

from .models import CustomUser


# Функция для регистрации нового пользователя
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем нового пользователя
            return redirect("mailings:home")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


# Функция для входа
def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        print(user)
        if user is not None:
            if user.is_blocked:
                return render(request, "users/login.html", {"error": "This account has been blocked."})
            login(request, user)  # Успешный вход
            return redirect("mailings:home")
        else:
            return render(request, "users/login.html", {"error": "Invalid email or password."})
    return render(request, "users/login.html")  # Отображение формы входа


# Функция для отображения профиля
class UserMailingsView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "users/st_mailings.html"
    context_object_name = "mailings"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        attempts = Attempt.objects.filter(owner=user)

        context["total_attempts"] = attempts.count()
        context["success_attempts"] = attempts.filter(status="Успешно").count()
        context["failed_attempts"] = attempts.filter(status="Не успешно").count()
        context["sent_messages"] = context["success_attempts"]
        return context


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        context = {
            "user": user,
            "avatar_url": user.avatar.url if user.avatar else None,
            "country": user.country.name if user.country else None,
        }
        return render(request, "users/profile.html", context)


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    fields = ["username", "email", "phone_number", "avatar", "country"]
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user


class CustomPasswordResetView(PasswordResetView):
    template_name = "users/password_reset_form.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"
    success_url = reverse_lazy("users:password_reset_done")
