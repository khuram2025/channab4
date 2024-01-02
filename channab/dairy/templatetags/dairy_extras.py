from django import template
from datetime import date
from dairy.models import Animal
from dateutil.relativedelta import relativedelta


register = template.Library()

@register.filter
def animal_age(dob):
    today = date.today()
    
    # Calculate the difference in years
    years = today.year - dob.year
    
    # Calculate the difference in months
    months = today.month - dob.month
    
    # Calculate the difference in days
    days = today.day - dob.day
    
    # Adjust if today's day is less than the birth day
    if days < 0:
        months -= 1
        if today.month == 1:
            last_month = today.replace(year=today.year - 1, month=12, day=1)
        else:
            last_month = today.replace(month=today.month - 1, day=1)
        days += (last_month + relativedelta(months=+1, days=-1)).day

    
    # Adjust if this month's difference is negative
    if months < 0:
        years -= 1
        months += 12
    
    # Build the age string
    age_parts = []
    if years > 0:
        age_parts.append(f"{years}Y")
    if months > 0:
        age_parts.append(f"{months}M")
    if days > 0:
        age_parts.append(f"{days}D")
    
    return ' '.join(age_parts)

    
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

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_animal_type_display(animal_type):
    return Animal.ANIMAL_TYPE_CHOICES_DICT.get(animal_type)

@register.filter
def positive_or_negative(value):
    if value > 0:
        return "text-success"
    elif value < 0:
        return "text-danger"
    return ""
@register.filter(name='truncatechars_ellipsis')
def truncatechars_ellipsis(value, arg):
    if value is None:
        return ""  # Return an empty string if the value is None

    if len(value) > arg:
        return value[:arg] + '...'
    return value
