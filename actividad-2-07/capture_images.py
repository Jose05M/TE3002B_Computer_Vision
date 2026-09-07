#!/usr/bin/env python3

# ============================================================
# PUZZLEBOT CAMERA CAPTURE NODE
# ============================================================
#
# FUNCIONAMIENTO:
#
# - Recibe imagen desde ROS2
# - Muestra video en vivo
# - Presiona:
#
#     s -> guardar imagen
#     q -> salir
#
# Las imágenes se guardan en:
#
# calibration_images/
#
# ============================================================

import os
import cv2
import numpy as np
import rclpy

from rclpy.node import Node
from sensor_msgs.msg import Image


class PuzzlebotCameraCapture(Node):

    def __init__(self):

        super().__init__("puzzlebot_camera_capture")

        # ====================================================
        # PARAMETROS
        # ====================================================

        self.declare_parameter(
            "image_topic",
            "/video_source/raw"
        )

        self.image_topic = self.get_parameter(
            "image_topic"
        ).value

        # ====================================================
        # CARPETA DE GUARDADO
        # ====================================================

        self.save_path = "calibration_images"

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        self.image_count = 0

        # ====================================================
        # SUBSCRIBER
        # ====================================================

        self.image_sub = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            10
        )

        # ====================================================
        # INFO
        # ====================================================

        self.get_logger().info("===================================")
        self.get_logger().info("PUZZLEBOT CAMERA CAPTURE")
        self.get_logger().info("===================================")
        self.get_logger().info("PUZZLEBOT CAMERA CAPTURE NODE")
        self.get_logger().info("===================================")
        self.get_logger().info(f"Topic: {self.image_topic}")
        self.get_logger().info("")
        self.get_logger().info("Teclas:")
        self.get_logger().info("s -> guardar imagen")
        self.get_logger().info("q -> salir")
        self.get_logger().info("===================================")

    # ========================================================
    # CALLBACK DE IMAGEN
    # ========================================================

    def image_callback(self, msg):

        # ====================================================
        # ROS IMAGE -> OPENCV
        # ====================================================

        frame = np.frombuffer(
            msg.data,
            dtype=np.uint8
        )

        frame = frame.reshape(
            (msg.height, msg.width, 3)
        )

        # ====================================================
        # SI TU CAMARA SE VE ESPEJEADA
        # DEJA ESTA LINEA
        #
        # SI NO, COMENTALA
        # ====================================================

        frame1 = cv2.flip(frame, 1)
        frame = cv2.flip(frame, 1)

        # ====================================================
        # TEXTO EN PANTALLA
        # ====================================================

        cv2.putText(
            frame,
            "Press S to save image",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "Press Q to quit",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Saved images: {self.image_count}",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        # ====================================================
        # MOSTRAR IMAGEN
        # ====================================================

        cv2.imshow(
            "Puzzlebot Camera",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        # ====================================================
        # GUARDAR IMAGEN
        # ====================================================

        if key == ord("s"):

            filename = (
                f"{self.save_path}/"
                f"img_{self.image_count:03d}.jpg"
            )

            cv2.imwrite(filename, frame1)

            self.get_logger().info(
                f"Imagen guardada: {filename}"
            )

            self.image_count += 1

        # ====================================================
        # SALIR
        # ====================================================

        elif key == ord("q"):

            self.get_logger().info(
                "Cerrando nodo..."
            )

            cv2.destroyAllWindows()

            rclpy.shutdown()

    # ========================================================
    # DESTROY
    # ========================================================

    def destroy_node(self):

        cv2.destroyAllWindows()

        super().destroy_node()


# ============================================================
# MAIN
# ============================================================

def main(args=None):

    rclpy.init(args=args)

    node = PuzzlebotCameraCapture()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()