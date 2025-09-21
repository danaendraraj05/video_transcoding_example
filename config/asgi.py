"""
ASGI config for transcode_video_example project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.local")


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

django_app = get_asgi_application()
from django.conf import settings
from app.api.main import app as fastapi_app

main_app = FastAPI()
main_app.mount(
    "/static",
    StaticFiles(directory=settings.BASE_DIR / "staticfiles"),
    name="static",
)
main_app.mount("/api", fastapi_app)
main_app.mount("/", django_app)

application = main_app

