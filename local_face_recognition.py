import cv2
import time
import requests
import os
import urllib.request
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from deepface import DeepFace
import mediapipe as mp
import math

MODEL_PATH = "face_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print("Downloading FaceLandmarker model...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Download complete.")

API_UPDATE_STATUS = "http://localhost:3000/api/attendance"
COOLDOWN_SECONDS = 5

# Set your Supabase keys here for the enrollment feature
SUPABASE_URL = "https://bkzprvmspptbqitcuktg.supabase.co/rest/v1/students"
SUPABASE_KEY = "sb_publishable_otwaSx22jr_AJf_VQtL4jQ_szQr0wYI"

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Face Attendance System")
        
        self.camera_capture = None
        self.is_camera_running = False
        self.last_recognition_timestamps = {}
        self.is_processing_frame = False
        self.detected_faces = []
        
        base_options = mp.tasks.BaseOptions(model_asset_path=MODEL_PATH)
        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False)
        self.face_landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(options)
        
        self.liveness_passed = False
        self.eyes_were_open = False
        self.last_face_time = 0
        
        self._setup_ui()
        self._detect_available_cameras()

    def _setup_ui(self):
        self.camera_label = tk.Label(self.root, text="Select Camera:")
        self.camera_label.pack(pady=5)
        
        self.camera_selector = ttk.Combobox(self.root)
        self.camera_selector.pack(pady=5)
        
        self.toggle_camera_button = tk.Button(self.root, text="Start Camera", command=self.toggle_camera, width=20)
        self.toggle_camera_button.pack(pady=5)
        
        self.enroll_button = tk.Button(self.root, text="Enroll New Student", command=self.open_enrollment_dialog, width=20, state=tk.DISABLED)
        self.enroll_button.pack(pady=5)
        
        self.video_display = tk.Label(self.root)
        self.video_display.pack(pady=5)
        
        self.log_output = tk.Text(self.root, height=12, width=60)
        self.log_output.pack(pady=5)

    def _detect_available_cameras(self):
        self.log("Scanning for available cameras...")
        available_cameras = []
        for camera_index in range(5):
            # Omit cv2.CAP_DSHOW because it causes artifacting with virtual cameras
            capture = cv2.VideoCapture(camera_index)
            if capture.isOpened():
                available_cameras.append(str(camera_index))
                capture.release()
        
        if available_cameras:
            self.camera_selector['values'] = available_cameras
            self.camera_selector.current(0)
            self.log(f"Found cameras: {available_cameras}")
        else:
            self.log("No cameras found")

    def log(self, message):
        self.log_output.insert(tk.END, message + "\n")
        self.log_output.see(tk.END)
        print(message)
        
    def toggle_camera(self):
        if self.is_camera_running:
            self.is_camera_running = False
            self.toggle_camera_button.config(text="Start Camera")
            self.enroll_button.config(state=tk.DISABLED)
            if self.camera_capture:
                self.camera_capture.release()
            self.video_display.config(image='')
            self.liveness_passed = False
            self.log("Camera stopped.")
        else:
            selected_camera = self.camera_selector.get()
            camera_index = int(selected_camera) if selected_camera.isdigit() else selected_camera
            self.camera_capture = cv2.VideoCapture(camera_index)
                
            if not self.camera_capture.isOpened():
                self.log("Error: Cannot open the selected camera.")
                return
                
            self.is_camera_running = True
            self.toggle_camera_button.config(text="Stop Camera")
            self.enroll_button.config(state=tk.NORMAL)
            self.log("Camera started. Looking for faces...")
            self.update_video_frame()
            
    def _calculate_ear(self, face_landmarks, eye_indices, frame_width, frame_height):
        pts = [(face_landmarks[idx].x * frame_width, face_landmarks[idx].y * frame_height) for idx in eye_indices]
        v1 = math.hypot(pts[1][0] - pts[5][0], pts[1][1] - pts[5][1])
        v2 = math.hypot(pts[2][0] - pts[4][0], pts[2][1] - pts[4][1])
        h = math.hypot(pts[0][0] - pts[3][0], pts[0][1] - pts[3][1])
        return (v1 + v2) / (2.0 * h) if h != 0 else 0.0

    def update_video_frame(self):
        if not self.is_camera_running: 
            return
        
        success, frame = self.camera_capture.read()
        if success:
            frame_height, frame_width, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            detection_result = self.face_landmarker.detect(mp_image)
            
            if detection_result.face_landmarks:
                self.last_face_time = time.time()
                
                for face_landmarks in detection_result.face_landmarks:
                    # Continuously prevent "tilting phone" spoofing
                    dx = face_landmarks[263].x - face_landmarks[33].x
                    dy = face_landmarks[263].y - face_landmarks[33].y
                    angle = math.degrees(math.atan2(abs(dy), abs(dx)))
                    if angle > 15:
                        cv2.putText(frame, "Keep your head straight!", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        self.eyes_were_open = False
                        self.liveness_passed = False
                        self.detected_faces = []
                        break
                        
                if not self.liveness_passed:
                    for face_landmarks in detection_result.face_landmarks:
                        # Re-calculate or just use the same face_landmarks
                        left_ear = self._calculate_ear(face_landmarks, [33, 160, 158, 133, 153, 144], frame_width, frame_height)
                        right_ear = self._calculate_ear(face_landmarks, [362, 385, 387, 263, 373, 380], frame_width, frame_height)
                        
                        avg_ear = (left_ear + right_ear) / 2.0
                        
                        if avg_ear > 0.25:
                            self.eyes_were_open = True
                        elif avg_ear < 0.2 and getattr(self, 'eyes_were_open', False):
                            self.liveness_passed = True
                            break
                            
                if self.liveness_passed:
                    cv2.putText(frame, "Liveness Passed!", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    if not self.is_processing_frame:
                        self.is_processing_frame = True
                        threading.Thread(target=self.recognize_faces, args=(frame.copy(),), daemon=True).start()
                else:
                    cv2.putText(frame, "Please blink your eyes...", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            else:
                if time.time() - getattr(self, 'last_face_time', 0) > 1.0:
                    self.liveness_passed = False
                    self.eyes_were_open = False
                    self.detected_faces = []
            
            # Only keep face bounding boxes that were updated within the last 2 seconds
            self.detected_faces = [face for face in self.detected_faces if time.time() - face['timestamp'] < 2]
            
            for face in self.detected_faces:
                color = (0, 0, 255) if face.get('is_fake', False) else (0, 255, 0)
                cv2.rectangle(frame, (face['x'], face['y']), (face['x'] + face['width'], face['y'] + face['height']), color, 2)
                cv2.putText(frame, face['name'], (face['x'], face['y'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            rgb_frame_ui = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_obj = Image.fromarray(rgb_frame_ui)
            tk_image = ImageTk.PhotoImage(image=image_obj)
            
            self.video_display.imgtk = tk_image
            self.video_display.configure(image=tk_image)
            
        self.root.after(30, self.update_video_frame)
        
    def recognize_faces(self, frame):
        try:
            # Enable deep learning-based Anti-Spoofing (FasNet) built into DeepFace
            results = DeepFace.represent(img_path=frame, model_name="Facenet512", enforce_detection=True, detector_backend="mtcnn", anti_spoofing=True)
            current_time = time.time()
            
            for result in results:
                # If the AI determines the face is a spoof (photo/video), reject it immediately
                if not result.get("is_real", True):
                    self.root.after(0, self.log, "Security Alert: Fake face (spoofing) detected and blocked!")
                    self.liveness_passed = False
                    self.eyes_were_open = False
                    self.detected_faces = [{'name': 'FAKE FACE BLOCKED!', 'x': result["facial_area"]["x"], 'y': result["facial_area"]["y"], 'width': result["facial_area"]["w"], 'height': result["facial_area"]["h"], 'timestamp': current_time, 'is_fake': True}]
                    continue
                    
                embedding_vector = result["embedding"]
                print(f"[Debug] Extracted Face Vector (Length {len(embedding_vector)}): {embedding_vector}")
                self.root.after(0, self.log, f"Scanned vector starts with: {str(embedding_vector[:5])}...")
                facial_area = result["facial_area"]
                x = facial_area["x"]
                y = facial_area["y"]
                width = facial_area["w"]
                height = facial_area["h"]
                
                # Draw the bounding box instantly to provide immediate visual feedback
                self.detected_faces = [{'name': 'Analyzing...', 'x': x, 'y': y, 'width': width, 'height': height, 'timestamp': current_time}]
                
                try:
                    response = requests.post(API_UPDATE_STATUS, json={"vector": embedding_vector}, timeout=5)
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        if response_data.get("success"):
                            student_info = response_data.get("student", {})
                            student_id = student_info.get("student_code") or student_info.get("id", "Unknown")
                            student_name = student_info.get("name", student_id)
                            
                            self.detected_faces = [{'name': student_name, 'x': x, 'y': y, 'width': width, 'height': height, 'timestamp': current_time}]
                            
                            # Apply a cooldown to avoid spamming successful logs for the same student
                            if student_id not in self.last_recognition_timestamps or (current_time - self.last_recognition_timestamps[student_id]) > COOLDOWN_SECONDS:
                                self.last_recognition_timestamps[student_id] = current_time
                                self.root.after(0, self.log, f"Attendance marked for: {student_name} ({student_id})")
                                
                                self.liveness_passed = False
                                self.eyes_were_open = False
                except requests.exceptions.RequestException:
                    pass

        except ValueError:
            # DeepFace.represent raises ValueError if no face is detected; safely catch to continue video stream
            pass
        except Exception as error:
            print(f"[Debug] DeepFace Error: {error}")
        finally:
            self.is_processing_frame = False

    def open_enrollment_dialog(self):
        if not self.is_camera_running:
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Enroll Student")
        dialog.geometry("300x250")
        
        tk.Label(dialog, text="Student Code:").pack(pady=2)
        code_entry = tk.Entry(dialog)
        code_entry.pack(pady=2)
        
        tk.Label(dialog, text="Full Name:").pack(pady=2)
        name_entry = tk.Entry(dialog)
        name_entry.pack(pady=2)
        
        tk.Label(dialog, text="Class Name:").pack(pady=2)
        class_entry = tk.Entry(dialog)
        class_entry.pack(pady=2)
        
        tk.Label(dialog, text="School:").pack(pady=2)
        school_entry = tk.Entry(dialog)
        school_entry.pack(pady=2)
        
        def submit_enrollment():
            student_code = code_entry.get().strip()
            name = name_entry.get().strip()
            class_name = class_entry.get().strip()
            school = school_entry.get().strip()
            
            if not all([student_code, name, class_name, school]):
                messagebox.showerror("Validation", "All fields are required.")
                return

            success, fresh_frame = self.camera_capture.read()
            if not success:
                messagebox.showerror("Error", "Could not capture frame from camera.")
                return
                
            self.log(f"Enrolling {name} to database...")
            
            try:
                # Synchronously extract vector for enrollment from the freshest frame
                results = DeepFace.represent(img_path=fresh_frame, model_name="Facenet512", enforce_detection=True, detector_backend="mtcnn", anti_spoofing=True)
                
                if not results[0].get("is_real", True):
                    messagebox.showerror("Security Alert", "Fake face detected! Enrollment blocked.")
                    return
                    
                vector = results[0]["embedding"]
                
                payload = {
                    "student_code": student_code,
                    "name": name,
                    "class_name": class_name,
                    "school": school,
                    "status": "absent",
                    "face_vector": vector
                }
                
                headers = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                }
                
                response = requests.post(SUPABASE_URL, headers=headers, json=payload, timeout=10)
                
                if response.status_code in [200, 201]:
                    self.log(f"Success: {name} enrolled in database.")
                    dialog.destroy()
                else:
                    self.log(f"Enrollment Error: {response.text}")
                    messagebox.showerror("API Error", f"Failed to save to Supabase: {response.status_code}")
                    
            except ValueError:
                messagebox.showerror("Error", "No face detected in the captured frame. Try again.")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")

        tk.Button(dialog, text="Capture & Save", command=submit_enrollment, bg="blue", fg="white").pack(pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
