import ffmpeg
import speech_recognition as sr
import os
import time
import random
import string

# Function to generate a unique filename using timestamp and random string
def generate_unique_filename(extension):
    timestamp = int(time.time())  # Use the current time as a timestamp
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))  # Random 6 characters
    return f"{timestamp}_{random_str}{extension}"

def extract_audio(video_path, audio_path):
    try:
        # Extract audio from the video using ffmpeg with the -y flag to overwrite any existing files
        ffmpeg.input(video_path).output(audio_path, y=None).run()
        return {"status": "success", "message": "Audio extracted successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def transcribe_audio(audio_path):
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            # Use Google Web Speech API for transcription
            text = recognizer.recognize_google(audio_data)
        return {"status": "success", "text": text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def compare_audio(video1_path, video2_path):
    # Generate unique filenames for each audio file
    audio1_path = generate_unique_filename(".wav")
    audio2_path = generate_unique_filename(".wav")

    # Step 1: Extract audio from both videos
    extract_result1 = extract_audio(video1_path, audio1_path)
    extract_result2 = extract_audio(video2_path, audio2_path)

    if extract_result1["status"] == "error" or extract_result2["status"] == "error":
        return {
            "status": "error",
            "message": f"Error extracting audio: {extract_result1['message']} or {extract_result2['message']}"
        }

    # Step 2: Transcribe audio
    transcription1 = transcribe_audio(audio1_path)
    transcription2 = transcribe_audio(audio2_path)

    if transcription1["status"] == "error" or transcription2["status"] == "error":
        return {
            "status": "error",
            "message": f"Error transcribing audio: {transcription1['message']} or {transcription2['message']}"
        }

    # Step 3: Compare transcriptions
    transcription1_text = transcription1["text"].lower()
    transcription2_text = transcription2["text"].lower()

    similarity = (transcription1_text == transcription2_text)

    return {
        "status": "success",
        "text1": transcription1["text"],
        "text2": transcription2["text"],
        "audio_match": similarity,
    }
