import cv2
import face_recognition
import pickle
import numpy as np
import mysql.connector
import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog
from PIL import Image,ImageTk

def create_connection():
    return mysql.connector.connect(
       host="localhost", port="3306", user="root", password="XX---XX", database="XXX"
    )        
    # Enter the information of the SQL database

def register_user(name, department, image_path):# USE to enter the name,department and photo of the new user
    try:
        conn = create_connection()
        cursor = conn.cursor()

        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            messagebox.showerror("Error", "No face found in the image.")
            return

        face_encoding = face_encodings[0]
        encoding_blob = face_encoding.tobytes()

        cursor.execute("INSERT INTO take2 (names, departments, encoding_blob) VALUES (%s, %s, %s)",
                       (name, department, encoding_blob))
        conn.commit()
        messagebox.showinfo("Success", f"User  {name} registered successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        conn.close()

def load_known_faces():# USE to load the information from database for encoding 
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT names,departments,encoding_blob FROM take2")
    known_faces = []
    known_names = []
    known_ids = []

    for names,departments,encoding_blob in cursor.fetchall():
        face_encoding = np.frombuffer(encoding_blob, dtype=np.float64)
        known_faces.append(face_encoding)
        known_names.append(names)
        known_ids.append(departments)

    conn.close()
    return known_faces, known_names

def load(name,department,path):
    register_user(name,department,path)

def Form():#FORM GUI
    def upload_photo():
        file_path = filedialog.askopenfilename(title="Select a Photo", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            try:
                img = Image.open(file_path)
                img.thumbnail((100, 100)) 
                img = ImageTk.PhotoImage(img)
                photo_label.config(image=img)
                photo_label.image = img 
                return file_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def submit_form():
        name = name_entry.get()
        department = dept_entry.get()
        if not name or not department:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
        else:
            messagebox.showinfo("Form Submitted", f"Name: {name}\nDepartment: {department}")
            load(name,department,upload_photo())

    root = tk.Tk()
    root.title("User Input Form")

    name_label = tk.Label(root, text="Name:")
    name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    name_entry = tk.Entry(root)
    name_entry.grid(row=0, column=1, padx=10, pady=5)
    name=name_entry.get()

    dept_label = tk.Label(root, text="Department:")
    dept_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    dept_entry = tk.Entry(root)
    dept_entry.grid(row=1, column=1, padx=10, pady=5)
    dept=dept_entry.get()

    photo_label = tk.Label(root, text="No photo selected", width=20, height=4, relief="solid")
    photo_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    submit_button = tk.Button(root, text="Submit", command=submit_form)
    submit_button.grid(row=4, column=0, columnspan=2, pady=10)   
    root.mainloop()

def procces():
   
    known_faces, known_names=load_known_faces()
    knownlist=[known_faces,known_names]

    idfile=open("ENCODE.p",'wb')
    pickle.dump(knownlist,idfile)
    idfile.close()

def capture():
    cap=cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)
    
    imgback=cv2.imread(r"DataSCI_Ayl\\Project_Face_detection\\Image\\background1.png")
    
    file=open('ENCODE.p','rb')
    knowidlist=pickle.load(file)
    file.close()
    knownlist,idfile=knowidlist

    while True:
        success,img=cap.read()
        imgs=cv2.resize(img,(0,0),None,0.25,0.25)
        imgs=cv2.cvtColor(imgs,cv2.COLOR_BGR2RGB)

        frame=face_recognition.face_locations(imgs)
        Encodeframe=face_recognition.face_encodings(imgs,frame)
        
        imgback[162:162+480,55:55+640]=img

        ido=False
        Index=0
        for encoderface,facelac in zip(Encodeframe,frame):

            matches=face_recognition.compare_faces(knownlist,encoderface)
            dis=face_recognition.face_distance(knownlist,encoderface)
            index=np.argmin(dis)
            if matches[index]:
                ido=True
                Index=index
        if(ido==True):
            cv2.putText(imgback,str(idfile[Index]),(55,200),cv2.FONT_HERSHEY_COMPLEX,1.0,(0,255,0),2)  
        else:
            cv2.putText(imgback,"Unknown",(55,250),cv2.FONT_HERSHEY_COMPLEX,1.0,(0,255,0),2)         
            cv2.putText(imgback,"PLEASE REGISTER",(55,200),cv2.FONT_HERSHEY_COMPLEX,1.0,(0,255,0),2)  
        cv2.imshow("Face Attendance",imgback)
        if(cv2.waitKey(25)==ord('a')):# change the waitkey accoding to needs
            break
    cap.release()  

def MAIN():
    procces()# use to encoding the image in the database
    capture()#open the webcam for capture the live video       
    
def call():
    root = tk.Tk()
    root.title("User Input Form")
    root.geometry("500x450")
    bg= PhotoImage(file="DataSCI_Ayl\\Project_Face_detection\\Image\\back.png")
    label=Label(root,image=bg)
    label.place(x=0,y=0)
    
    image =Image.open('DataSCI_Ayl\\Project_Face_detection\\Image\\logo.png')
    image=ImageTk.PhotoImage(image)
    image_label=tk.Label(root,image=image)
    image_label.pack(pady=5)
    
    text1 =tk.Label(root,text="Welcome",width=40,height=1,font=("helventica",16))
    text2 =tk.Label(root,text="Scan the face here",width=40,height=1,font=("helventica",8))
    text1.pack(pady=10)
    text2.pack(pady=10)
    
    capture_button = Button(root, text="Face Scan", command=MAIN,bg="RED",fg="BLACK")
    capture_button.pack(pady=15)
    
    register_button=Button(root,text="Register User",command=Form,bg="RED",fg="BLACK")
    register_button.pack(pady=5)
    root.mainloop()    
    
if __name__=="__main__":
    #call function
    call() 