from django import forms

from multi_email_field.forms import MultiEmailField

from .models import User, Voter
from .widgets import DateInput


class LoginForm(forms.ModelForm):
    email = forms.EmailField(
        required=True, widget=forms.TextInput(attrs={"autofocus": True})
    )

    class Meta:
        model = User
        fields = ["email"]

    def clean_email(self):
        value = self.cleaned_data["email"]
        return value.lower()


class VoterForm(forms.ModelForm):
    email = forms.EmailField(disabled=True, required=False)
    first_name = forms.CharField(
        label="Legal first name", widget=forms.TextInput(attrs={"autofocus": True})
    )
    last_name = forms.CharField()
    birth_date = forms.CharField(widget=DateInput)

    class Meta:
        model = Voter
        fields = [
            "email",
            "nickname",
            "first_name",
            "last_name",
            "birth_date",
            "zip_code",
        ]

    def __init__(self, *args, locked: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nickname"].widget.attrs["placeholder"] = "Preferred first name"
        self.fields["birth_date"].required = True
        self.fields["birth_date"].widget.attrs["placeholder"] = "mm/dd/yyyy"
        self.fields["birth_date"].widget.attrs["data-date-format"] = "mm/dd/yyyy"
        self.fields["zip_code"].required = True
        self.fields["first_name"].widget.attrs["data-lpignore"] = True
        if locked:
            del self.fields["email"]
            if not kwargs["initial"].get("nickname"):
                del self.fields["nickname"]
            for name in self.fields:
                self.fields[name].required = False
                self.fields[name].widget.attrs["autofocus"] = False
                self.fields[name].widget.attrs["readonly"] = True

    def clean_zip_code(self):
        value = self.cleaned_data["zip_code"].strip()
        if len(value) != 5 or not value.isnumeric():
            raise forms.ValidationError("This value must be exactly five digits.")
        return value


class FriendsForm(forms.Form):
    emails = MultiEmailField()

    def __init__(self, *args, required=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["emails"].widget.attrs["rows"] = "4"
        self.fields["emails"].required = required

    def clean_emails(self):
        values = self.cleaned_data["emails"]
        return [value.lower() for value in values]
