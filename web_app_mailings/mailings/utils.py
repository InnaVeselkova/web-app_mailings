import logging
from django.core.mail import send_mail, EmailMessage
from django.utils import timezone
from django.conf import settings
from .models import Attempt
import pytz

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def initiate_sending_mailing(mailing, user):
    moscow_tz = pytz.timezone("Europe/Moscow")
    now_moscow = timezone.now().astimezone(moscow_tz)

    logger.info(f"Московское время: {now_moscow}")
    logger.info(f"Диапазон рассылки: {mailing.start_time} - {mailing.end_time}")

    start_time_moscow = mailing.start_time.astimezone(moscow_tz) if mailing.start_time else None
    end_time_moscow = mailing.end_time.astimezone(moscow_tz) if mailing.end_time else None

    if start_time_moscow and end_time_moscow and start_time_moscow <= now_moscow <= end_time_moscow:
        for recipient in mailing.recipients.all():
            recipient_email = recipient.email
            logger.info(f"Отправка рассылки на адрес: {recipient_email}")

            try:
                email = EmailMessage(
                    mailing.message.subject,
                    mailing.message.body,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient_email],
                    headers={"Reply-To": user.email},
                )
                email.send(fail_silently=False)
                logger.info(f"Email успешно отправлен на {recipient_email}")

                Attempt.objects.create(
                    attempt_time=timezone.now(),
                    status="Успешно",
                    server_response="Email отправлен успешно.",
                    mailing=mailing,
                    owner=user,
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке email на {recipient_email}: {str(e)}")
                Attempt.objects.create(
                    attempt_time=timezone.now(),
                    status="Не успешно",
                    server_response=str(e),
                    mailing=mailing,
                    owner=user,
                )
        return True
    else:
        logger.info("Текущее время вне диапазона рассылки.")
        return False
