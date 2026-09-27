import cv2
import time
import requests
import os
import json
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from deepface import DeepFace

DATASET_DIR = "dataset/"
API_UPDATE_STATUS = ""
COOLDOWN_SECONDS = 5

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("face attendance gui")
        
        self.cap = None
        self.running = False
        self.last_rec_time = {}
        self.is_processing = False
        self.current_boxes = [] # Lưu tọa độ khung mặt để vẽ
        
        # gui widgets
        self.lbl = tk.Label(root, text="select cam:")
        self.lbl.pack(pady=5)
        
        self.combo = ttk.Combobox(root)
        self.combo.pack(pady=5)
        
        self.btn = tk.Button(root, text="start", command=self.toggle, width=20)
        self.btn.pack(pady=5)
        
        self.video = tk.Label(root)
        self.video.pack(pady=5)
        
        self.log_txt = tk.Text(root, height=12, width=60)
        self.log_txt.pack(pady=5)
        
        # check dataset folder
        if not os.path.exists(DATASET_DIR):
            os.makedirs(DATASET_DIR, exist_ok=True)
            self.log("no dataset folder. created. put pics in there.")
            
        # detect cams
        self.log("scanning for cams...")
        cams = []
        for i in range(5):
            cap = cv2.VideoCapture(i) # bo dshow vi hay gay nhieng hinh voi cam ao
            if cap.isOpened():
                cams.append(str(i))
                cap.release()
        
        if cams:
            self.combo['values'] = cams
            self.combo.current(0)
            self.log(f"found cams: {cams}")
        else:
            self.log("no cams found")
            
    def log(self, text):
        self.log_txt.insert(tk.END, text + "\n")
        self.log_txt.see(tk.END)
        print(text)
        
    def toggle(self):
        if self.running:
            self.running = False
            self.btn.config(text="start")
            if self.cap:
                self.cap.release()
            self.video.config(image='')
            self.log("stopped.")
        else:
            val = self.combo.get()
            if val.isdigit():
                self.cap = cv2.VideoCapture(int(val))
            else:
                self.cap = cv2.VideoCapture(val)
                
            if not self.cap.isOpened():
                self.log("err: cant open cam")
                return
                
            self.running = True
            self.btn.config(text="stop")
            self.log("started. looking for faces...")
            self.update_video()
            
    def update_video(self):
        if not self.running: return
        
        ret, frame = self.cap.read()
        if ret:
            # Vẽ khung xanh xung quanh mặt (giữ khung trong 2 giây)
            self.current_boxes = [b for b in self.current_boxes if time.time() - b['time'] < 2]
            for b in self.current_boxes:
                cv2.rectangle(frame, (b['x'], b['y']), (b['x']+b['w'], b['y']+b['h']), (0, 255, 0), 2)
                cv2.putText(frame, b['name'], (b['x'], b['y']-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # show video
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video.imgtk = imgtk
            self.video.configure(image=imgtk)
            
            # run face rec in background thread (ko lag gui)
            if not self.is_processing:
                self.is_processing = True
                threading.Thread(target=self.recognize, args=(frame.copy(),), daemon=True).start()
                
        self.root.after(30, self.update_video)
        
    def recognize(self, frame):
        try:
            dfs = DeepFace.find(img_path=frame, db_path=DATASET_DIR, enforce_detection=False, silent=True, detector_backend="mtcnn")
            if dfs and not dfs[0].empty:
                best_match_row = dfs[0].iloc[0]
                match = best_match_row['identity']
                student_id = os.path.splitext(os.path.basename(match))[0]
                
                # Trích xuất khung mặt để vẽ
                if 'source_x' in best_match_row:
                    x = int(best_match_row['source_x'])
                    y = int(best_match_row['source_y'])
                    w = int(best_match_row['source_w'])
                    h = int(best_match_row['source_h'])
                    self.current_boxes = [{'name': student_id, 'x': x, 'y': y, 'w': w, 'h': h, 'time': time.time()}]
                
                now = time.time()
                if student_id not in self.last_rec_time or (now - self.last_rec_time[student_id]) > COOLDOWN_SECONDS:
                    self.last_rec_time[student_id] = now
                    self.root.after(0, self.log, f"success: {student_id}")
                    
                    data = {"student_id": student_id, "status": "present"}
                    if API_UPDATE_STATUS:
                        try:
                            requests.post(API_UPDATE_STATUS, json=data, timeout=5)
                            self.root.after(0, self.log, "api ok")
                        except Exception as e:
                            self.root.after(0, self.log, f"api err: {e}")
                    else:
                        self.root.after(0, self.log, f"mock post: {data}")
        except Exception as e:
            print(f"[Debug] Lỗi DeepFace: {e}")
        finally:
            self.is_processing = False

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
