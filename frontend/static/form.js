import { showNotification } from './utils.js';

export function handleRegisterForm(registerForm) {
  registerForm.addEventListener("submit", async e => {
    e.preventDefault();
    const formData = new FormData(registerForm);
    const submitBtn = registerForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;

    submitBtn.textContent = "Registering...";
    submitBtn.disabled = true;

    try {
      const res = await fetch("/register", { method: "POST", body: formData });
      const data = await res.json();
      if (data.success || data.status === "success") {
        showNotification(data.message || "Registered Successfully", "success");
        registerForm.reset();
      } else {
        showNotification(data.message, "error");
      }
    } catch (err) {
      showNotification("Failed to register: " + err.message, "error");
    } finally {
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    }
  });
}

export function handleUserInfoForm(userInfoForm, renderChartCallback) {
  userInfoForm.addEventListener("submit", async e => {
    e.preventDefault();
    const roll = document.querySelector("#rollSearch").value.trim();
    const detailsDiv = document.querySelector("#userInfoResult");
    if (!roll) return showNotification("Please enter a roll number", "error");

    const submitBtn = userInfoForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = "Searching...";
    submitBtn.disabled = true;

    try {
      const res = await fetch(`/user_info?roll=${roll}`);
      const data = await res.json();
      if (data.error || !data.success) {
        detailsDiv.innerHTML = `<p class="error">${data.error || data.message}</p>`;
        renderChartCallback([]); 
      } else {
        detailsDiv.innerHTML = `
            <h3>Student Found</h3>
            <p><strong>Name:</strong> ${data.name}</p>
            <p><strong>Roll No:</strong> ${data.roll_no}</p>
            <p><strong>Course:</strong> ${data.course || "N/A"}</p>
            <p><strong>Attendance Count:</strong> ${data.attendance_count || 0}</p>
        `;
        renderChartCallback(data.attendance || []);
      }
    } catch (err) {
      detailsDiv.innerHTML = `<p class="error">Something went wrong.</p>`;
    } finally {
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    }
  });
}