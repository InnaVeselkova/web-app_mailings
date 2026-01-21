import pytz
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

from users.models import CustomUser


# Получатель рассылки
class Recipient(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='Ф.И.О.')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Владелец')

    def __str__(self):
        return f'{self.full_name} ({self.email})'

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'


# Сообщение для рассылки
class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Владелец')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


# Рассылка
class Mailing(models.Model):
    STATUS_CHOICES = [
        ('Создана', 'Создана'),
        ('Запущена', 'Запущена'),
        ('Завершена', 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name='Дата и время начала')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Создана',
        verbose_name='Статус'
    )

    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Сообщение')
    recipients = models.ManyToManyField(Recipient, verbose_name='Получатели')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Владелец')

    def update_status(self):
        """Обновляет статус рассылки в зависимости от текущего московского времени."""
        moscow_tz = pytz.timezone('Europe/Moscow')
        now = timezone.now().astimezone(moscow_tz)
        new_status = self.status

        if self.start_time > now:
            new_status = 'Создана'
        elif self.start_time <= now <= self.end_time:
            new_status = 'Запущена'
        else:
            new_status = 'Завершена'

        # Если статус изменился, сохраняем его
        if self.status != new_status:
            self.status = new_status

    def save(self, *args, **kwargs):
        self.update_status()
        super().save(*args, **kwargs)

    def clean(self):
        """Валидация на уровне модели."""
        # Проверяем, что дата начала не в прошлом (при создании)
        if not self.pk and self.start_time and self.start_time < timezone.now():
            raise ValidationError({'start_time': 'Дата начала не может быть в прошлом.'})

        # Проверяем, что дата начала раньше даты окончания
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({'end_time': 'Дата окончания должна быть позже даты начала.'})

    def __str__(self):
        return f'Рассылка #{self.pk} от {self.start_time.strftime("%Y.%m.%d %H:%M")}'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class Attempt(models.Model):
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(max_length=20, choices=(('Успешно', 'Успешно'), ('Не успешно', 'Не успешно')), verbose_name='Статус')
    server_response = models.TextField(verbose_name='Ответ почтового сервера')
    mailing = models.ForeignKey('Mailing', on_delete=models.CASCADE, related_name='attempts', verbose_name='Рассылка')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              verbose_name='Владелец')
    def __str__(self):
        return f'Попытка {self.status} для {self.mailing} в {self.attempt_time}'

    class Meta:
        verbose_name = 'Попытка отправки'
        verbose_name_plural = 'Попытки отправок'
