from django.forms.widgets import TextInput


class DateInput(TextInput):
    input_type = "date"
