import yt_dlp
import os

def download_youtube_playlist_mp3(playlist_url, output_folder="DHH_for_Cute_gurls"):
    """
    Downloads all videos from a given YouTube playlist as highest quality MP3s.

    Args:
        playlist_url (str): The URL of the YouTube playlist.
        output_folder (str): The name of the folder where the MP3s will be saved.
                             This folder will be created in the current working directory.
    """

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output directory: {output_folder}")
    else:
        print(f"Using existing output directory: {output_folder}")

    # yt-dlp options for downloading audio
    ydl_opts = {
        'format': 'bestaudio/best',  # Select the best audio format
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Use FFmpeg to extract audio
            'preferredcodec': 'mp3',      # Convert to MP3
            'preferredquality': '0',      # Highest quality for MP3
        }],
        'extract_flat': 'auto',  # Automatically handle playlist extraction
        'yes_playlist': True,    # Explicitly tell yt-dlp it's a playlist
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'), # Output template
                                                                     # %(title)s for video title
                                                                     # %(ext)s for file extension (mp3)
        'ignoreerrors': True,    # Continue if some videos in the playlist cause errors
        'restrictfilenames': True, # Keep filenames simple (no special characters)
        'noplaylist': False,     # Process as a playlist
        'progress_hooks': [lambda d: print(f"Status: {d['status']} - {d.get('_percent_str', '')} {d.get('_eta_str', '')}")], # Show progress
        'verbose': False,        # Set to True for more detailed debug output
    }

    try:
        print(f"\nStarting download for playlist: {playlist_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
        print(f"\nDownload complete! MP3s saved to: {os.path.abspath(output_folder)}")
    except Exception as e:
        print(f"\nAn error occurred during download: {e}")
        print("Please ensure FFmpeg is installed and accessible in your system's PATH.")
        print("You can download FFmpeg from: https://ffmpeg.org/download.html")

if __name__ == "__main__":
    playlist_link = "https://youtube.com/playlist?list=PLVbLhzs-GWDklTDNi_k_cXO_dawcefU2x&si=0NNRSuodxMf-cozi"
    download_youtube_playlist_mp3(playlist_link)
