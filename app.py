import os
import sys
import json

from deepgram import Deepgram
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import path
from django.utils.crypto import get_random_string
from dotenv import load_dotenv
from whitenoise import WhiteNoise

load_dotenv()

settings.configure(
    ALLOWED_HOSTS=["localhost"],
    DEBUG=(os.environ.get("DEBUG", "") == "1"),
    ROOT_URLCONF=__name__,
    SECRET_KEY=get_random_string(40),
    MIDDLEWARE=[
        "whitenoise.middleware.WhiteNoiseMiddleware",
    ],
    STATIC_URL="/",
    STATIC_ROOT="static/",
    STATICFILES_STORAGE="whitenoise.storage.CompressedManifestStaticFilesStorage",
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["static"],
        },
    ],
)

deepgram = Deepgram(os.environ.get("DEEPGRAM_API_KEY"))


async def transcribe(request):
    if request.method == "POST":
        form = request.POST
        files = request.FILES

        url = form.get("url")
        features = form.get("features")
        model = form.get("model")
        version = form.get("version")
        tier = form.get("tier")

        dgFeatures = json.loads(features)
        dgRequest = None

        try:
            if url and url.startswith("https://res.cloudinary.com/deepgram"):
                dgRequest = {"url": url}

            if "file" in files:
                file = files["file"]
                dgRequest = {"mimetype": file.content_type, "buffer": file.read()}

            dgFeatures["model"] = model

            if version:
                dgFeatures["version"] = version

            if model == "whisper":
                dgFeatures["tier"] = tier

            if not dgRequest:
                raise Exception(
                    "Error: You need to choose a file to transcribe your own audio."
                )

            transcription = await deepgram.transcription.prerecorded(
                dgRequest, dgFeatures
            )

            return JsonResponse(
                {
                    "model": model,
                    "version": version,
                    "tier": tier,
                    "dgFeatures": dgFeatures,
                    "transcription": transcription,
                }
            )
        except Exception as error:
            return json_abort(str(error))
    else:
        return HttpResponseBadRequest("Invalid HTTP method")


def json_abort(message):
    return HttpResponseBadRequest(json.dumps({"err": str(message)}))


def index(request):
    return render(request, "index.html")


urlpatterns = [
    path("", index),
    path("api", transcribe, name="transcribe"),
]

app = get_wsgi_application()
app = WhiteNoise(app, root="static/", prefix="/")

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
