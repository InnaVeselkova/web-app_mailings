from django.core.mail import send_mail
from django.utils import timezone

from .models import Attempt

import pytz

def initiate_sending_mailing(mailing, user):
    moscow_tz = pytz.timezone('Europe/Moscow')
    now_moscow = timezone.now().astimezone(moscow_tz)

    print("Текущее московское время:", now_moscow)
    print("Диапазон рассылки:", mailing.start_time, "-", mailing.end_time)

    # Конвертируем start_time и end_time в московский часовой пояс
    start_time_moscow = mailing.start_time.astimezone(moscow_tz) if mailing.start_time else None
    end_time_moscow = mailing.end_time.astimezone(moscow_tz) if mailing.end_time else None

    if start_time_moscow and end_time_moscow and start_time_moscow <= now_moscow <= end_time_moscow:
        for recipient in mailing.recipients.all():
            subject = mailing.message.subject
            body = mailing.message.body

            try:
                send_mail(
                    subject,
                    body,
                    user.email,
                    [recipient.email],
                    fail_silently=False,
                )
                Attempt.objects.create(
                    attempt_time=timezone.now(),
                    status='Успешно',
                    server_response='Email отправлен успешно.',
                    mailing=mailing,
                    owner=user
                )
            except Exception as e:
                Attempt.objects.create(
                    attempt_time=timezone.now(),
                    status='Не успешно',
                    server_response=str(e),
                    mailing=mailing,
                    owner=user
                )
        return True
    else:
        return False