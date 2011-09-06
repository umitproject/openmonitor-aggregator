from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag
def addthis_bubble_small(request, url="", title="", description=""):
    return render_to_string("gui/social/addthis_bubble_small.html", locals())
addthis_bubble_small.is_safe = True

@register.simple_tag
def addthis_small(request, url="", title="", description=""):
    return render_to_string("gui/social/addthis_small.html", locals())
addthis_small.is_safe = True

@register.simple_tag
def addthis_large(request, url="", title="", description=""):
    return render_to_string("gui/social/addthis_large.html", locals())
addthis_large.is_safe = True