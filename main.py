import os
import shutil
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --- CRITICAL FIX FOR MOVIEPY + PILLOW 10+ ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
# ---------------------------------------------

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
from faster_whisper import WhisperModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = FastAPI(title="AttentionX - Automated Content Repurposing Engine")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure ImageMagick for Windows
IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.2-Q16\magick.exe"
if os.path.exists(IMAGEMAGICK_BINARY):
    print(f"ImageMagick found at: {IMAGEMAGICK_BINARY}")
    change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})
else:
    print("WARNING: ImageMagick not found at expected path. Captions may fail.")

# Directories
UPLOAD_DIR = "uploads"
AUDIO_DIR = "audio"
TRANSCRIPTS_DIR = "transcripts"
HIGHLIGHTS_DIR = "highlights"
CLIPS_DIR = "clips"
VERTICAL_DIR = "clips_vertical"
CAPTIONED_DIR = "clips_captioned"

for directory in [UPLOAD_DIR, AUDIO_DIR, TRANSCRIPTS_DIR, HIGHLIGHTS_DIR, CLIPS_DIR, VERTICAL_DIR, CAPTIONED_DIR]:
    os.makedirs(directory, exist_ok=True)
    # Serve each directory as static files so frontend can access them
    app.mount(f"/{directory}", StaticFiles(directory=directory), name=directory)

# Initialize Faster-Whisper Model
# Using "base" model for a balance between speed and accuracy
# Device can be "cuda" if GPU is available, else "cpu"
print("Loading transcription model...")
model = WhisperModel("base", device="cpu", compute_type="int8")
print("Model loaded successfully.")

# Initialize Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

IMPACT_KEYWORDS = ["important", "amazing", "must", "never", "biggest", "secret", "incredible", "essential", "warning"]

@app.get("/")
async def root():
    return {"message": "AttentionX Backend is running"}

def extract_audio(video_path: str, audio_path: str):
    """
    Extracts audio from a video file and saves it as an MP3.
    """
    try:
        video = VideoFileClip(video_path)
        if video.audio is None:
            raise ValueError("Video file has no audio track.")
        video.audio.write_audiofile(audio_path, logger=None)
        video.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio extraction failed: {str(e)}")

def transcribe_audio(audio_path: str, transcript_path: str):
    """
    Transcribes audio file using faster-whisper and saves result as JSON.
    """
    try:
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        transcript_data = []
        for segment in segments:
            transcript_data.append({
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip()
            })
            
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, indent=4)
            
        return transcript_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

def detect_highlights(segments: list, highlights_path: str):
    """
    Analyzes segments for sentiment and keywords to detect high-impact moments.
    """
    # Advanced AI Hooks & Virality Keywords
    HOOK_KEYWORDS = ["secret", "how to", "stop", "never", "always", "finally", "exposed", "truth", "hack"]
    CONTROVERSY_KEYWORDS = ["wrong", "lie", "fake", "terrible", "worst", "mistake"]
    SURPRISE_KEYWORDS = ["incredible", "unbelievable", "shocking", "wow", "crazy"]

    scored_segments = []
    for seg in segments:
        text = seg['text'].lower()
        
        # 1. Sentiment Score (Abs value of compound to catch both high positive/negative emotion)
        sentiment = analyzer.polarity_scores(text)
        sentiment_score = abs(sentiment['compound']) * 5
        
        # 2. Advanced Keyword & Context Analysis
        keyword_score = sum(2 for word in IMPACT_KEYWORDS if word in text)
        hook_score = sum(3 for word in HOOK_KEYWORDS if word in text)
        controversy_score = sum(2.5 for word in CONTROVERSY_KEYWORDS if word in text)
        surprise_score = sum(2.5 for word in SURPRISE_KEYWORDS if word in text)
        
        # 3. Text length/density (penalize very short or very long segments)
        word_count = len(text.split())
        length_score = 1.0 if 8 <= word_count <= 20 else 0.3
        
        # 4. Question Hook Detection (Videos starting with questions are more viral)
        question_score = 4.0 if text.strip().endswith('?') else 0.0
        
        total_score = round(sentiment_score + keyword_score + hook_score + controversy_score + surprise_score + length_score + question_score, 2)
        print(f"Segment: '{text[:30]}...' | Total Score: {total_score} (S:{sentiment_score:.1f}, H:{hook_score}, Q:{question_score})")
        
        scored_segments.append({
            **seg,
            "sentiment_score": sentiment_score,
            "keyword_score": keyword_score,
            "total_score": total_score
        })
    
    # Sort by total_score and take top 5
    top_highlights = sorted(scored_segments, key=lambda x: x['total_score'], reverse=True)[:5]
    
    with open(highlights_path, "w", encoding="utf-8") as f:
        json.dump(top_highlights, f, indent=4)
        
    return top_highlights


def generate_clips(video_path: str, highlights: list, transcript_segments: list, filename_base: str):
    """
    Cuts the original video into social-ready clips by snapping to transcript segment boundaries
    to ensure we never cut in the middle of a sentence.
    """
    clip_paths = []
    vertical_paths = []
    captioned_paths = []
    
    try:
        video = VideoFileClip(video_path)
        video_duration = video.duration
        
        for i, highlight in enumerate(highlights):
            h_start = highlight['start']
            h_end = highlight['end']
            
            # Find the index of the current highlight segment
            main_idx = -1
            for idx, seg in enumerate(transcript_segments):
                if abs(seg['start'] - h_start) < 0.1:
                    main_idx = idx
                    break
            
            if main_idx == -1: continue

            # Build a "cluster" of segments around the highlight to get ~20s of context
            start_idx = main_idx
            end_idx = main_idx
            
            # Expand backwards and forwards until we hit ~20s or run out of segments
            while (transcript_segments[end_idx]['end'] - transcript_segments[start_idx]['start'] < 20) :
                expanded = False
                if start_idx > 0:
                    start_idx -= 1
                    expanded = True
                if end_idx < len(transcript_segments) - 1:
                    end_idx += 1
                    expanded = True
                if not expanded: break

            # Snap to the exact boundaries of the segment cluster
            final_start = max(0, transcript_segments[start_idx]['start'] - 0.1)
            final_end = min(video_duration, transcript_segments[end_idx]['end'] + 0.1)
            
            filename_suffix = f"{filename_base}_clip{i+1}.mp4"
            clip_path = os.path.join(CLIPS_DIR, filename_suffix)
            vertical_path = os.path.join(VERTICAL_DIR, filename_suffix)
            captioned_path = os.path.join(CAPTIONED_DIR, filename_suffix)
            
            # 1. Cut the clip
            print(f"--> Generating Context-Aware Clip {i+1}: {final_start:.2f}s to {final_end:.2f}s")
            sub_clip = video.subclip(final_start, final_end)
            
            # 2. Save Standard Landscape Clip
            sub_clip.write_videofile(clip_path, codec="libx264", audio_codec="aac", temp_audiofile=f"temp-audio-{i}.m4a", remove_temp=True, logger=None)
            clip_paths.append(clip_path)

            # 3. Create Vertical Version (9:16 Center Crop)
            w, h = sub_clip.size
            target_w = h * (9/16)
            vertical_clip = sub_clip.crop(x_center=w/2, y_center=h/2, width=target_w, height=h).resize(height=1920)
            vertical_clip.write_videofile(vertical_path, codec="libx264", audio_codec="aac", temp_audiofile=f"temp-v-audio-{i}.m4a", remove_temp=True, logger=None)
            vertical_paths.append(vertical_path)

            # 4. Generate Captioned Version
            clip_segments = transcript_segments[start_idx : end_idx + 1]
            text_clips = []
            for seg in clip_segments:
                rel_start = max(0, seg['start'] - final_start)
                rel_end = min(final_end - final_start, seg['end'] - final_start)
                
                # Premium Caption Styling
                txt = (TextClip(seg['text'].upper(), font='Arial-Bold', fontsize=55, color='yellow', 
                                stroke_color='black', stroke_width=2, method='caption', 
                                size=(sub_clip.w*0.85, None))
                       .set_start(rel_start)
                       .set_duration(rel_end - rel_start)
                       .set_position(('center', sub_clip.h * 0.75)))
                text_clips.append(txt)
            
            captioned_video = CompositeVideoClip([sub_clip] + text_clips)
            captioned_video.write_videofile(captioned_path, codec="libx264", audio_codec="aac", temp_audiofile=f"temp-c-audio-{i}.m4a", remove_temp=True, logger=None)
            captioned_paths.append(captioned_path)
            
        video.close()
        return clip_paths, vertical_paths, captioned_paths
    except Exception as e:
        print(f"Error generating context-aware clips: {e}")
        return [], [], []

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """
    Endpoint to upload a video, extract audio, and generate transcript.
    """
    # 1. Save Video
    video_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. Extract Audio
    filename_base = os.path.splitext(file.filename)[0]
    audio_path = os.path.join(AUDIO_DIR, f"{filename_base}.mp3")
    extract_audio(video_path, audio_path)
    
    # 3. Transcribe
    transcript_path = os.path.join(TRANSCRIPTS_DIR, f"{filename_base}.json")
    transcript_segments = transcribe_audio(audio_path, transcript_path)
    
    # 4. Detect Highlights
    highlights_path = os.path.join(HIGHLIGHTS_DIR, f"{filename_base}.json")
    highlights = detect_highlights(transcript_segments, highlights_path)
    
    # 5. Generate Clips
    clip_paths, vertical_paths, captioned_paths = generate_clips(video_path, highlights, transcript_segments, filename_base)
    
    return {
        "filename": file.filename,
        "video_path": video_path,
        "audio_path": audio_path,
        "transcript_path": transcript_path,
        "highlights_path": highlights_path,
        "clips": clip_paths,
        "vertical_clips": vertical_paths,
        "captioned_clips": captioned_paths,
        "segments": transcript_segments,
        "highlights": highlights,
        "segments_count": len(transcript_segments),
        "message": "Video processed, highlights detected, and captioned clips generated!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
