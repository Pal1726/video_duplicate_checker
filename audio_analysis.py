import ffmpeg
import speech_recognition as sr
from io import BytesIO

def extract_audio_as_wav(video_path):
    try:
        # Extract audio directly into memory
        out, _ = (
            ffmpeg
            .input(video_path)
            .output('pipe:1', format='wav', acodec='pcm_s16le', ac=1, ar='16000')  # Mono, 16kHz for faster transcription
            .run(capture_stdout=True, capture_stderr=True)
        )
        if not out:
            return {"status": "error", "message": "No audio data extracted."}
        return {"status": "success", "audio_data": out}
    except Exception as e:
        return {"status": "error", "message": f"Audio extraction failed: {str(e)}"}

def transcribe_audio(audio_data):
    try:
        recognizer = sr.Recognizer()
        audio_stream = BytesIO(audio_data)
        with sr.AudioFile(audio_stream) as source:
            audio = recognizer.record(source)
            transcription = recognizer.recognize_google(audio)
        return {"status": "success", "text": transcription}
    except sr.RequestError as e:
        return {"status": "error", "message": f"Speech recognition service error: {e}"}
    except sr.UnknownValueError:
        return {"status": "error", "message": "Unable to recognize speech in audio."}
    except Exception as e:
        return {"status": "error", "message": f"Transcription failed: {str(e)}"}

def compare_audio(video1_path, video2_path):
    # Step 1: Extract audio from both videos
    audio1 = extract_audio_as_wav(video1_path)
    audio2 = extract_audio_as_wav(video2_path)

    if audio1["status"] == "error":
        return {"status": "error", "message": audio1["message"]}
    if audio2["status"] == "error":
        return {"status": "error", "message": audio2["message"]}

    # Step 2: Transcribe both audio streams
    transcription1 = transcribe_audio(audio1["audio_data"])
    transcription2 = transcribe_audio(audio2["audio_data"])

    if transcription1["status"] == "error":
        return {"status": "error", "message": transcription1["message"]}
    if transcription2["status"] == "error":
        return {"status": "error", "message": transcription2["message"]}

    # Step 3: Compare transcriptions
    text1 = transcription1["text"].lower()
    text2 = transcription2["text"].lower()
    similarity = text1 == text2

    return {
        "status": "success",
        "text1": transcription1["text"],
        "text2": transcription2["text"],
        "audio_match": similarity,
    }
