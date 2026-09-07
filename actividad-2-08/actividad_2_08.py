# ACTIVIDAD 2.8
# Pipeline:
# 1. Cargar imágenes
# 2. Remover distorsión usando K, k1 y k2 obtenidos en 2.7
# 3. Detectar features con SIFT
# 4. Empatar features usando BFMatcher + KNN
# 5. Filtrar matches con Lowe Ratio Test
# 6. Calcular homografía usando RANSAC
# 7. Transformar esquinas con perspectiveTransform
# 8. Transformar la imagen con warpPerspective
# 9. Hacer stitching para formar panorama
#
# Funciones utilizadas:
# - cv2.undistort
# - cv2.SIFT_create
# - sift.detectAndCompute
# - cv2.BFMatcher
# - bf.knnMatch
# - cv2.findHomography
# - cv2.RANSAC
# - cv2.perspectiveTransform
# - cv2.warpPerspective
# ============================================================

import cv2
import numpy as np
import glob

# Matriz K y distorcion
K = np.array([
    [1.30487758e+03, 0.00000000e+00, 6.40220427e+02],
    [0.00000000e+00, 1.30484981e+03, 3.66430195e+02],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
], dtype=np.float32)

dist = np.array([
    [ 1.29594899e-01,
      2.16938764e-01,
      0,
      0,
      0]
], dtype=np.float32)

image_paths = sorted(glob.glob("panorama_images/*.jpg"))

for p in image_paths:
    print(p)

if len(image_paths) < 2:
    print("\nNecesita minimo 2 imagenes\n")
    exit()

#Leer primera imagen
panorama = cv2.imread(image_paths[0])

panorama = cv2.undistort(panorama,K,dist)

#Sift
sift = cv2.SIFT_create()

#Recorre resto de imagenes
for i in range(1, len(image_paths)):

    print("\n===================================")
    print(f"PROCESANDO {image_paths[i]}")
    print("===================================\n")

    #Carga nueva imagen
    new_image = cv2.imread(image_paths[i])

    new_image = cv2.undistort(new_image,K,dist)

    gray_panorama = cv2.cvtColor(panorama,cv2.COLOR_BGR2GRAY)

    gray_new = cv2.cvtColor(new_image,cv2.COLOR_BGR2GRAY)

    #sift.detectAndCompute
    kp1, des1 = sift.detectAndCompute(gray_panorama,None)
    kp2, des2 = sift.detectAndCompute(gray_new,None)

    print(f"Features panorama: {len(kp1)}")
    print(f"Features new image: {len(kp2)}")

    #cv2.BFMatcher
    bf = cv2.BFMatcher()

    #bf.knnMatch
    matches = bf.knnMatch(des1,des2,k=2)

    good_matches = []

    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    print(f"Good matches: {len(good_matches)}")

    #Dibuja matches
    match_img = cv2.drawMatches(panorama,kp1,new_image,kp2,good_matches,None,flags=2)

    cv2.imshow("Matches",match_img)
    cv2.waitKey(500)

    src_pts = np.float32([
        kp1[m.queryIdx].pt
        for m in good_matches
    ]).reshape(-1,1,2)

    dst_pts = np.float32([
        kp2[m.trainIdx].pt
        for m in good_matches
    ]).reshape(-1,1,2)

    #cv2.findHomography + cv2.RANSAC
    H, mask = cv2.findHomography(
        dst_pts,
        src_pts,
        cv2.RANSAC,
        5.0
    )
    print("\nHomografia:")
    print(H)

    # cv2.perspectiveTransform
    h1, w1 = panorama.shape[:2]
    h2, w2 = new_image.shape[:2]

    corners_img2 = np.float32([
        [0,0],
        [0,h2],
        [w2,h2],
        [w2,0]
    ]).reshape(-1,1,2)

    transformed_corners = cv2.perspectiveTransform(
        corners_img2,
        H
    )

    #cv2.warpPerspective
    warped = cv2.warpPerspective(new_image,H,(w1 + w2, max(h1, h2)))

    #Pegar panorama anterior
    for y in range(h1):
        for x in range(w1):
            if np.all(warped[y, x] == 0):
                warped[y, x] = panorama[y, x]

    gray_result = cv2.cvtColor(warped,cv2.COLOR_BGR2GRAY)

    coords = cv2.findNonZero(gray_result)
    x, y, w, h = cv2.boundingRect(coords)
    panorama = warped[y:y+h,x:x+w]


#Guarda resultado
cv2.imwrite("panorama_final.jpg",panorama)
print("Guardado: panorama_final.jpg")

cv2.imshow("Panorama Final",panorama)
print("\nENTER para salir\n")

while True:
    key = cv2.waitKey(1)
    if key == 13:
        break
cv2.destroyAllWindows()