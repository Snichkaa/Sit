from jinja2 import Environment
from django.urls import reverse
from django.utils.html import format_html
from django.middleware.csrf import get_token

def csrf_input(request):
    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request)
    )

def environment(**options):
    env = Environment(**options)
    env.globals.update({
        "url": reverse,
        "csrf_input": csrf_input,
    })
    return env
