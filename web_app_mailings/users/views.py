from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView

from django.shortcuts import render, redirect
from django.urls import reverse_lazy


from .forms import UserRegisterForm
from mailings.models import Mailing, Attempt


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
def profile(request):
    user = request.user
    mailings = Mailing.objects.filter(owner=user)

    # Получаем все попытки этого пользователя
    attempts = Attempt.objects.filter(owner=user)

    total_attempts = attempts.count()
    success_attempts = attempts.filter(status="Успешно").count()
    failed_attempts = attempts.filter(status="Не успешно").count()

    # Количество отправленных сообщений — это успешные попытки
    sent_messages = success_attempts

    context = {
        "mailings": mailings,
        "total_attempts": total_attempts,
        "success_attempts": success_attempts,
        "failed_attempts": failed_attempts,
        "sent_messages": sent_messages,
    }
    return render(request, "users/profile.html", context)


class CustomPasswordResetView(PasswordResetView):
    template_name = "users/password_reset_form.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"
    success_url = reverse_lazy("users:password_reset_done")
