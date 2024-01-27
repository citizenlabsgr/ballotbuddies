from django import template

register = template.Library()


@register.filter
def replace(value, arg):
    """Custom template filter to replace string."""
    search, replace_with = arg.split(",")
    return value.replace(search, replace_with)
