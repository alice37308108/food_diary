from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def add(value, arg):
    """加算フィルター"""
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        try:
            return float(value) + float(arg)
        except (ValueError, TypeError):
            return value

@register.filter
def subtract(value, arg):
    """減算フィルター"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        try:
            return float(value) - float(arg)
        except (ValueError, TypeError):
            return value