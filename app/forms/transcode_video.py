from django import forms
from app.models.transcode import TranscodedVideo

RESOLUTION_CHOICES = [
    ('240p', '240p'), ('360p', '360p'), ('480p', '480p'),
    ('720p', '720p'), ('1080p', '1080p')
]

class TranscodeForm(forms.ModelForm):
    resolutions = forms.MultipleChoiceField(
        choices=RESOLUTION_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = TranscodedVideo
        fields = ['original_video', 'codec', 'profile', 'resolutions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile'].required = False
