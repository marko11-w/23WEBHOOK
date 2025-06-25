from moviepy.editor import VideoFileClip, AudioFileClip
import requests

def download_file(url, filename):
    r = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(r.content)

def generate_ai_video():
    video_url = "https://player.vimeo.com/external/449451633.sd.mp4?s=4cf646917b5f4e616df9e273ba8d5ed4b9f6cc33&profile_id=165&oauth2_token_id=57447761"
    audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

    download_file(video_url, "video.mp4")
    download_file(audio_url, "audio.mp3")

    clip = VideoFileClip("video.mp4").subclip(0, 30)
    audio = AudioFileClip("audio.mp3").subclip(0, 30)
    final = clip.set_audio(audio)
    final.write_videofile("final_video.mp4", codec='libx264', audio_codec='aac')

    return "final_video.mp4"