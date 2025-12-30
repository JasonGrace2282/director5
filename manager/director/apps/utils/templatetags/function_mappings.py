from django import template
from django.templatetags.static import static as django_static

register = template.Library()

"""
These 1:1 function mappings will help you get around django-cotton's limitations;
i.e. you can't use {% static %} within a component,
but you can use {{ }} notation, i.e. {{ "favicon/mascot/mocha-bear-reading.png"|static }}
"""

@register.filter
def static(path):
    return django_static(path)
