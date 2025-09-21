from django.db import models
import os

class TranscodedVideo(models.Model):
    original_video = models.FileField(upload_to='uploads/')
    codec = models.CharField(
        max_length=10,
        choices=[('h264','H.264'),('h265','H.265'),('av1','AV1'),('vp9','VP9')]
    )
    profile = models.CharField(
        max_length=10,
        choices=[('baseline','Baseline'),('main','Main'),('high','High')]
    )
    resolutions = models.JSONField()  # e.g., ["240p","480p","720p"]
    output_folder = models.CharField(max_length=255)
    transcoding_time = models.FloatField(null=True, blank=True)  # seconds
    bandwidth = models.FloatField(null=True, blank=True)  # MB/s
    storage_used = models.FloatField(null=True, blank=True)  # total MB
    size_per_resolution = models.JSONField(null=True, blank=True)  # e.g., {"240p": 5.3, "360p": 8.1}
    source_size = models.FloatField(null=True, blank=True)  # MB
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically calculate source size in MB
        if self.original_video and not self.source_size:
            try:
                self.source_size = os.path.getsize(self.original_video.path) / (1024*1024)
            except FileNotFoundError:
                self.source_size = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.original_video.name} ({self.codec})"
