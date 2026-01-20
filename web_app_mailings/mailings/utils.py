from django.core.mail import send_mail
from django.utils import timezone

from .models import Attempt

def initiate_sending_mailing(mailing, user):
    # Проверяем, входит ли текущее время в разрешенный диапазон
    if mailing.start_time <= timezone.now() <= mailing.end_time:
        # Проходим по всем получателям
        for recipient in mailing.recipients.all():
            subject = mailing.message.subject  # Тема письма
            body = mailing.message.body  # Тело письма

            try:
                # Отправляем письмо
                send_mail(
                    subject,
                    body,
                    'from@example.com',  # Ваш email адрес для отправки
                    [recipient.email],
                    fail_silently=False,
                )
                # Создаем запись об успешной попытке отправки
                Attempt.objects.create(
                    attempt_time=timezone.now(),
                    status='Успешно',
                    server_response='Email отправлен успешно.',
                    mailing=mailing,
                    owner=user  # Устанавливаем владельца
                )
            except Exception as e:
                # Создаем запись о неуспешной попытке отправки
                Attempt.objects.create(
                    attempt_time=timezone.now(),
                    status='Не успешно',
                    server_response=str(e),
                    mailing=mailing,
                    owner=user  # Устанавливаем владельца
                )
        return True  # Успешно завершено
    else:
        return False  # Текущая дата вне диапазона
