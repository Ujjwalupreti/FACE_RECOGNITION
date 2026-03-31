import { startWebcam, stopWebcam, captureFrame } from './webcam.js';
import { handleRegisterForm, handleUserInfoForm } from './form.js';
import { showNotification, renderChart, downloadCSV } from './utils.js';

document.addEventListener("DOMContentLoaded", () => {
  const registerForm = document.querySelector("#registerForm");
  const userInfoForm = document.querySelector("#userInfoForm");
  const chartCanvas = document.getElementById("attendanceChart");
  const downloadCsvBtn = document.getElementById("downloadCsvBtn");
  
  const video = document.getElementById("webcam");
  const canvas = document.getElementById("snapshot");
  const startCamBtn = document.getElementById("startCamBtn");
  const captureBtn = document.getElementById("captureBtn");
  
  let stream = null;
  let currentAttendanceData = [];

  if (registerForm) handleRegisterForm(registerForm);
  if (userInfoForm) handleUserInfoForm(userInfoForm, (data) => {
    currentAttendanceData = data;
    renderChart(chartCanvas, data);
    downloadCsvBtn.style.display = data.length > 0 ? "inline-block" : "none";
  });

  if (startCamBtn && captureBtn) {
    startCamBtn.addEventListener("click", async () => {
      stream = await startWebcam(video);
      if (stream) {
        startCamBtn.disabled = true;
        captureBtn.disabled = false;
        showNotification("Camera started. Align your face and click capture.", "info");
      }
    });

    captureBtn.addEventListener("click", async () => {
      if (!stream) return showNotification("Start the camera first!", "error");
      
      const originalText = captureBtn.textContent;
      captureBtn.textContent = "Processing...";
      captureBtn.disabled = true;

      const blob = await captureFrame(video, canvas);
      stopWebcam(video, stream);
      
      startCamBtn.disabled = false;
      captureBtn.textContent = originalText;

      if (!blob) {
        captureBtn.disabled = false;
        return showNotification("Failed to capture frame.", "error");
      }

      const formData = new FormData();
      formData.append("frame", blob, "frame.jpg");

      try {
        const res = await fetch("/capture", { method: "POST", body: formData });
        const data = await res.json();
        if (data.status === "success") showNotification(data.message, "success");
        else showNotification(data.message, "error");
      } catch (err) {
        showNotification("Failed: " + err.message, "error");
      }
    });
  }

  if (downloadCsvBtn) downloadCsvBtn.addEventListener("click", () => downloadCSV(currentAttendanceData));

  // Smooth Scrolling
  document.querySelectorAll("nav a").forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      const targetId = link.getAttribute("href").substring(1);
      const targetSection = document.getElementById(targetId);
      if (targetSection) targetSection.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
});