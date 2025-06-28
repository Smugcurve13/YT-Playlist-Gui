import streamlit as st
import yt_dlp
import os
import zipfile
import base64
from datetime import datetime

def create_zip_file(folder_path, zip_name):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.mp3'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
    return zip_name

def get_binary_file_downloader_html(zip_path, file_label='File'):
    with open(zip_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/zip;base64,{b64}" download="{os.path.basename(zip_path)}">Download {file_label}</a>'
    return href

def download_youtube_playlist_mp3(playlist_url, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }],
        'extract_flat': 'auto',
        'yes_playlist': True,
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'ignoreerrors': True,
        'restrictfilenames': True,
        'noplaylist': False,
        'verbose': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
        return True
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return False

# Streamlit UI
st.title("YouTube Playlist to MP3 Downloader")
st.write("Enter a YouTube playlist URL to download all videos as MP3s and get them in a ZIP file!")

# Input field for playlist URL
playlist_url = st.text_input("Enter YouTube Playlist URL")

# Input field for output folder (subfolder inside Downloads)
default_subfolder = ""
subfolder = st.text_input("Enter subfolder name inside Downloads to save MP3s", value=default_subfolder)

# Construct the full output folder path
output_folder = os.path.join("Downloads", subfolder)

if st.button("Download and Convert"):
    if playlist_url:
        with st.spinner("Downloading and converting videos to MP3... This may take a while."):
            # Extract playlist title for ZIP name
            try:
                with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                    info = ydl.extract_info(playlist_url, download=False)
                    playlist_title = info.get("title", "playlist_mp3")
                    # Sanitize title for filename
                    playlist_title = "".join(c for c in playlist_title if c.isalnum() or c in (' ', '_', '-')).rstrip()
            except Exception as e:
                st.error(f"Failed to get playlist title: {e}")
                playlist_title = "playlist_mp3"

            success = download_youtube_playlist_mp3(playlist_url, output_folder)
            
            if success:
                # Create ZIP file with playlist title
                zip_name = f"{playlist_title}.zip"
                zip_path = create_zip_file(output_folder, zip_name)
                
                # Create download link
                st.success("Download ready!")
                st.markdown(get_binary_file_downloader_html(zip_path, "ZIP File"), unsafe_allow_html=True)
                
                # Cleanup
                if os.path.exists(zip_path):
                    st.info("The ZIP file will be available for download. You can close this page after downloading.")
    else:
        st.warning("Please enter a valid YouTube playlist URL")