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

    def __init__(self, *args, locked: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        if locked:
            del self.fields["email"]
            for name in self.fields:
                self.fields[name].required = False
                self.fields[name].widget.attrs["autofocus"] = False
                self.fields[name].widget.attrs["readonly"] = True
        else:
            self.fields["birth_date"].required = True
            self.fields["zip_code"].required = True

    def clean_zip_code(self):
        value = self.cleaned_data["zip_code"].strip()
        if len(value) != 5 or not value.isnumeric():
            raise forms.ValidationError("This value must be exactly five digits.")
        return value


class FriendsForm(forms.Form):
    emails = MultiEmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["emails"].widget.attrs["rows"] = "4"
