import cv2
import mediapipe as mp
import math
import random as rd 
import time
from vpython import * # ==========================================
# 1. VISUAL SETUP (IMMERSIVE DIVE V.45)
# ==========================================
scene.title = """
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&display=swap" rel="stylesheet">
<style>
    body { margin: 0; padding: 0; background-color: #000; overflow: hidden; }
    .hud-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100px; z-index: 9999;
        background: linear-gradient(to bottom, rgba(0,10,20,0.9) 0%, rgba(0,0,0,0) 100%);
        text-align: center; font-family: 'Orbitron', sans-serif; color: #0ff;
        pointer-events: none;
    }
    h1 { margin-top: 15px; font-size: 2em; letter-spacing: 4px; text-shadow: 0 0 15px #0ff; opacity: 1.0; }
    .status-bar { font-size: 0.7em; color: #8ff; opacity: 0.8; letter-spacing: 2px; margin-top: 5px; }
    .highlight { color: #fff; font-weight: bold; }
</style>
<div class="hud-overlay">
    <h1>AETHER <span style="font-size:0.5em; color:white;">DIVE v.45</span></h1>
    <div class="status-bar">ACTION: <span class="highlight">CAMERA DIVE</span> // TRACKING: <span class="highlight">ACTIVE</span></div>
</div>
"""

scene.background = color.black
scene.width = 1400 
scene.height = 800 
scene.autoscale = False    
scene.userzoom = False     
scene.userspin = False     
scene.userpan = False      
scene.fov = 1.2 # FOV Lebar untuk efek kecepatan
scene.lights = [] 

# ==========================================
# 2. SISTEM 2000 PARTIKEL (FIBONACCI CLOUD)
# ==========================================
print("Membangun Dunia Partikel...")

N_PARTIKEL = 2000 # Jumlah banyak agar saat masuk tetap ramai
partikel_list = []
posisi_rumah_list = [] 
offset_wave = []       

phi = math.pi * (3. - math.sqrt(5.)) 

for i in range(N_PARTIKEL):
    y = 1 - (i / float(N_PARTIKEL - 1)) * 2 
    radius = math.sqrt(1 - y * y)
    theta = phi * i 
    
    x = math.cos(theta) * radius
    z = math.sin(theta) * radius
    
    # Radius Dasar cukup besar (6.0) agar ruangannya lega saat kita masuk
    r_base = 6.0 
    
    if i % 2 == 0:
        r_final = r_base + rd.uniform(-1, 1) # Variasi kedalaman
        c_final = vector(0, 1, 1) # Cyan
    else:
        r_final = (r_base * 1.2) + rd.uniform(-1, 1)
        c_final = vector(0.6, 0, 1) # Purple
        
    home_pos = vector(x * r_final, y * r_final, z * r_final)
    posisi_rumah_list.append(home_pos)
    offset_wave.append(rd.uniform(0, 10))
    
    # Radius 0.05 (Sedikit lebih besar biar jelas saat lewat depan muka)
    p = sphere(pos=home_pos, radius=0.05, color=c_final, 
               emissive=True, shininess=0) 
    partikel_list.append(p)

# ==========================================
# 3. LOGIKA KAMERA & TRACKING
# ==========================================
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, 
                       min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

# Variabel Animasi
rotasi_global = 0.0
expansion_value = 0.0 

# Variabel Kamera (KUNCI DIVE)
current_cam_z = 25.0
target_cam_z = 25.0

# Variabel Tangan
hand_pos_x = 0.0
hand_pos_y = 0.0
target_pos_x = 0.0
target_pos_y = 0.0

print("SISTEM SIAP.")
print("- BUKA TANGAN LEBAR = TERBANG MASUK (DIVE)")
print("- GESER JARI = PINDAHKAN POSISI")

while True:
    rate(45) 
    rotasi_global += 0.005
    waktu = time.time()
    
    # --- PROSES SMOOTHING ---
    
    # 1. Camera Dive (Gerakan Kamera Maju Mundur)
    # Ini kuncinya: Kamera bergerak fisik dari Z=25 ke Z=2
    current_cam_z = current_cam_z + (target_cam_z - current_cam_z) * 0.08
    scene.camera.pos = vector(0, 0, current_cam_z)
    
    # 2. Motion Tracking (Posisi Bola)
    hand_pos_x = hand_pos_x + (target_pos_x - hand_pos_x) * 0.1
    hand_pos_y = hand_pos_y + (target_pos_y - hand_pos_y) * 0.1
    move_offset = vector(hand_pos_x, hand_pos_y, 0)
    
    # 3. Expansion (Partikel Mekar sedikit saat kita masuk)
    target_expansion = 1.0 if target_cam_z < 10.0 else 0.0
    expansion_value = expansion_value + (target_expansion - expansion_value) * 0.1

    # --- UPDATE POSISI PARTIKEL ---
    for i in range(N_PARTIKEL):
        p = partikel_list[i]
        home = posisi_rumah_list[i]
        
        # A. Rotasi Global
        base_pos = home.rotate(angle=rotasi_global, axis=vector(0,1,0))
        
        # B. Efek Bernapas & Mekar
        # Saat kita masuk (expansion tinggi), partikel menyebar agar tidak menabrak kamera
        breath = math.sin(waktu * 2 + offset_wave[i]) * 0.1
        arah_keluar = norm(base_pos)
        dist_expand = expansion_value * 5.0 # Mekar 5 meter
        
        # C. Gabungkan Posisi + Offset Tangan
        # Perhatikan: Move Offset ikut digeser, jadi bola-nya pindah
        final_pos = (base_pos + (arah_keluar * (breath + dist_expand))) + move_offset
        
        p.pos = final_pos
        
        # D. Efek Warna Jarak Jauh vs Dekat
        # Saat kamera dekat (Z < 10), partikel jadi lebih terang (Putih)
        if current_cam_z < 10.0:
             # Hitung jarak partikel ke kamera
             dist_to_cam = mag(p.pos - scene.camera.pos)
             if dist_to_cam < 5.0: # Jika sangat dekat dengan muka
                 p.color = vector(1, 1, 1) # Putih silau
             else:
                 p.color = vector(0, 1, 1) if i % 2 == 0 else vector(0.6, 0, 1)
        else:
             p.color = vector(0, 1, 1) if i % 2 == 0 else vector(0.6, 0, 1)

    # --- INPUT TANGAN ---
    success, img = cap.read()
    if not success: break
    img = cv2.flip(img, 1) 
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    hand_detected = False
    
    if results.multi_hand_landmarks:
        hand_detected = True
        for hand_landmarks in results.multi_hand_landmarks:
            thumb = hand_landmarks.landmark[4]
            index = hand_landmarks.landmark[8]
            
            # Hitung Jarak Cubit
            jarak = math.sqrt((thumb.x - index.x)**2 + (thumb.y - index.y)**2 + (thumb.z - index.z)**2)
            
            # === LOGIKA DIVE (TERBANG MASUK) ===
            # Buka Tangan (> 0.15) = Kamera Maju ke Z=2.0 (Masuk ke dalam)
            # Cubit (< 0.15)       = Kamera Mundur ke Z=28.0 (Lihat dari jauh)
            if jarak > 0.15:
                target_cam_z = 2.0 
            else:
                target_cam_z = 28.0
            
            # === LOGIKA MOTION (GESER) ===
            target_pos_x = (index.x - 0.5) * 30.0 # Multiplier besar agar jangkauan luas
            target_pos_y = (0.5 - index.y) * 20.0
            
            # Visualisasi
            cx, cy = int(index.x * 640), int(index.y * 480)
            color_ind = (0, 255, 0) if jarak > 0.15 else (0, 0, 255)
            cv2.circle(img, (cx, cy), 15, color_ind, 2)
            cv2.line(img, (320, 240), (cx, cy), color_ind, 1)

    if not hand_detected:
        target_cam_z = 28.0 # Auto mundur jika tangan hilang
        target_pos_x = 0.0
        target_pos_y = 0.0

    # Tampilan Kamera
    cv2.rectangle(img, (0,0), (640, 480), (200, 200, 0), 1)
    status = "MODE: DIVING INSIDE" if target_cam_z < 10 else "MODE: ORBIT VIEW"
    cv2.putText(img, status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 255, 0), 2)
    
    cv2.imshow("Cam", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()