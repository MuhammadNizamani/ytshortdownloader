import streamlit as st
import yt_dlp
import io
import zipfile
import tempfile
import os
from streamlit.components.v1 import html

st.title("Auto-Download Videos 🚀")
option = st.radio("Select Platform:", ("TikTok", "YouTube Shorts"))
st.write("Enter video links (one per line)")
video_links = st.text_area("Paste URLs here:", height=150)
video_urls = [url.strip() for url in video_links.split("\n") if url.strip()]

def download_video(url, platform):
    try:
        ydl_opts = {
            "quiet": True,
            "noplaylist": True,
        }
        
        if platform == "TikTok":
            # For TikTok, enforce MP4
            ydl_opts["format"] = "best[ext=mp4]"
            ydl_opts["merge_output_format"] = "mp4"  # # Force MP4 container
        else:
            # For YouTube Shorts, download best video and audio and let yt-dlp pick a suitable container (usually MKV)
            ydl_opts["format"] = "bestvideo+bestaudio/best"
            # Remove merge_output_format so that merging happens in the container that supports both streams
            ydl_opts.pop("merge_output_format", None)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts["outtmpl"] = os.path.join(temp_dir, "%(title)s.%(ext)s")  # # Set output template
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                with open(file_path, "rb") as f:
                    video_content = f.read()
                return info.get("title", "video"), video_content
    except Exception as e:
        st.error(f"Error downloading {url}: {str(e)}")
        return None, None

if st.button("Start Download"):
    if not video_urls:
        st.error("Please enter at least one URL")
    else:
        videos = []
        with st.spinner("Preparing downloads..."):
            for url in video_urls[:100]:
                title, content = download_video(url, option)
                if content:
                    videos.append((title, content))
        if videos:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for title, content in videos:
                    sanitized_title = "".join(c if c.isalnum() or c in ("-_") else "_" for c in title)
                    # Use .mp4 for TikTok and .mkv for YouTube Shorts
                    extension = "mp4" if option == "TikTok" else "mkv"
                    zip_file.writestr(f"{sanitized_title}.{extension}", content)
            zip_buffer.seek(0)
            st.download_button(
                label="Download All",
                data=zip_buffer,
                file_name="videos.zip",
                mime="application/zip",
                key="auto_download",
            )
            auto_download_js = """
            <script>
                function triggerDownload() {
                    const downloadButton = document.querySelector('[data-testid="stDownloadButton"]');
                    if (downloadButton) {
                        downloadButton.click();
                        document.getElementById('status').innerText = "Downloads started!";
                    }
                }
                let attempts = 0;
                const checkExist = setInterval(() => {
                    if (attempts++ > 50) clearInterval(checkExist);
                    triggerDownload();
                }, 100);
            </script>
            """
            html(auto_download_js)
            st.markdown('<div id="status"></div>', unsafe_allow_html=True)
