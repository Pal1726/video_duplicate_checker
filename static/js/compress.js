document.getElementById('uploadForm').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent the default form submission behavior

    const video1 = document.getElementById('video1').files[0];
    const video2 = document.getElementById('video2').files[0];
    const progress = document.getElementById('uploadProgress'); // Progress bar element
    const statusMessage = document.getElementById('statusMessage'); // Status message element

    // Check if both videos are selected
    if (!video1 || !video2) {
        alert("Please select both videos before uploading.");
        return;
    }

    try {
        // Compress the first video
        statusMessage.textContent = "Compressing Video 1...";
        const compressedVideo1 = await compressVideo(video1);

        // Compress the second video
        statusMessage.textContent = "Compressing Video 2...";
        const compressedVideo2 = await compressVideo(video2);

        // Prepare the form data for upload
        statusMessage.textContent = "Uploading videos...";
        const formData = new FormData();
        formData.append('video1', compressedVideo1);
        formData.append('video2', compressedVideo2);

        // Upload videos and track progress
        const response = await uploadVideos(formData, progress);

        // Handle the response from the server
        const result = await response.json();
        statusMessage.textContent = result.message || "Videos uploaded and processed successfully!";
    } catch (error) {
        statusMessage.textContent = "An error occurred: " + error.message;
    }
});

// Function to compress video using FFmpeg
async function compressVideo(videoFile) {
    const { createFFmpeg, fetchFile } = FFmpeg;
    const ffmpeg = createFFmpeg({ log: true }); // Initialize FFmpeg
    await ffmpeg.load(); // Load FFmpeg core

    const videoName = videoFile.name; // Original video file name
    await ffmpeg.FS('writeFile', videoName, await fetchFile(videoFile)); // Load video into FFmpeg

    const compressedName = `compressed_${videoName}`; // Compressed video file name
    // Run FFmpeg compression
    await ffmpeg.run('-i', videoName, '-vcodec', 'libx264', '-crf', '28', '-preset', 'ultrafast', compressedName);

    // Retrieve the compressed video file
    const compressedData = ffmpeg.FS('readFile', compressedName);
    const compressedBlob = new Blob([compressedData.buffer], { type: 'video/mp4' });
    return new File([compressedBlob], compressedName, { type: 'video/mp4' });
}

// Function to upload videos with progress tracking
async function uploadVideos(formData, progress) {
    const xhr = new XMLHttpRequest(); // Create XMLHttpRequest
    return new Promise((resolve, reject) => {
        xhr.open('POST', '/upload', true); // Open POST request to '/upload'

        // Monitor upload progress and update the progress bar
        xhr.upload.onprogress = function (e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progress.value = percentComplete; // Update progress bar
            }
        };

        // Handle successful upload
        xhr.onload = function () {
            if (xhr.status === 200) {
                resolve(new Response(xhr.responseText, { status: xhr.status })); // Resolve the promise
            } else {
                reject(new Error("Failed to upload videos. Status: " + xhr.status)); // Reject on error
            }
        };

        // Handle upload errors
        xhr.onerror = function () {
            reject(new Error("Upload failed.")); // Reject on network error
        };

        xhr.send(formData); // Send the form data
    });
}
