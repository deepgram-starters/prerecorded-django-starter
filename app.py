import os
import sys
import json

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import path
from django.utils.crypto import get_random_string
from django.shortcuts import render
from whitenoise import WhiteNoise

settings.configure(
    ALLOWED_HOSTS=["localhost"],
    DEBUG=(os.environ.get("DEBUG", "") == "1"),
    ROOT_URLCONF=__name__,
    SECRET_KEY=get_random_string(40),
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["static"],
        },
    ],
    MIDDLEWARE=[
        "whitenoise.middleware.WhiteNoiseMiddleware",
    ],
    STATIC_URL="/",
    STATIC_ROOT="static/",
    STATICFILES_STORAGE="whitenoise.storage.CompressedManifestStaticFilesStorage",
)


def index(request):
    return render(request, "index.html")


async def transcribe(request):
    if request.method == "POST":
        return JsonResponse({"data": "test2"})
    else:
        return HttpResponseBadRequest("Invalid HTTP method")


def json_abort(message):
    return HttpResponseBadRequest(json.dumps({"err": str(message)}))


urlpatterns = [
    path("api", transcribe, name="transcribe"),
]

app = get_wsgi_application()
app = WhiteNoise(app, root="static/", prefix="/")

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
