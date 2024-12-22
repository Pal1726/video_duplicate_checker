document.getElementById('uploadForm').addEventListener('submit', function (event) {
    event.preventDefault();  // Prevent the form from submitting immediately

    // Get the video files
    const video1 = document.getElementById('video1').files[0];
    const video2 = document.getElementById('video2').files[0];

    if (video1 && video2) {
        // Call the compression function for both videos
        compressAndUpload(video1, 'video1');
        compressAndUpload(video2, 'video2');
    }
});

async function compressAndUpload(videoFile, videoInputName) {
    try {
        const compressedVideo = await compressVideo(videoFile);
        
        // Create a new FormData object to submit the compressed video
        const formData = new FormData();
        formData.append(videoInputName, compressedVideo);

        // Use Fetch API to upload the compressed video to Flask
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        alert(result.message);  // Display the response from Flask
    } catch (error) {
        alert('Error during video compression or upload: ' + error.message);
    }
}

async function compressVideo(videoFile) {
    // Here we use ffmpeg.wasm for video compression
    const { createFFmpeg, fetchFile } = FFmpeg; // Assuming ffmpeg.wasm is loaded

    const ffmpeg = createFFmpeg({ log: true });
    await ffmpeg.load();

    // Create a temporary file for the video in the FFmpeg virtual filesystem
    await ffmpeg.FS('writeFile', videoFile.name, await fetchFile(videoFile));

    // Define a filename for the output compressed video
    const outputFileName = 'compressed_' + videoFile.name;

    // Run FFmpeg command to compress the video (adjust the quality here)
    await ffmpeg.run('-i', videoFile.name, '-vcodec', 'libx264', '-crf', '28', outputFileName);

    // Get the compressed video from the virtual filesystem
    const compressedVideoData = ffmpeg.FS('readFile', outputFileName);

    // Create a Blob and return the compressed video file
    const compressedVideoBlob = new Blob([compressedVideoData.buffer], { type: 'video/mp4' });
    return new File([compressedVideoBlob], outputFileName, { type: 'video/mp4' });
}
