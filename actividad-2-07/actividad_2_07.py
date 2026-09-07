import cv2
import numpy as np
import glob

CHESSBOARD_SIZE = (5, 7)

criteria = (
    cv2.TERM_CRITERIA_EPS +
    cv2.TERM_CRITERIA_MAX_ITER,
    30,
    0.001
)

objp = np.zeros(
    (CHESSBOARD_SIZE[0] * CHESSBOARD_SIZE[1], 3),
    np.float32
)

objp[:, :2] = np.mgrid[
    0:CHESSBOARD_SIZE[0],
    0:CHESSBOARD_SIZE[1]
].T.reshape(-1, 2)

#Lista para guardar puntos
objpoints = []
imgpoints = []


images = glob.glob("calibration_images1/*.jpg")
print(f"\nSe encontraron {len(images)} imagenes\n")


for fname in images:

    print(f"Procesando: {fname}")
    img = cv2.imread(fname)

    if img is None:
        print("No se pudo abrir la imagen")
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #Detecta tablero
    ret, corners = cv2.findChessboardCorners(
        gray,
        CHESSBOARD_SIZE,
        None
    )

    if ret:

        print("Tablero detectado")

        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(
            gray,
            corners,
            (11, 11),
            (-1, -1),
            criteria
        )

        imgpoints.append(corners2)

        #Dibujar esquinas
        cv2.drawChessboardCorners(
            img,
            CHESSBOARD_SIZE,
            corners2,
            ret
        )

        cv2.imshow("Corners", img)
        cv2.waitKey(500)

    else:
        print("No se detecto el tablero")

cv2.destroyAllWindows()

if len(objpoints) == 0:

    print("\nERROR: No se detectaron tableros\n")
    exit()

#Calibracion
print("\nCalibrando camara...\n")

ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints,
    imgpoints,
    gray.shape[::-1],
    None,
    None
)

print("===================================")
print("MATRIZ K")
print("===================================\n")
print(K)

print("\n===================================")
print("PARAMETROS DE DISTORSION")
print("===================================\n")
print(dist)

#Remover distorcion
test_img = cv2.imread(images[0])
h, w = test_img.shape[:2]

newK, roi = cv2.getOptimalNewCameraMatrix(
    K,
    dist,
    (w, h),
    1,
    (w, h)
)

undistorted = cv2.undistort(
    test_img,
    K,
    dist,
    None,
    newK
)

#Muestra y guarda imagenes
cv2.imshow("Original", test_img)
cv2.imshow("Undistorted", undistorted)
cv2.imwrite("img_original.jpg", test_img)
cv2.imwrite("img_undistorted.jpg", undistorted)

print("\nPresiona cualquier tecla para salir...\n")

cv2.waitKey(0)
cv2.destroyAllWindows()
