import re

from django import template

register = template.Library()


@register.filter
def replace(value: str, parameter: str):
    """Custom template filter to replace words."""
    word, replacement = parameter.split(",")
    pattern = rf"\b{word}\b"
    return re.sub(pattern, replacement, value)


@register.filter
def abbreviate(value: str):
    try:
        count = float(value)
        if count >= 1000:
            count = round(count / 1000, 1)
            return f"{count}k"
        return value
    except (ValueError, TypeError):
        return value
