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
        value = int(value)
        if value >= 1000:
            return f"{round(value / 1000, 1)}k"
        return value
    except (ValueError, TypeError):
        return value
