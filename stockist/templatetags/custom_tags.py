# myapp/templatetags/custom_tags.py
from django import template

register = template.Library()

@register.simple_tag
def set(var_name, value):
    return f"{var_name} = {value}"
