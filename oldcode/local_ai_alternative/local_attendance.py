import os
import cv2
import time
import pickle
import numpy as np
from datetime import datetime
from deepface import DeepFace

DATASET_DIR = "dataset"
EMBEDDINGS_FILE = "embeddings.pkl"
CSV_FILE = "diemdanh.csv"
THRESHOLD = 0.68

def cosine_distance(vec1, vec2):
    """Calculates cosine distance between two vectors."""
    a = np.array(vec1)
    b = np.array(vec2)
    return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def load_or_extract_embeddings():
    """Loads embeddings from pickle file or extracts them from dataset directory."""
    if os.path.exists(EMBEDDINGS_FILE):
        print(f"Loading embeddings from {EMBEDDINGS_FILE}...")
        try:
            with open(EMBEDDINGS_FILE, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading pickle file: {e}")
            return {}
            
    print(f"Extracting embeddings from {DATASET_DIR}...")
    db = {}
    
    if not os.path.exists(DATASET_DIR):
        try:
            os.makedirs(DATASET_DIR)
            print(f"Created {DATASET_DIR}. Please add images (e.g., 'John_10A.jpg') and restart.")
        except Exception as e:
            print(f"Error creating dataset directory: {e}")
        return db

    for file in os.listdir(DATASET_DIR):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            name_class = os.path.splitext(file)[0]
            img_path = os.path.join(DATASET_DIR, file)
            try:
                reps = DeepFace.represent(img_path, model_name='ArcFace', enforce_detection=True)
                if reps and len(reps) > 0:
                    db[name_class] = reps[0]['embedding']
                    print(f"Successfully extracted: {name_class}")
            except Exception as e:
                print(f"Error extracting {file}: {e}")
                
    if db:
        try:
            with open(EMBEDDINGS_FILE, "wb") as f:
                pickle.dump(db, f)
            print("Embeddings saved to disk.")
        except Exception as e:
            print(f"Error saving pickle file: {e}")
        
    return db

def log_attendance(name_class, logged_today):
    """Logs the attendance to a CSV file."""
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")
    
    if name_class in logged_today and logged_today[name_class] == today:
        return
        
    parts = name_class.split('_')
    name = parts[0]
    student_class = parts[1] if len(parts) > 1 else "Unknown"
    
    file_exists = os.path.isfile(CSV_FILE)
    
    try:
        with open(CSV_FILE, "a", encoding="utf-8") as f:
            if not file_exists:
                f.write("Date,Time,Name,Class\n")
            f.write(f"{today},{now_time},{name},{student_class}\n")
        print(f"Logged attendance: {name} - Class: {student_class}")
        logged_today[name_class] = today
    except Exception as e:
        print(f"Error logging to CSV: {e}")

def main():
    db = load_or_extract_embeddings()
    if not db:
        print("No database loaded. Exiting.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam.")
        return

    print("Opening webcam... Press 'q' to exit.")
    
    logged_today = {}
    last_process_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Cannot read frame from webcam.")
            break

        cv2.imshow('Local Attendance System', frame)

        current_time = time.time()
        if current_time - last_process_time > 1:
            try:
                reps = DeepFace.represent(frame, model_name='ArcFace', enforce_detection=True)
                
                if reps:
                    for rep in reps:
                        target_emb = rep['embedding']
                        best_match = None
                        min_dist = float('inf')
                        
                        for name_class, db_emb in db.items():
                            dist = cosine_distance(target_emb, db_emb)
                            if dist < min_dist:
                                min_dist = dist
                                best_match = name_class
                                
                        if best_match and min_dist < THRESHOLD:
                            print(f"Match found: {best_match} (Distance: {min_dist:.2f})")
                            log_attendance(best_match, logged_today)
                        else:
                            print(f"Face detected but not recognized (Min distance: {min_dist:.2f}).")
                            
                last_process_time = current_time

            except ValueError:
                pass
            except Exception as e:
                print(f"Error during face processing: {e}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    try:
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error closing resources: {e}")

if __name__ == "__main__":
    main()
