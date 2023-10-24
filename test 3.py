import pytube.exceptions as exceptions

try:
    raise exceptions.VideoPrivate(video_id='')
except Exception as e:
    print(type(e).__name__)
