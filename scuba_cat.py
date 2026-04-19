import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import time
import os


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# relax
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'hand_landmarker.task')
VIDEO_PATH = os.path.join(BASE_DIR, 'scuba.mp4')

print("--- RELAX SCUBA CODER V01 BASLATILIYOR ---")
print("Lutfen bekleyin, kamera birazdan acilacak (10-15 saniye surebilir)...")

try:
    
    base_options = mp.tasks.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1
    )
    detector = vision.HandLandmarker.create_from_options(options)

   
    cap = cv2.VideoCapture(0)
    scuba_video = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print("HATA: Kamera bulunamadı!")
        exit()
    if not scuba_video.isOpened():
        print(f"HATA: {VIDEO_PATH} bulunamadı!")
        exit()

    v_width = int(scuba_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    v_height = int(scuba_video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print("SISTEM AKTIF! Elinizi kameraya gosterin.")
    print("Kapatmak icin kamera ekranindayken 'q' tusuna basin.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        # Goruntuyu hazirla
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # El tespiti
        detection_result = detector.detect_for_video(mp_image, int(time.time() * 1000))
        
        hand_detected = False
        if detection_result.hand_landmarks:
            hand_detected = True
            # Skeleton Cizimi
            for hand_landmarks in detection_result.hand_landmarks:
                for landmark in hand_landmarks:
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        if hand_detected:
            v_ret, v_frame = scuba_video.read()
            if not v_ret:
                scuba_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                v_ret, v_frame = scuba_video.read()
            
            if v_ret:
                # Kameranin ve videonun boyutlarini al
                h, w, _ = frame.shape
                
                # Videoyu kameranin boyutuna gore olcekleyelim (Ekranin yarisi kadar)
                target_w = int(w * 0.5)
                scale_ratio = target_w / v_width
                target_h = int(v_height * scale_ratio)
                
                # Eger video kamerasindan yuksekse dikeyde kucult
                if target_h > h:
                    target_h = int(h * 0.8)
                    scale_ratio = target_h / v_height
                    target_w = int(v_width * scale_ratio)

                v_resized = cv2.resize(v_frame, (target_w, target_h))
                
                # Sola yasla (20px marj ile)
                x_off = 80
                y_off = (h - target_h) // 2
                
                # Bindirme
                frame[y_off:y_off+target_h, x_off:x_off+target_w] = v_resized
                cv2.putText(frame, "scubaa", (x_off, y_off-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            scuba_video.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # Ekrana bas
        cv2.imshow('Camera - scuba cat', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    detector.close()
    cap.release()
    scuba_video.release()
    cv2.destroyAllWindows()

except Exception as e:
    print(f"SISTEM HATASI: {e}")
    input("Devam etmek icin Enter'a basin...")
