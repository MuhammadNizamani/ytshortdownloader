import streamlit as st
import yt_dlp
import io
import zipfile
import tempfile
import os
from streamlit.components.v1 import html

# Streamlit UI
st.title("Auto-Download Videos 🚀")

# User selection
option = st.radio("Select Platform:", ("TikTok", "YouTube Shorts"))
st.write("Enter video links (one per line)")

video_links = st.text_area("Paste URLs here:", height=150)
video_urls = [url.strip() for url in video_links.split("\n") if url.strip()]

def download_video(url, platform):
    try:
        ydl_opts = {
            "quiet": True,
            "format": "best[ext=mp4]" if platform == "TikTok" else "mp4",
            "noplaylist": True,
            "postprocessors": [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            with tempfile.TemporaryDirectory() as temp_dir:
                ydl_opts["outtmpl"] = os.path.join(temp_dir, "%(title)s.%(ext)s")
                ydl = yt_dlp.YoutubeDL(ydl_opts)
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                
                with open(file_path, "rb") as f:
                    video_content = f.read()
                
                return info["title"], video_content
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
            # Create ZIP in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for title, content in videos:
                    sanitized_title = "".join(
                        c if c.isalnum() or c in ("-_") else "_" for c in title
                    )
                    zip_file.writestr(f"{sanitized_title}.mp4", content)
            zip_buffer.seek(0)
            
            # Create download button
            st.download_button(
                label="Download All",
                data=zip_buffer,
                file_name="videos.zip",
                mime="application/zip",
                key="auto_download",
            )
            
            # JavaScript to trigger download automatically
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
