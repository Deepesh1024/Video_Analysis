import yt_dlp
def download_youtube_video(url, save_path="static/uploads/video.mp4"):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', 
        'outtmpl': save_path,  
        'merge_output_format': 'mp4'  
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
# video_url = "https://youtu.be/3MJh2Dm9IgQ?si=SW5ZpSPcMC9jCK6O"
# download_youtube_video(video_url)