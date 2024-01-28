import re

from django import template

register = template.Library()


@register.filter
def replace(text, parameter):
    """Custom template filter to replace words."""
    word, replacement = parameter.split(",")
    pattern = rf"\b{word}\b"
    return re.sub(pattern, replacement, text)
