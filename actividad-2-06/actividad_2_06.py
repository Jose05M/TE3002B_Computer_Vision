# PIPELINE
# Este sistema implementa un pipeline híbrido para la detección de señales de tráfico
# utilizando dos enfoques principales: una red neuronal convolucional (YOLO) y una
# métrica de similitud estructural (SSIM).
#
# 1. Captura de imagen:
#    Se obtiene cada frame desde un video o simulador y se ajusta su tamaño.
# 2. Detección con YOLO (CNN):
#    Se utiliza un modelo previamente entrenado para detectar las señales de tráfico
#    (STOP, WORKERS, LEFT, RIGHT, STRAIGHT) y obtener sus bounding boxes y confianza.
# 3. Filtrado básico:
#    Se descartan detecciones muy pequeñas para reducir ruido y falsos positivos.
# 4. Validación con SSIM:
#    Para cada región detectada (ROI), se calcula la similitud estructural con una
#    plantilla correspondiente. Este valor no elimina detecciones, sino que apoya
#    la decisión final.
# 5. Fusión de información:
#    Se calcula un puntaje combinado que considera:
#       - la confianza de YOLO (principal)
#       - la similitud SSIM (validación)
#       - el área del objeto (aproximación de cercanía)
# 6. Selección de señal al frente:
#    Se selecciona la señal con mayor puntaje final, interpretándola como la más
#    relevante o más cercana al vehículo.
# 7. Visualización:
#    Se dibujan las detecciones y se muestra en pantalla la señal que se encuentra
#    al frente en tiempo real.
# En el siguiente enlace se encutran los el dataset con el cual se entreno YOLO y los templates para el SSIM asi como los videos
# Enlace: https://drive.google.com/drive/folders/1d7FpIBrH8n6VqHO5EmIznrZjPG7roXxg?usp=sharing

from ultralytics import YOLO
import cv2
from skimage.metrics import structural_similarity as ssim

model = YOLO("dataset/runs/detect/train/weights/best.pt")

templates = {
    "STOP": cv2.imread("template/stop.jpeg"),
    "WORKERS": cv2.imread("template/workers.jpeg"),
    "LEFT": cv2.imread("template/turn_left.jpeg"),
    "RIGHT": cv2.imread("template/turn_right.jpeg"),
    "STRAIGHT": cv2.imread("template/straight.jpeg")
}
def compute_ssim(img1, img2):
    img1 = cv2.resize(img1, (100, 100))
    img2 = cv2.resize(img2, (100, 100))
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    score, _ = ssim(gray1, gray2, full=True)
    return score

cap = cv2.VideoCapture("video.mp4")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 30, (640, 480))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))

    # Con conf=0.3 se logra detectar todas las señales, aunque tambien detecta ruido (detecta señales fantasma)
    # Con conf > 0.6 se elimina la mayoria de ruido, pero se sacrifica la deteccion de señales que estan muy lejos, ej. la señal de straight
    results = model(frame, conf=0.3, imgsz=640)

    best_label = None
    best_score = 0

    for r in results:
        for box in r.boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = model.names[cls]

            w = x2 - x1
            h = y2 - y1
            area = w * h

            if area < 400:
                continue

            roi = frame[y1:y2, x1:x2]
            if roi.size == 0:
                continue

            ssim_score = 0

            if label in templates and templates[label] is not None:
                ssim_score = compute_ssim(roi, templates[label])

            final_score = (0.6 * conf) + (0.3 * ssim_score) + (0.001 * area)


            if final_score > best_score:
                best_score = final_score
                best_label = label

            color = (0,255,0)
            if label == "STOP":
                color = (0,0,255)
            elif label == "LEFT":
                color = (255,0,0)
            elif label == "RIGHT":
                color = (255,255,0)
            elif label == "STRAIGHT":
                color = (0,255,255)
            elif label == "WORKERS":
                color = (255,0,255)

            #Escribe sobre el video
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame,
                        f"{label} ({conf:.2f} | s:{ssim_score:.2f})",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, color, 2)

    #Muestra lo que esta enfrente
    if best_label is not None:
        cv2.putText(frame,
                    f"FRONT: {best_label}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0,255,0), 3)
    out.write(frame)
    cv2.imshow("Detection", frame)

    if cv2.waitKey(30) & 0xFF == 27:
        break

cap.release()
out.release()
cv2.destroyAllWindows()