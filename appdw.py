import streamlit as st
import yt_dlp
import io
import requests
import zipfile
from streamlit.components.v1 import html

# Streamlit UI
st.title("Auto-Download YouTube Shorts 🚀")
st.write("Enter YouTube Shorts links (one per line)")

shorts_links = st.text_area("Paste URLs here:", height=150)
shorts_urls = [url.strip() for url in shorts_links.split("\n") if url.strip()]

def download_shorts_video(url):
    try:
        ydl_opts = {"format": "mp4", "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
            response = requests.get(video_url, headers=info.get('http_headers', {}))
            return info['title'], response.content
    except Exception as e:
        st.error(f"Error with {url}: {str(e)}")
        return None, None

if st.button("Start Auto-Download"):
    if not shorts_urls:
        st.error("Please enter at least one URL")
    else:
        videos = []
        with st.spinner("Preparing downloads..."):
            for url in shorts_urls[:100]:
                title, content = download_shorts_video(url)
                if content:
                    videos.append((title, content))
        
        if videos:
            # Create ZIP in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for title, content in videos:
                    zip_file.writestr(f"{title.replace(' ', '_')}.mp4", content)
            zip_buffer.seek(0)
            
            # Create download button
            st.download_button(
                label="Download All",
                data=zip_buffer,
                file_name="youtube_shorts.zip",
                mime="application/zip",
                key="auto_download"
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
                // Retry until button exists
                let attempts = 0;
                const checkExist = setInterval(() => {
                    if (attempts++ > 50) clearInterval(checkExist);
                    triggerDownload();
                }, 100);
            </script>
            """
            html(auto_download_js)
            st.markdown('<div id="status"></div>', unsafe_allow_html=True)