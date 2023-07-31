from django import template

register = template.Library()

@register.filter(name='addstr')
def addstr(value, data):
    return str(value)+str(data)