from django import template
from datetime import date

register = template.Library()

@register.filter
def age_display(dob):
    today = date.today()
    years = today.year - dob.year
    months = today.month - dob.month
    days = today.day - dob.day

    if days < 0:
        months -= 1
        days += 30  # assuming 30 days per month

    if months < 0:
        years -= 1
        months += 12

    return f"{years} year{'s' if years != 1 else ''} {months} month{'s' if months != 1 else ''} {days} day{'s' if days != 1 else ''}"
