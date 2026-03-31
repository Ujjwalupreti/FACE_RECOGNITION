import cv2
import os
import logging
import shutil
import numpy as np
from flask import Flask, request, render_template, jsonify
from datetime import datetime

from db import DatabaseService
from model.face_extraction import extract_faces
from model.face_model import identify_face, train_model, get_total_registered_models

logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR) 
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")
STATIC_DIR   = os.path.join(FRONTEND_DIR, "static")
FACES_DIR    = os.path.join(STATIC_DIR, "faces")
MODEL_PATH   = os.path.join(STATIC_DIR, "face_recognition_model.pkl")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
os.makedirs(FACES_DIR, exist_ok=True)

DatabaseService.init_tables()

@app.route("/")
def home():
    """Serves the main frontend UI."""
    return render_template("index.html")

@app.route("/user_info", methods=["GET"])
def user_info():
    """API endpoint to fetch student info and attendance history for the chart."""
    roll = request.args.get("roll", "").strip()
    if not roll:
        return jsonify({"success": False, "error": "Roll number required"})
        
    student = DatabaseService.get_student_by_roll(roll)
    if not student:
        return jsonify({"success": False, "error": "Student not found"})
        
    records = DatabaseService.get_attendance_records(roll)
    attendance_dates = [r['date_time'].strftime("%Y-%m-%d") for r in records]
    
    return jsonify({
        "success": True,
        "name": student['names'],
        "roll_no": student['roll_no'],
        "course": student['course'],
        "attendance_count": len(records),
        "attendance": attendance_dates
    })

@app.route("/capture", methods=["POST"])
def capture():
    """API endpoint triggered when user clicks 'Capture & Submit' in the UI."""
    if 'frame' not in request.files:
        return jsonify({"status": "error", "message": "No image frame received."})
        
    frame_file = request.files['frame']
    
    try:
        
        npimg = np.frombuffer(frame_file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        
        faces = extract_faces(frame)
        if len(faces) == 0:
            return jsonify({"status": "error", "message": "No face detected. Please align your face and try again."})
            
        
        (x, y, w, h) = faces[0]
        face_img = cv2.resize(frame[y:y+h, x:x+w], (50, 50))
        
        
        roll_no = identify_face(face_img.reshape(1, -1))
        
        if roll_no:
            student_name = DatabaseService.get_student_name_by_roll(roll_no)
            if not DatabaseService.check_attendance_today(roll_no):
                if DatabaseService.mark_attendance(roll_no):
                    return jsonify({"status": "success", "message": f"Attendance marked for {student_name}!"})
                else:
                    return jsonify({"status": "error", "message": "Database error while marking attendance."})
            else:
                return jsonify({"status": "error", "message": f"{student_name} is already marked for today."})
        else:
            return jsonify({"status": "error", "message": "Face not recognized. Please register first."})

    except Exception as e:
        logging.error(f"/capture error: {e}")
        return jsonify({"status": "error", "message": str(e)})


@app.route("/register", methods=["POST"])
def register():
    """API endpoint triggered when a new student submits the registration form."""
    newusername = request.form.get("name", "").strip()
    newuserid   = request.form.get("roll", "").strip()
    newcourse   = request.form.get("course", "Not Specified").strip()
    image_file  = request.files.get("image")

    if not newusername or not newuserid or not image_file:
        return jsonify({"status": "error", "message": "Name, Roll ID, and Image are required."})

    
    npimg = np.frombuffer(image_file.read(), np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    faces = extract_faces(frame)
    
    if len(faces) == 0:
         return jsonify({"status": "error", "message": "No face detected in the uploaded image. Please use a clear photo."})

    
    safe_name = "".join(c for c in newusername if c.isalnum() or c == "-")
    userfolder = os.path.join(FACES_DIR, f"{safe_name}_{newuserid}")
    os.makedirs(userfolder, exist_ok=True)

    
    (x, y, w, h) = faces[0]
    face_crop = frame[y:y+h, x:x+w]
    
    
    cv2.imwrite(os.path.join(userfolder, "0.jpg"), face_crop)
    
    for i in range(1, 10):
        cv2.imwrite(os.path.join(userfolder, f"{i}.jpg"), face_crop)

    
    image_file.seek(0) 
    db_result = DatabaseService.register_student(newusername, newuserid, newcourse, image_file.read())
    
    if not db_result['success']:
        shutil.rmtree(userfolder, ignore_errors=True)
        return jsonify({"status": "error", "message": db_result['message']})

    
    if train_model():
        return jsonify({"status": "success", "message": f"'{newusername}' registered successfully!"})
    else:
        return jsonify({"status": "error", "message": "Added to DB, but model training failed."})


@app.route("/delete_user", methods=["POST"])
def delete_user():
    """API endpoint to delete a user from the database and the file system."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided."})
            
        roll_no = data.get("roll_no", "").strip()
        if not roll_no:
            return jsonify({"success": False, "message": "Roll number is required for deletion."})

        student_name = DatabaseService.get_student_name_by_roll(roll_no)
        
        conn = DatabaseService.create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM take2 WHERE roll_no=%s", (roll_no,))
        conn.commit()
        cursor.close()
        conn.close()
        
        safe_name = "".join(c for c in student_name if c.isalnum() or c == "-")
        folder_name = f"{safe_name}_{roll_no}"
        user_path = os.path.join(FACES_DIR, folder_name)
        
        if os.path.exists(user_path):
            shutil.rmtree(user_path)
            
        if get_total_registered_models() > 0:
            train_model()
        elif os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
            
        return jsonify({"success": True, "message": f"User '{student_name}' ({roll_no}) deleted successfully."})
    except Exception as e:
        logging.error(f"delete_user error: {e}")
        return jsonify({"success": False, "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)