from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import User


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return None

        if existing_user := User.objects.filter(email=sociallogin.user.email).first():
            login(request, existing_user, backend=settings.AUTHENTICATION_BACKENDS[0])
            return redirect(request.GET.get("next") or "core:index")

        return super().pre_social_login(request, sociallogin)
