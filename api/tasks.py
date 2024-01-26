from celery import shared_task
from django.contrib.auth import get_user_model
from common.users.models import Code

User = get_user_model()


@shared_task(name='send_sms')
def send_sms(id, phone):
    pass


@shared_task(name='verified_user')
def verified_user(guid):
    user = User.objects.get(guid=guid)
    user.is_verified = True
    user.save()
