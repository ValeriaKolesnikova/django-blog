from typing import TYPE_CHECKING, NamedTuple
from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_encode
from django.template import loader
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


from api.email_services import BaseEmailHandler

from main.decorators import except_shell

if TYPE_CHECKING:
    from main.models import UserType


User: 'UserType' = get_user_model()


class CreateUserData(NamedTuple):
    first_name: str
    last_name: str
    email: str
    password_1: str
    password_2: str


class ConfirmationEmailHandler(BaseEmailHandler):
    FRONTEND_URL = settings.FRONTEND_URL
    FRONTEND_PATH = '/confirm'
    TEMPLATE_NAME = 'emails/verify_email.html'

    def _get_activate_url(self) -> str:
        url = urljoin(self.FRONTEND_URL, self.FRONTEND_PATH)
        query_params: str = urlencode(
            {
                'key': self.user.confirmation_key,
            },
            safe=':+',
        )
        return f'{url}?{query_params}'

    def email_kwargs(self, **kwargs) -> dict:
        return {
            'subject': _('Register confirmation email'),
            'to_email': self.user.email,
            'context': {
                'user': self.user.full_name,
                'activate_url': self._get_activate_url(),
            },
        }


class AuthAppService:
    @staticmethod
    def is_user_exist(email: str) -> bool:
        return User.objects.filter(email=email).exists()

    @staticmethod
    @except_shell((User.DoesNotExist,))
    def get_user(email: str) -> User:
        return User.objects.get(email=email)

    @transaction.atomic()
    def create_user(self, validated_data: dict):
        data = CreateUserData(**validated_data)
        user = User.objects.create_user(
            email=data.email,
            password=data.password_1,
            first_name=data.first_name,
            last_name=data.last_name,
            is_active=False
        )
        context = {
            'full_name': user.full_name,
            'activate_url': f'http://localhost:8008/confirm?key={user.confirmation_key}'
        }
        html_template = loader.render_to_string('emails/registration_email.html', context=context)
        send_mail(
            subject='Регистрация',
            message='Вы успешно зарегистрировались.',
            from_email='testtest-2023@internet.ru',
            recipient_list=[data.email],
            html_message=html_template,
            fail_silently=False,
        )
        print(f'{data=}')
        return user
    
    def send_password_reset_email(self, email: str):
        print(f'{email=}')
        user = User.objects.filter(email=email).first()
        if not user:
            raise NotFound('This email not found.')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        context = {
            'reset_url': f'http://localhost:8008/reset-password?uid={uid}&token={token}'
        }
        html_template = loader.render_to_string('emails/reset_email.html', context=context)
        send_mail(
            subject='Сброс пароля.',
            message=strip_tags(html_template),
            from_email='testtest-2023@internet.ru',
            recipient_list=[email],
            html_message=html_template,
        )


def full_logout(request):
    response = Response({"detail": _("Successfully logged out.")}, status=status.HTTP_200_OK)
    auth_cookie_name = settings.REST_AUTH['JWT_AUTH_COOKIE']
    refresh_cookie_name = settings.REST_AUTH['JWT_AUTH_REFRESH_COOKIE']

    response.delete_cookie(auth_cookie_name)
    refresh_token = request.COOKIES.get(refresh_cookie_name)
    if refresh_cookie_name:
        response.delete_cookie(refresh_cookie_name)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except KeyError:
        response.data = {"detail": _("Refresh token was not included in request data.")}
        response.status_code = status.HTTP_401_UNAUTHORIZED
    except (TokenError, AttributeError, TypeError) as error:
        if hasattr(error, 'args'):
            if 'Token is blacklisted' in error.args or 'Token is invalid or expired' in error.args:
                response.data = {"detail": _(error.args[0])}
                response.status_code = status.HTTP_401_UNAUTHORIZED
            else:
                response.data = {"detail": _("An error has occurred.")}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        else:
            response.data = {"detail": _("An error has occurred.")}
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    else:
        message = _(
            "Neither cookies or blacklist are enabled, so the token "
            "has not been deleted server side. Please make sure the token is deleted client side."
        )
        response.data = {"detail": message}
        response.status_code = status.HTTP_200_OK
    return response
