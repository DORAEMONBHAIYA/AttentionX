from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import json
from moviepy.editor import VideoFileClip
from faster_whisper import WhisperModel

app = FastAPI(title="AttentionX Backend API")

UPLOAD_DIR = "uploads"
AUDIO_DIR = "audio"
TRANSCRIPTS_DIR = "transcripts"

# 1. Create folders if they don't exist
for directory in [UPLOAD_DIR, AUDIO_DIR, TRANSCRIPTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Load the whisper model once at startup to avoid reloading it on every request
print("Loading faster-whisper base model...")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
print("Model loaded successfully.")

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    # Save the uploaded file
    video_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    filename_without_ext = os.path.splitext(file.filename)[0]
    audio_path = os.path.join(AUDIO_DIR, f"{filename_without_ext}.wav")
    transcript_path = os.path.join(TRANSCRIPTS_DIR, f"{filename_without_ext}.json")
    
    # 2. Extract audio from the uploaded video
    print(f"--> Audio extraction started for {file.filename}")
    try:
        video_clip = VideoFileClip(video_path)
        if video_clip.audio is None:
            video_clip.close()
            # Handle cases where video has no audio
            raise HTTPException(status_code=400, detail="Video file has no audio track.")
            
        video_clip.audio.write_audiofile(audio_path, logger=None)
        video_clip.close()
        print(f"--> Audio extraction done: saved to {audio_path}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error extracting audio: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract audio from video.")
        
    # 3. Transcribe the audio using faster-whisper
    print(f"--> Transcription started for {audio_path}")
    segments_data = []
    try:
        segments, info = whisper_model.transcribe(audio_path, beam_size=5)
        for segment in segments:
            segments_data.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
        print(f"--> Transcription done. Extracted {len(segments_data)} segments.")
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail="Failed to transcribe audio.")
        
    # 4. Save transcript as JSON
    try:
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump({"segments": segments_data}, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving transcript: {e}")
        raise HTTPException(status_code=500, detail="Failed to save transcript.")
        
    # 5. Return response
    return {
        "filename": file.filename,
        "video_path": video_path,
        "audio_path": audio_path,
        "transcript_path": transcript_path,
        "segments": len(segments_data)
    }
