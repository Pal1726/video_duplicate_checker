import ffmpeg
import speech_recognition as sr
from io import BytesIO
import time
import random
import string

# Function to generate a unique filename using timestamp and random string
def generate_unique_filename(extension):
    timestamp = int(time.time())  # Use the current time as a timestamp
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))  # Random 6 characters
    return f"{timestamp}_{random_str}{extension}"

def extract_audio_in_memory(video_path):
    try:
        # Extract audio from the video using ffmpeg and store it in memory (using pipe:1)
        out, err = (
            ffmpeg
            .input(video_path)
            .output('pipe:1', format='wav')  # Pipe the audio output in WAV format
            .run(capture_stdout=True, capture_stderr=True)
        )
        return {"status": "success", "audio_data": out}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def transcribe_audio_from_memory(audio_data):
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        audio_file = BytesIO(audio_data)  # Convert audio bytes to a file-like object
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
            # Use Google Web Speech API for transcription
            text = recognizer.recognize_google(audio)
        return {"status": "success", "text": text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def compare_audio(video1_path, video2_path):
    # Step 1: Extract audio from both videos in memory
    extract_result1 = extract_audio_in_memory(video1_path)
    extract_result2 = extract_audio_in_memory(video2_path)

    if extract_result1["status"] == "error" or extract_result2["status"] == "error":
        return {
            "status": "error",
            "message": f"Error extracting audio: {extract_result1['message']} or {extract_result2['message']}"
        }

    # Step 2: Transcribe audio in memory
    transcription1 = transcribe_audio_from_memory(extract_result1["audio_data"])
    transcription2 = transcribe_audio_from_memory(extract_result2["audio_data"])

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
