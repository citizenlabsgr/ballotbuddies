from django import forms

from ballotbuddies.buddies.forms import VoterForm

from .models import User


class SignupForm(VoterForm):
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"autofocus": True})
    )
    nickname = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields["email"].widget.attrs["data-lpignore"]


class LoginForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        label="",
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "autofocus": True,
                "placeholder": "Email address",
                "data-lpignore": "true",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["email"]

    def clean_email(self):
        value = self.cleaned_data["email"]
        return value.lower()
