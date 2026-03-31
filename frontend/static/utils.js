export function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `notification ${type}`;
  notification.innerText = message;
  document.body.appendChild(notification);
  
  // Force reflow
  void notification.offsetWidth;
  
  notification.classList.add("show");
  
  setTimeout(() => {
    notification.classList.remove("show");
    setTimeout(() => notification.remove(), 300);
  }, 4000);
}

export function renderChart(chartCanvas, attendance) {
  if (!chartCanvas) return;
  if (window.chartInstance) window.chartInstance.destroy();
  if (!attendance || attendance.length === 0) return;

  const totalDays = 45;
  const attended = attendance.length > totalDays ? totalDays : attendance.length;
  const absent = totalDays - attended;

  // Chart.js global defaults for dark glass theme
  Chart.defaults.color = '#fff';

  window.chartInstance = new Chart(chartCanvas, {
    type: "doughnut", // Doughnut looks better with glassmorphism
    data: {
      labels: ["Attended", "Absent"],
      datasets: [{ 
        data: [attended, absent], 
        backgroundColor: ["#4ade80", "#f87171"],
        borderColor: "transparent",
        hoverOffset: 4
      }]
    },
    options: { 
      responsive: false,
      plugins: {
        legend: { labels: { color: '#fff' } }
      }
    }
  });
}

export function downloadCSV(data) {
  if (!data || data.length === 0) return showNotification("No attendance data available", "error");
  const rows = [["Date"], ...data.slice(0, 45).map(d => [d])];
  const csvContent = "data:text/csv;charset=utf-8," + rows.map(e => e.join(",")).join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "attendance_last_45_days.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}