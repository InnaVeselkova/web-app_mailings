from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Mailing, Recipient, Message
from .forms import MailingForm, RecipientForm, MessageForm
from .utils import initiate_sending_mailing


class HomeListView(ListView):
    model = Mailing
    template_name = 'mailings/home.html'

    def get_context_data(self, **kwargs):
        # Сначала вызываем метод родительского класса
        context = super().get_context_data(**kwargs)

        # Общее количество всех созданных рассылок
        total_mailings = Mailing.objects.count()

        # Количество активных рассылок
        now = timezone.now()
        active_mailings = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            status='Запущена'
        ).count()

        # Добавляем данные в контекст
        context['total_mailings'] = total_mailings
        context['active_mailings'] = active_mailings

        return context


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # ← пересчёт и сохранение статуса
        return obj


class MailingCreateView(CreateView):
    def get(self, request):
        # Отображаем пустую форму при GET-запросе
        form = MailingForm()
        return render(request, 'mailings/mailing_form.html', {'form': form})

    def post(self, request):
        form = MailingForm(request.POST)

        if form.is_valid():
            mailing = form.save(commit=False)  # Сохраняем рассылку, но не в базе данных
            mailing.owner = request.user  # Устанавливаем владельца
            mailing.save()  # Теперь сохраняем экземпляр в базу данных
            mailing.recipients.set(form.cleaned_data['recipients'])  # Устанавливаем получателей
            return redirect('mailings:home')

        return render(request, 'mailings/mailing_form.html', {'form': form})


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:home')


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:home')


class RecipientListView(ListView):
    model = Recipient
    template_name = 'mailings/recipient_list.html'


class RecipientDetailView(DetailView):
    model = Recipient
    template_name = 'mailings/recipient_detail.html'


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def form_valid(self, form):
        recipient = form.save(commit=False)  # Создаем объект, но не сохраняем
        recipient.owner = self.request.user  # Устанавливаем владельца
        recipient.save()  # Теперь сохраняем объект в базе данных
        return super().form_valid(form)

class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')


class RecipientDeleteView(DeleteView):
    model = Recipient
    template_name = 'mailings/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailings:recipient_list')


class MessageListView(ListView):
    model = Message
    template_name = 'mailings/message_list.html'


class MessageDetailView(DetailView):
    model = Message
    template_name = 'mailings/message_detail.html'


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def form_valid(self, form):
        message = form.save(commit=False)  # Создаем объект, но не сохраняем
        message.owner = self.request.user  # Устанавливаем владельца
        message.save()  # Теперь сохраняем объект в базе данных
        return super().form_valid(form)

class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')


class InitiateMailingView(View):
    def get(self, request, mailing_id):
        mailing = get_object_or_404(Mailing, id=mailing_id)  # Получаем рассылку по ID
        success = initiate_sending_mailing(mailing)  # Вызываем функцию отправки

        if success:
            return HttpResponse("Рассылка успешно инициирована.")  # Успешное сообщение
        else:
            return HttpResponse("Ошибка: Текущее время вне диапазона рассылки.")

