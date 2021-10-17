from django import forms

from multi_email_field.forms import MultiEmailField

from .models import User, Voter


class LoginForm(forms.ModelForm):
    email = forms.EmailField(
        required=True, widget=forms.TextInput(attrs={"autofocus": True})
    )

    class Meta:
        model = User
        fields = ["email"]


class VoterForm(forms.ModelForm):
    email = forms.EmailField(disabled=True, required=False)
    first_name = forms.CharField(widget=forms.TextInput(attrs={"autofocus": True}))
    last_name = forms.CharField()

    class Meta:
        model = Voter
        fields = ["email", "first_name", "last_name", "birth_date", "zip_code"]

    def clean_zip_code(self):
        value = self.cleaned_data["zip_code"].strip()
        if len(value) != 5 or not value.isnumeric():
            raise forms.ValidationError("This value must be exactly five digits.")
        return value


class FriendsForm(forms.Form):
    emails = MultiEmailField()
