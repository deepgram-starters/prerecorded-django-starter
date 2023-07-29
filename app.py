import os
import sys

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse
from django.urls import path, re_path
from django.utils.crypto import get_random_string
from django.conf.urls.static import static
from django.shortcuts import render

settings.configure(
    MEDIA_URL="/",
    MEDIA_ROOT="static/",
    DEBUG=(os.environ.get("DEBUG", "") == "1"),
    ROOT_URLCONF=__name__,
    SECRET_KEY=get_random_string(40),
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["static"],
        },
    ],
)


def index(request):
    return render(request, "index.html")


def transcribe(request):
    return JsonResponse({"data": "test2"})


urlpatterns = [path("", index), re_path(r"^api/?$", transcribe)] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

app = get_wsgi_application()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
