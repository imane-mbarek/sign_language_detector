import os      #nous permet de lire les images et d'écrire texte sur la vidéo 
import cv2     #c'est l'utile qui permet à python de parler avec l'ordinateur 

DATA_DIR="./data"

if not os.path.exists(DATA_DIR):     #si le dossier data n'existe pas, on le crée
    os.makedirs(DATA_DIR)
 
num_classes=3
dataset_size=100

cap=cv2.VideoCapture(0)  #on ouvre la caméra 
for j in range(num_classes):       #pour chaque classe
    if not os.path.exists(os.path.join(DATA_DIR, str(j))):       #si le dossier de la classe n'existe pas 
        os.makedirs(os.path.join(DATA_DIR, str(j)))           #on le crée

    print('Collecting data for class {}'.format(j))

    done=False
    while True:   
        ret, frame=cap.read() #on lit la caméra 
        cv2.putText(frame, 'ready? press "Q"! :)', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255,0), 3, cv2.LINE_AA) #on écrit le texte sur la vidéo
        cv2.imshow('frame', frame)  #on affiche la vidéo
        if cv2.waitKey(25)==ord('q')   :  #si on appuie sur 'q', on sort de la boucle
            break

    counter=0
    while counter<dataset_size:
        ret, frame=cap.read()
        cv2.imshow('frame', frame) 
        cv2.waitKey(25)
        cv2.imwrite(os.path.join(DATA_DIR, str(j), '{}.jpg'.format(counter)), frame)
        counter+=1

cap.release()  #on libère la caméra
cv2.destroyAllWindows()  #on ferme la fenêtre de la vidéo