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
def abbreviate(value: float):
    try:
        value = float(value)
        if value >= 1000:
            value = round(value / 1000, 1)
            return f"{value}k"
        else:
            return value
    except (ValueError, TypeError):
        return value
