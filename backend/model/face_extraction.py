import cv2
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASCADE_PATH = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")
face_detector = cv2.CascadeClassifier(CASCADE_PATH)

def extract_faces(img):
    """
    Takes an image frame and returns coordinates of detected faces.
    """
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.2, 5, minSize=(20, 20))
        return faces
    except Exception as e:
        logging.error(f"Face extraction error: {e}")
        return []