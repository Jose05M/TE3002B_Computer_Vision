import time
import sys
import math
import numpy as np
import cv2
sys.path.append('/home/ed/Documents/CoppeliaSim/programming/zmqRemoteApi/clients/python/src')
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

class OrangeDetector:
    def __init__(self):
        """
        Inicializa la conexión con CoppeliaSim y configura el sensor de visión.
        """
        # Conexión con CoppeliaSim
        self.client = RemoteAPIClient()
        self.sim = self.client.getObject('sim')

        # Obtener el handle del sensor de visión
        self.sensor1Handle = self.sim.getObject('/Vision_sensor')
        self.sim.startSimulation()
        time.sleep(1)

    def capture_image(self):
        """
        Captura una imagen desde el sensor de visión de CoppeliaSim.
        :return: Imagen en formato OpenCV (BGR) o None si no se pudo capturar.
        """
        try:
            img, [resX, resY] = self.sim.getVisionSensorImg(self.sensor1Handle)
            img = np.frombuffer(img, dtype=np.uint8).reshape(resY, resX, 3)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            img = cv2.flip(img, 0)
            return img
        
        except Exception as e:
            print(f"eror al capturar imagen: {e}")
            return None

    def detect_orange_object(self, img):
        """
        Detecta el objeto naranja en la imagen y devuelve las coordenadas del mejor candidato.
        :param img: Imagen en formato OpenCV (BGR).
        :return: Coordenadas del centroide (cx, cy) del mejor candidato o None si no se detecta.
        """
        best_candidate = None
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower_orange = np.array([0, 80, 50])
        upper_orange = np.array([20, 255, 255])

        mask = cv2.inRange(hsv, lower_orange, upper_orange)
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 50:
                moments = cv2.moments(largest_contour)
                if moments["m00"] != 0:
                    cx = int(moments["m10"] / moments["m00"])
                    cy = int(moments["m01"] / moments["m00"])
                    best_candidate = (cx, cy)
                else:
                    print("No se puede calcular el centroide.")

        return best_candidate

    def run(self):
        """
        Ejecuta el detector en un bucle continuo.
        """
        while True:
            # Capturar la imagen desde el sensor de visión
            img = self.capture_image()

            if img is not None:
                # Detectar el objeto naranja y obtener el mejor candidato
                best_candidate = self.detect_orange_object(img)

                if best_candidate:
                    print(f"Mejor centroide detectado en: {best_candidate}")
                else:
                    print("No se detectó ningún objeto naranja.")

if __name__ == "__main__":
    detector = OrangeDetector()
    detector.run()