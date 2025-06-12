
import streamlit as st
from pytube import YouTube
import whisper
import os
import tempfile
import moviepy.editor as mp
from transformers import pipeline
import uuid

st.set_page_config(page_title="MyVideoCutter (Opus Clone)", layout="centered")
st.title("🎬 MyVideoCutter - AI Podcast Highlighter")

st.markdown("Paste a YouTube link. Get auto-generated Shorts with captions. No login. 100% free.")

# Step 1: YouTube Input
video_url = st.text_input("Enter YouTube video URL:")

if video_url:
    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(only_audio=False, file_extension='mp4').first()

        with st.spinner("Downloading video..."):
            temp_dir = tempfile.mkdtemp()
            downloaded_path = stream.download(output_path=temp_dir)

        st.success("Downloaded successfully!")

        # Step 2: Transcribe audio
        st.write("Transcribing with Whisper...")
        model = whisper.load_model("base")
        result = model.transcribe(downloaded_path)
        transcript = result['text']

        st.success("Transcription complete.")

        # Step 3: Highlight detection using summarizer
        st.write("Detecting highlights...")
        summarizer = pipeline("summarization")
        chunks = [transcript[i:i+1000] for i in range(0, len(transcript), 1000)]
        summaries = [summarizer(chunk)[0]['summary_text'] for chunk in chunks]

        st.write("Highlights:")
        for i, summary in enumerate(summaries):
            st.markdown(f"**Clip {i+1}:** {summary}")

        # Step 4: Generate sample clip (30s)
        st.write("Generating preview highlight clip (first 30 seconds)...")
        clip = mp.VideoFileClip(downloaded_path).subclip(0, 30)
        clip_path = os.path.join(temp_dir, f"clip_{uuid.uuid4().hex}.mp4")
        clip.write_videofile(clip_path, codec="libx264", audio_codec="aac")

        with open(clip_path, 'rb') as f:
            st.download_button("⬇️ Download Highlight Clip", f, file_name="highlight_clip.mp4")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
