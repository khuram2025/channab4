from django import template

register = template.Library()

@register.filter
def bg_color(value):
    value = float(value)
    return 'custome-1-bg' if value >= 0 else 'custome-3-bg'

