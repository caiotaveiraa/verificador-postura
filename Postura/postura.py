import cv2
import mediapipe as mp
import numpy as np
import math

# Inicializa o módulo de pose do MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils  # Utilitário para desenhar os landmarks

# Abre a webcam padrão (índice 0)
cap = cv2.VideoCapture(0)

while True:
    # Captura um frame da webcam
    ret, frame = cap.read()
    if not ret:  # Se não conseguir capturar, sai do loop
        break

    # Converte a imagem para RGB (formato esperado pelo MediaPipe)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Processa o frame para detectar os landmarks da pose
    results = pose.process(frame_rgb)

    # Se algum ponto da pose foi detectado
    if results.pose_landmarks:
        h, w = frame.shape[:2]  # Altura e largura da imagem
        lm = results.pose_landmarks.landmark  # Lista dos landmarks detectados

        # Pega as coordenadas do nariz, ombro esquerdo e direito (convertendo para pixels)
        nose = np.array([lm[mp_pose.PoseLandmark.NOSE].x * w, lm[mp_pose.PoseLandmark.NOSE].y * h])
        left_shoulder = np.array([lm[mp_pose.PoseLandmark.LEFT_SHOULDER].x * w, lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y * h])
        right_shoulder = np.array([lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w, lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h])

        # Cria vetores do nariz para os ombros
        vec_left = left_shoulder - nose
        vec_right = right_shoulder - nose

        # Calcula o cosseno do ângulo entre os vetores
        cos_theta = np.dot(vec_left, vec_right) / (np.linalg.norm(vec_left) * np.linalg.norm(vec_right) + 1e-7)
        cos_theta = np.clip(cos_theta, -1, 1)  # Limita para evitar erros numéricos
        angle = math.degrees(math.acos(cos_theta))  # Converte o ângulo para graus

        # Define cor e texto baseados no ângulo para indicar postura
        color = (0, 255, 0)  # Verde para postura OK
        text = f"Postura OK - Angulo: {int(angle)}"
        if angle > 90:  # Se ângulo maior que 90, considera postura ruim
            color = (0, 0, 255)  # Vermelho
            text = f"Postura Ruim! Angulo: {int(angle)}"

        # Mostra o texto na imagem
        cv2.putText(frame, text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        # Desenha círculos nos pontos do nariz e ombros
        cv2.circle(frame, tuple(nose.astype(int)), 7, (255, 0, 0), -1)
        cv2.circle(frame, tuple(left_shoulder.astype(int)), 7, (255, 0, 0), -1)
        cv2.circle(frame, tuple(right_shoulder.astype(int)), 7, (255, 0, 0), -1)
        # Desenha linhas ligando o nariz aos ombros
        cv2.line(frame, tuple(nose.astype(int)), tuple(left_shoulder.astype(int)), (255, 255, 0), 2)
        cv2.line(frame, tuple(nose.astype(int)), tuple(right_shoulder.astype(int)), (255, 255, 0), 2)

        # Desenha todos os landmarks da pose na imagem
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Mostra o frame com as anotações numa janela
    cv2.imshow('Postura com angulo - MediaPipe', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Libera a webcam e fecha todas as janelas ao sair do loop
cap.release()
cv2.destroyAllWindows()