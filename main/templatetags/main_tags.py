from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    param = context['request'].GET.copy()
    for key, value in kwargs.items():
        param[key] = value
    for key in [key for key, value in param.items() if not value]:
        del param[key]
    return param.urlencode()
    