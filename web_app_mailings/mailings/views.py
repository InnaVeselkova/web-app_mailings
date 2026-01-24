from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Mailing, Recipient, Message
from .forms import MailingForm, RecipientForm, MessageForm
from .utils import initiate_sending_mailing
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


class OwnerOrManagerMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        # Проверка, что пользователь — владелец или менеджер
        return user.is_superuser or user.is_staff or obj.owner == user


class OwnerOnlyMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class HomeListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailings/home.html"

    def get_context_data(self, **kwargs):
        # Сначала вызываем метод родительского класса
        context = super().get_context_data(**kwargs)

        # Общее количество всех созданных рассылок
        total_mailings = Mailing.objects.count()

        # Общее количество всех получателей
        total_recipients = Recipient.objects.filter(mailing__isnull=False).distinct().count()

        # Количество активных рассылок
        now = timezone.now()
        active_mailings = Mailing.objects.filter(start_time__lte=now, end_time__gte=now, status="Запущена").count()

        # Добавляем данные в контекст
        context["total_mailings"] = total_mailings
        context["active_mailings"] = active_mailings
        context["total_recipients"] = total_recipients

        return context


@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingDetailView(OwnerOrManagerMixin, DetailView):
    model = Mailing
    template_name = "mailings/mailing_detail.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # ← пересчёт и сохранение статуса
        return obj


class MailingCreateView(OwnerOnlyMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        return render(request, "mailings/mailing_form.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.owner = request.user
            mailing.save()
            mailing.recipients.set(form.cleaned_data["recipients"])
            return redirect("mailings:home")
        return render(request, "mailings/mailing_form.html", {"form": form})


class MailingUpdateView(OwnerOnlyMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:home")


class MailingDeleteView(OwnerOnlyMixin, DeleteView):
    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:home")


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = "mailings/recipient_list.html"

    def get_queryset(self):
        user = self.request.user
        cache_key = f"recipients_user_{user.id}"
        queryset = cache.get(cache_key)
        if queryset is None:
            if user.is_superuser or user.is_staff:
                queryset = list(Recipient.objects.all())
            else:
                queryset = list(Recipient.objects.filter(owner=user))
            cache.set(cache_key, queryset, 300)  # кешировать 5 минут
        return queryset


@method_decorator(cache_page(60 * 15), name="dispatch")
class RecipientDetailView(OwnerOrManagerMixin, DetailView):
    model = Recipient
    template_name = "mailings/recipient_detail.html"


class RecipientCreateView(OwnerOnlyMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailings/recipient_form.html"
    success_url = reverse_lazy("mailings:recipient_list")

    def form_valid(self, form):
        recipient = form.save(commit=False)  # Создаем объект, но не сохраняем
        recipient.owner = self.request.user  # Устанавливаем владельца
        recipient.save()  # Теперь сохраняем объект в базе данных
        return super().form_valid(form)


class RecipientUpdateView(OwnerOnlyMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailings/recipient_form.html"
    success_url = reverse_lazy("mailings:recipient_list")


class RecipientDeleteView(OwnerOnlyMixin, DeleteView):
    model = Recipient
    template_name = "mailings/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailings:recipient_list")


@method_decorator(cache_page(60 * 15), name="dispatch")
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailings/message_list.html"

    def get_queryset(self):
        user = self.request.user
        # Менеджеры видят всех
        if user.is_superuser or user.is_staff:
            return Message.objects.all()
        # Обычные пользователи — только свои
        return Message.objects.filter(owner=user)


@method_decorator(cache_page(60 * 15), name="dispatch")
class MessageDetailView(OwnerOrManagerMixin, DetailView):
    model = Message
    template_name = "mailings/message_detail.html"


class MessageCreateView(OwnerOnlyMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:message_list")

    def form_valid(self, form):
        message = form.save(commit=False)  # Создаем объект, но не сохраняем
        message.owner = self.request.user  # Устанавливаем владельца
        message.save()  # Теперь сохраняем объект в базе данных
        return super().form_valid(form)


class MessageUpdateView(OwnerOnlyMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:message_list")


class MessageDeleteView(OwnerOnlyMixin, DeleteView):
    model = Message
    template_name = "mailings/message_confirm_delete.html"
    success_url = reverse_lazy("mailings:message_list")


class InitiateMailingView(View, OwnerOrManagerMixin):
    def get(self, request, mailing_id):
        mailing = get_object_or_404(Mailing, id=mailing_id)  # Получаем рассылку по ID
        success = initiate_sending_mailing(mailing, request.user)

        if success:
            return HttpResponse("Рассылка успешно инициирована.")
        else:
            return HttpResponse("Ошибка: Текущее время вне диапазона рассылки.")
