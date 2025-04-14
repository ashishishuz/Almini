from django import template

register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def sub(value, arg):
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0