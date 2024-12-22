document.getElementById('uploadForm').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent the default form submission behavior

    const video1 = document.getElementById('video1').files[0];
    const video2 = document.getElementById('video2').files[0];
    const progress = document.getElementById('uploadProgress');
    const statusMessage = document.getElementById('statusMessage');

    if (!video1 || !video2) {
        alert("Please select both videos before uploading.");
        return;
    }

    try {
        statusMessage.textContent = "Compressing Video 1...";
        const compressedVideo1 = await compressVideo(video1);
        statusMessage.textContent = "Compressing Video 2...";
        const compressedVideo2 = await compressVideo(video2);

        statusMessage.textContent = "Uploading videos...";
        const formData = new FormData();
        formData.append('video1', compressedVideo1);
        formData.append('video2', compressedVideo2);

        const response = await uploadVideos(formData, progress);
        const result = await response.json();

        statusMessage.textContent = result.message || "Videos uploaded and processed successfully!";
    } catch (error) {
        statusMessage.textContent = "An error occurred: " + error.message;
    }
});

async function compressVideo(videoFile) {
    const { createFFmpeg, fetchFile } = FFmpeg;
    const ffmpeg = createFFmpeg({ log: true });
    await ffmpeg.load();

    const videoName = videoFile.name;
    await ffmpeg.FS('writeFile', videoName, await fetchFile(videoFile));

    const compressedName = `compressed_${videoName}`;
    await ffmpeg.run('-i', videoName, '-vcodec', 'libx264', '-crf', '28', '-preset', 'ultrafast', compressedName);

    const compressedData = ffmpeg.FS('readFile', compressedName);
    const compressedBlob = new Blob([compressedData.buffer], { type: 'video/mp4' });
    return new File([compressedBlob], compressedName, { type: 'video/mp4' });
}

async function uploadVideos(formData, progress) {
    const xhr = new XMLHttpRequest();
    return new Promise((resolve, reject) => {
        xhr.open('POST', '/upload', true);
        xhr.upload.onprogress = function (e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progress.value = percentComplete;
            }
        };
        xhr.onload = function () {
            if (xhr.status === 200) {
                resolve(new Response(xhr.responseText, { status: xhr.status }));
            } else {
                reject(new Error("Failed to upload videos. Status: " + xhr.status));
            }
        };
        xhr.onerror = function () {
            reject(new Error("Upload failed."));
        };
        xhr.send(formData);
    });
}
