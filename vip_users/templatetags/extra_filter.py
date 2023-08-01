from django.template.defaulttags import register


@register.filter
def int1(x):
    return int(x)
