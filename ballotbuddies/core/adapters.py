from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect

import log
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import User


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email.lower()

        if existing_user := User.objects.filter(email=email).first():
            log.info(f"Logging in existing social user: {email}")
            login(request, existing_user, backend=settings.AUTHENTICATION_BACKENDS[0])
            return redirect(settings.LOGIN_REDIRECT_URL)

        log.info(f"Creating new social user: {email}")
        return super().pre_social_login(request, sociallogin)
