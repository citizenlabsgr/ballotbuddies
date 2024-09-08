from django.conf import settings
from django.shortcuts import redirect

import log
from allauth.account.utils import perform_login
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import User


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return None

        email = sociallogin.user.email.lower()

        if email and User.objects.filter(email=email).exists():
            log.info(f"Found existing social account: {email}")
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)
            perform_login(request, user, email_verification="none")
            return redirect(settings.LOGIN_REDIRECT_URL)

        log.info(f"Authenticating new social account: {email}")
        return super().pre_social_login(request, sociallogin)
