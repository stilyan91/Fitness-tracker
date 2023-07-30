from django import template


register = template.Library()

@register.filter(name="placeholder")
def placeholder(value,token):
    value.widget.attrs['placeholder'] = token
    return value