from django import template
from django.templatetags.static import static

register = template.Library()

@register.filter
def get_static(path):
    return static(path)
