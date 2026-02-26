import pickle
# U
import cv2
import mediapipe as mp
import numpy as np

model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=False,max_num_hands=1, min_detection_confidence=0.3)

labels_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I',
                9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R',
                  18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z'}
while True:

    data_aux = []
    x_ = []
    y_ = []

    ret, frame = cap.read()

    H, W, _ = frame.shape

    # Calque pour les effets de lumière néon
    overlay = np.zeros((H, W, 3), dtype=np.uint8)

    frame = cv2.flip(frame, 1)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]

        for hand_landmarks in results.multi_hand_landmarks:
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y

                x_.append(x)
                y_.append(y)

            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

        x1, y1 = int(min(x_) * W) - 20, int(min(y_) * H) - 20
        x2, y2 = int(max(x_) * W) + 20, int(max(y_) * H) + 20

        # Points néons (Glow)
        for i in range(len(hand_landmarks.landmark)):
            cx, cy = int(hand_landmarks.landmark[i].x * W), int(hand_landmarks.landmark[i].y * H)
            cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)
            cv2.circle(overlay, (cx, cy), 8, (0, 255, 0), -1)

        # Coins de visée Cyan
        l = 25
        cv2.line(frame, (x1, y1), (x1+l, y1), (0, 255, 255), 2)
        cv2.line(frame, (x1, y1), (x1, y1+l), (0, 255, 255), 2)
        cv2.line(frame, (x2, y2), (x2-l, y2), (0, 255, 255), 2)
        cv2.line(frame, (x2, y2), (x2, y2-l), (0, 255, 255), 2)

        prediction = model.predict([np.asarray(data_aux)])

        predicted_character = labels_dict[int(prediction)]

        # Étiquette de détection
        cv2.rectangle(overlay, (x1, y1 - 40), (x2, y1), (0, 0, 0), -1)
        cv2.putText(frame, f"ANALYSIS: {predicted_character}", (x1 + 5, y1 - 12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
    # Fusion des calques
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

    # Barre système
    cv2.rectangle(frame, (0, H-30), (W, H), (10, 10, 10), -1)
    cv2.putText(frame, "AETHER_HUD ACTIVE // NO_DELAY_SHUTDOWN_ENABLED", (15, H-10), 
                cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)

    cv2.imshow('frame', frame)
    cv2.waitKey(1)

    if cv2.getWindowProperty('frame', cv2.WND_PROP_VISIBLE) < 1:
        break

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == 27: break
    


# je veux ajouter que lorsque je fait une sign avec mes mains le programme s'arrete automatiquement , comme ça on resoudre ce probléme , que il ne s'arrete pas 
cap.release()
cv2.destroyAllWindows()