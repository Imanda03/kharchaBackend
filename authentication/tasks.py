from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from celery import shared_task
from .utils import RandomStringTokenGenerator
from django.template.loader import render_to_string

def send_register_mail(instance, domain, assets_image_path, UserTokenSerializer, template):
    from .models import UserToken
    rand = RandomStringTokenGenerator()
    token = rand.generate_unique_token(model=UserToken, field="key")
    first_name = instance.first_name if (len(instance.first_name) >= 1) else "User"
    message = render_to_string(template, 
    {'username': first_name, 'domain': domain, 'token': token, 'identifier': instance.id, 'url': assets_image_path})
    mail = instance.send_mail(subject=f"Welcome to {settings.PROJECT_NAME} - Registration Confirmation", message=message)
    if(mail == "success"):
        data = {"user" : instance.id, "key" : token, "key_type" : 0}
        tokenSerializer = UserTokenSerializer(data=data)
        if(tokenSerializer.is_valid(raise_exception=True)):
            UserToken.objects.create(**tokenSerializer.validated_data)
    else:
        raise Exception

@shared_task
def send_mail_asynchron(**kwargs):
    try:
        subject = kwargs.get("subject")
        from_email = kwargs.get("from_email", settings.DEFAULT_FROM_EMAIL)
        to = kwargs.get('to_email')
        message = kwargs.get("message")
        msg = "Registration email"
        toSend = EmailMultiAlternatives(subject, msg, from_email, to)
        toSend.attach_alternative(message, "text/html")
        toSend.send()
        return "success"
    except Exception:
        return "failure"

@shared_task
def send_extended_mail_asynchron(**kwargs):
    try:
        subject = kwargs.get("subject")
        from_email = kwargs.get("from_email", settings.DEFAULT_FROM_EMAIL)
        to = kwargs.get("to_email")
        message = kwargs.get("message")
        msg = "Email"
        toSend = EmailMultiAlternatives(subject, msg, from_email, [to, ])
        toSend.attach_alternative(message, "text/html")
        if "attachment" in kwargs:
            filename = kwargs.get("attachment")
            toSend.attach(filename['name'], filename['file'], filename['type'])
        toSend.send()
        return "success"
    except Exception:
        return "failure"
