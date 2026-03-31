# 📸 Face Recognition Attendance System
[![Flask](https://img.shields.io/badge/Backend-Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![JavaScript](https://img.shields.io/badge/Frontend-Vanilla_JS-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![MySQL](https://img.shields.io/badge/Database-MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Scikit-Learn](https://img.shields.io/badge/Machine_Learning-Scikit_Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![OpenCV](https://img.shields.io/badge/Vision-OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)

> **A lightweight, high-performance attendance management system utilizing browser-based webcam streams, OpenCV face extraction, and K-Nearest Neighbors (KNN) classification.**

## 📌 Project Overview
The **Face Recognition Attendance System** replaces manual attendance tracking with a contactless, biometric solution. Built on a Flask backend and a Vanilla JavaScript frontend, the application captures live webcam frames and processes them through a custom Machine Learning pipeline.

The system uses OpenCV's Haar Cascades to instantly locate facial bounding boxes, and a custom-trained **K-Nearest Neighbors (KNN)** model to classify the student. This hybrid approach ensures high accuracy while remaining computationally efficient.

### 🎯 Key Features
* **📸 Browser-Based WebRTC Capture:** Uses the HTML5 API (`webcam.js`) to stream live video and POST `<canvas>` snapshots directly to the Flask backend.
* **🧠 Real-Time Face Extraction:** Utilizes `haarcascade_frontalface_default.xml` to rapidly detect and crop faces from live frames and uploaded registration photos.
* **🤖 Dynamic KNN Classification:** Automatically retrains the `KNeighborsClassifier` model whenever a new student registers or is deleted, saving the trained model state to `face_recognition_model.pkl` via `joblib`.
* **🛡️ Secure Database Logging:** Validates identities against a MySQL database (`db.py`), ensuring students are only marked present once per day.

---

## ⚙️ Technology Stack

| Component | Tech Stack | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS, Vanilla JS | `index.html` UI coupled with modular JS (`main.js`, `webcam.js`, `form.js`) |
| **Backend** | Flask (Python) | API routing (`app.py`) handling multipart image payloads and user data |
| **Database** | MySQL | Relational data storage for student profiles and attendance logs |
| **Computer Vision**| OpenCV (`cv2`) | Image decoding, resizing, and Haar Cascade face detection |
| **Machine Learning**| Scikit-Learn, `joblib` | K-Nearest Neighbors classifier and model state serialization |

---

## 🔄 System Architecture & Workflow

1. **Student Registration (`/register`):** * Frontend POSTs student details and an image.
   * `face_extraction.py` uses Haar Cascades to crop the face. The system saves multiple copies of this crop into a user-specific folder (`static/faces/Name_RollNo`).
   * `face_model.py` triggers `train_model()`, flattening the images into 1D arrays, fitting the KNN model, and serializing it to disk.
2. **Live Attendance (`/capture`):** * `webcam.js` captures a live frame and POSTs it to the server.
   * The frame is decoded (`cv2.imdecode`), and the face is extracted and resized to 50x50 pixels.
   * The KNN model (`face_recognition_model.pkl`) predicts the roll number based on the extracted face array.
3. **Database Validation:** * If recognized, `db.py` checks if the student has already been marked present today. If not, it executes an `INSERT` statement to log the attendance.

---

## 🚀 Future Roadmap

### 🧠 Computer Vision Enhancements
- [ ] **Multi-Face Detection:** Upgrade the `/capture` logic to loop through multiple bounding boxes returned by the Haar Cascade, allowing the system to mark attendance for an entire classroom photo simultaneously.
- [ ] **Anti-Spoofing (Liveness):** Integrate blink detection or motion tracking to ensure students cannot use printed photos or phone screens to trick the webcam.

### 💻 Application Features
- [ ] **Automated Leave Application System:** Build a student dashboard allowing them to submit sick leave or out-of-station requests. Once an admin approves the request in the database, the system will automatically bypass the daily absence penalty.
- [ ] **Admin Analytics Panel:** Expand the `/user_info` endpoint to visualize daily class presence percentages and long-term attendance trends.

---

## 👥 Contributors
* **Ujjwal Upreti**
