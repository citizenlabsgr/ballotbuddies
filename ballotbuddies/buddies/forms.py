from django import forms
from django.core import validators
from django.core.validators import validate_email

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
    first_name = forms.CharField(
        label="Legal first name", widget=forms.TextInput(attrs={"autofocus": True})
    )
    last_name = forms.CharField()

    class Meta:
        model = Voter
        fields = ["email", "first_name", "last_name", "birth_date", "zip_code"]

    def __init__(self, *args, locked: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["birth_date"].required = True
        self.fields["birth_date"].widget.attrs["placeholder"] = "YYYY-MM-DD"
        self.fields["zip_code"].required = True
        self.fields["zip_code"].widget.attrs["placeholder"] = "#####"
        if locked:
            del self.fields["email"]
            for name in self.fields:
                self.fields[name].required = False
                self.fields[name].widget.attrs["autofocus"] = False
                self.fields[name].widget.attrs["readonly"] = True

    def clean_zip_code(self):
        value = self.cleaned_data["zip_code"].strip()
        if len(value) != 5 or not value.isnumeric():
            raise forms.ValidationError("This value must be exactly five digits.")
        return value


class MultiEmailWidget(forms.widgets.Textarea):

    EMPTY_VALUES = validators.EMPTY_VALUES + ("[]",)

    is_hidden = False

    def _prepare(self, value) -> str:
        if value in self.EMPTY_VALUES:
            return ""
        elif isinstance(value, str):
            return value
        elif isinstance(value, list):
            return "\n".join(value)
        raise forms.ValidationError("Invalid format.")

    def render(self, name, value, **kwargs):
        value = self._prepare(value)
        return super().render(name, value, **kwargs)


class MultiEmailField(forms.Field):

    widget = MultiEmailWidget

    def to_python(self, value):
        if not value:
            return []
        return [v.strip() for v in value.splitlines() if v != ""]

    def validate(self, value):
        super().validate(value)
        for email in value:
            validate_email(email)


class FriendsForm(forms.Form):
    emails = MultiEmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["emails"].widget.attrs["rows"] = "4"
