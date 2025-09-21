import os, time, subprocess
from django.conf import settings
from django.shortcuts import render, redirect
from app.forms.transcode_video import TranscodeForm
from app.models.transcode import TranscodedVideo

def transcode_video(request):
    if request.method == 'POST':
        form = TranscodeForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            input_path = video.original_video.path

            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Uploaded file not found: {input_path}")

            # Create main output folder
            video.output_folder = os.path.join(settings.MEDIA_ROOT, 'videos', str(int(time.time())))
            os.makedirs(video.output_folder, exist_ok=True)

            start = time.time()
            codec = video.codec
            profile = video.profile
            resolutions = form.cleaned_data['resolutions']
            size_per_resolution = {}
            playlist_paths = []

            # Base name from input file (remove extension)
            base_name = os.path.splitext(os.path.basename(input_path))[0]

            for res in resolutions:
                height = res.replace('p', '')
                res_folder = os.path.join(video.output_folder, res)
                os.makedirs(res_folder, exist_ok=True)
                output_m3u8 = os.path.join(res_folder, f"{res}.m3u8")

                command = [
                    'ffmpeg', '-i', input_path,
                    '-vf', f'scale=-2:{height}',
                    '-start_number', '0',
                    '-hls_time', '10',
                    '-hls_list_size', '0',
                    '-f', 'hls',
                    output_m3u8,
                    '-c:v', codec
                ]

                if codec in ['h264', 'hevc', 'h265']:
                    command += ['-profile:v', profile]
                elif codec == 'vp9':
                    command += ['-b:v', '2M', '-crf', '30']
                elif codec == 'av1':
                    command += ['-b:v', '2M', '-cpu-used', '4']

                subprocess.run(command, check=True)

                folder_size = sum(
                    os.path.getsize(os.path.join(res_folder, f)) for f in os.listdir(res_folder)
                ) / (1024*1024)
                size_per_resolution[res] = round(folder_size, 2)
                playlist_paths.append((res, output_m3u8))

            # Transcoding time
            end = time.time()
            video.transcoding_time = end - start

            # Create master playlist with dynamic name
            master_playlist_path = os.path.join(video.output_folder, f"{base_name}.m3u8")
            with open(master_playlist_path, 'w') as master:
                master.write("#EXTM3U\n#EXT-X-VERSION:3\n")
                for res, playlist in playlist_paths:
                    bandwidth = int(size_per_resolution[res] * 1024 * 1024 / video.transcoding_time)
                    master.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={res}\n")
                    master.write(f"{res}/{res}.m3u8\n")

            # Bandwidth MB/s
            video.bandwidth = os.stat(input_path).st_size / video.transcoding_time / (1024*1024)

            # Total storage used and per-resolution sizes
            video.storage_used = sum(size_per_resolution.values())
            video.size_per_resolution = size_per_resolution

            video.save()
            return redirect('transcoded_video_list')
    else:
        form = TranscodeForm()

    return render(request, 'transcode_form.html', {'form': form})


def transcoded_video_list(request):
    # Fetch all transcoded videos ordered by newest first
    videos = TranscodedVideo.objects.all().order_by('-created_at')
    return render(request, 'transcoded_video_list.html', {'videos': videos})