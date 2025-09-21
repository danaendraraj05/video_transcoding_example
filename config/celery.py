import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.base")
app = Celery("transcode_video_example")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["app.tasks"])
