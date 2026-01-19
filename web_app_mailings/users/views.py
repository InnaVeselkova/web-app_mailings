from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import UserRegisterForm

# Функция для регистрации нового пользователя
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем нового пользователя
            return redirect('login')  # Перенаправляем на страницу входа
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# Функция для входа
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)  # Используйте username вместо email
        if user is not None:
            if user.is_blocked:
                return render(request, 'users/login.html', {'error': 'This account has been blocked.'})
            login(request, user)  # Успешный вход
            return redirect('users:profile')  # Предполагаем, что у вас есть URL для профиля
        else:
            return render(request, 'users/login.html', {'error': 'Invalid email or password.'})

    return render(request, 'users/login.html')  # Отображение формы входа

# Функция для отображения профиля
def profile(request):
    return render(request, 'users/profile.html')
