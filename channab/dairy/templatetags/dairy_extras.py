from django import template
from datetime import date

register = template.Library()

@register.filter
def animal_age(dob):
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    months = (today.month - dob.month - (today.day < dob.day)) % 12
    days = (today - dob.replace(year=today.year)).days

    if age > 0:
        return f"{age} Year{'s' if age > 1 else ''} {months} Month{'s' if months > 1 else ''} {days} Day{'s' if days > 1 else ''}"
    elif months > 0:
        return f"{months} Month{'s' if months > 1 else ''} {days} Day{'s' if days > 1 else ''}"
    else:
        return f"{days} Day{'s' if days > 1 else ''}"
    
@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def div(value, arg):
    return value / arg if arg != 0 else 0

@register.filter
def mul(value, arg):
    return value * arg
