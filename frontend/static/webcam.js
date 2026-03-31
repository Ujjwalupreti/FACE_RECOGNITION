export async function startWebcam(video) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    await video.play();
    return stream;
  } catch (err) {
    console.error("Cannot access webcam:", err);
    return null;
  }
}

export function stopWebcam(video, stream) {
  if (stream) stream.getTracks().forEach(track => track.stop());
  if (video) {
    video.pause();
    video.srcObject = null;
  }
}

export async function captureFrame(video, canvas) {
  // Ensure video is playing and metadata is loaded
  if (video.readyState < 2) {
      await new Promise(resolve => {
          video.onloadedmetadata = () => resolve();
      });
  }

  const ctx = canvas.getContext("2d");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  
  // Draw the current video frame onto the canvas
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Convert canvas to Blob (JPEG file)
  return new Promise(resolve => canvas.toBlob(blob => resolve(blob), "image/jpeg", 0.9));
}