import ffmpeg

def get_video_metadata(video_path):
    try:
        metadata = ffmpeg.probe(video_path)
        # Extract useful metadata fields
        video_stream = next((stream for stream in metadata['streams'] if stream['codec_type'] == 'video'), None)
        if not video_stream:
            raise ValueError("No video stream found")
        return {
            'duration': float(video_stream['duration']),
            'resolution': f"{video_stream['width']}x{video_stream['height']}",
            'codec': video_stream['codec_name']
        }
    except Exception as e:
        return {"error": str(e)}

def compare_metadata(video1_path, video2_path):
    metadata1 = get_video_metadata(video1_path)
    metadata2 = get_video_metadata(video2_path)

    # Check for errors in metadata extraction
    if "error" in metadata1 or "error" in metadata2:
        return {
            "status": "error",
            "message": f"Error extracting metadata: {metadata1.get('error') or metadata2.get('error')}"
        }

    # Perform metadata comparison
    comparison = {
        "status": "success",
        "message": "Metadata comparison successful",
        "duration_match": metadata1['duration'] == metadata2['duration'],
        "resolution_match": metadata1['resolution'] == metadata2['resolution'],
        "codec_match": metadata1['codec'] == metadata2['codec'],
        "metadata1": metadata1,
        "metadata2": metadata2,
    }
    return comparison

