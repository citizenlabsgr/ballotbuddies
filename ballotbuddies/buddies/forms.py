from django import forms

from .models import User, Voter


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]


class VoterForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta:
        model = Voter
        fields = ["first_name", "last_name", "birth_date", "zip_code"]
