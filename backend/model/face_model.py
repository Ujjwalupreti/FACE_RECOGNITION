import os
import cv2
import numpy as np
import joblib
import logging
from sklearn.neighbors import KNeighborsClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)

FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
FACES_DIR = os.path.join(STATIC_DIR, "faces")
MODEL_PATH = os.path.join(STATIC_DIR, "face_recognition_model.pkl")

def identify_face(facearray):
    if not os.path.exists(MODEL_PATH):
        return None
    model = joblib.load(MODEL_PATH)
    return model.predict(facearray)[0]

def train_model():
    faces, labels = [], []
    VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}
    
    if not os.path.exists(FACES_DIR):
        return False

    for user in os.listdir(FACES_DIR):
        user_path = os.path.join(FACES_DIR, user)
        if not os.path.isdir(user_path):
            continue
            
        parts = user.split("_")
        if len(parts) < 2:
            continue
            
        roll_no = parts[1] 

        for imgname in os.listdir(user_path):
            if os.path.splitext(imgname)[1].lower() not in VALID_EXTS:
                continue
            img = cv2.imread(os.path.join(user_path, imgname))
            if img is None:
                continue
            img = cv2.resize(img, (50, 50))
            faces.append(img.ravel())
            labels.append(roll_no)

    if not faces:
        logging.error("train_model: no valid images found")
        return False
        
    faces = np.array(faces)
    n_neighbors = max(1, min(5, len(faces) // max(1, len(set(labels)))))
    
    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(faces, labels)
    joblib.dump(knn, MODEL_PATH)
    
    logging.info(f"Model trained: {len(set(labels))} users, {len(faces)} images, k={n_neighbors}")
    return True

def get_total_registered_models():
    if not os.path.exists(FACES_DIR):
        return 0
    return len([d for d in os.listdir(FACES_DIR) if os.path.isdir(os.path.join(FACES_DIR, d))])