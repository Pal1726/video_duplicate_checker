from flask import Flask, request, render_template, redirect, url_for
import os
from metadata_analysis import compare_metadata
from frame_analysis import compare_frames  # Import the frame comparison function
from audio_analysis import compare_audio  # Import the audio comparison function

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'video1' not in request.files or 'video2' not in request.files:
        return "Please upload two videos for comparison."
    
    # Get the video files from the request
    video1 = request.files['video1']
    video2 = request.files['video2']

    # Check if the videos exist
    if video1 and video2:
        # Save the compressed videos to the uploads folder
        video1_path = os.path.join(app.config['UPLOAD_FOLDER'], 'compressed_' + video1.filename)
        video2_path = os.path.join(app.config['UPLOAD_FOLDER'], 'compressed_' + video2.filename)
        
        # Save the compressed videos (you should send the compressed video from the client-side)
        video1.save(video1_path)
        video2.save(video2_path)

        # Now proceed with video comparison (metadata, frame, and audio analysis)
        metadata_comparison_result = compare_metadata(video1_path, video2_path)
        
        if metadata_comparison_result["status"] == "error":
            return metadata_comparison_result["message"]
        
        # Frame-by-frame comparison
        frame_comparison_result = compare_frames(video1_path, video2_path)

        # Audio comparison
        audio_comparison_result = compare_audio(video1_path, video2_path)
        
        if audio_comparison_result["status"] == "error":
            return audio_comparison_result["message"]
        
        # Combine results (weights: 20% metadata, 40% frame, 40% audio)
        overall_similarity = calculate_overall_similarity(metadata_comparison_result, frame_comparison_result, audio_comparison_result)
        
        return render_template('results.html', 
                               metadata_result=metadata_comparison_result, 
                               frame_result=frame_comparison_result, 
                               audio_result=audio_comparison_result,
                               overall_similarity=overall_similarity)

    return "Failed to upload videos."


def calculate_overall_similarity(metadata_result, frame_result, audio_result):
    # Weights: 20% for metadata, 40% for frame comparison, 40% for audio comparison
    metadata_score = 0
    if metadata_result["duration_match"] and metadata_result["resolution_match"] and metadata_result["codec_match"]:
        metadata_score = 100
    else:
        metadata_score = 0

    frame_similarity = frame_result.get("frame_similarity", 0)
    audio_similarity = 100 if audio_result["audio_match"] else 0
    
    # Calculate overall similarity
    overall_similarity = (0.2 * metadata_score) + (0.4 * frame_similarity) + (0.4 * audio_similarity)
    return overall_similarity

if __name__ == '__main__':
    app.run(debug=True)
