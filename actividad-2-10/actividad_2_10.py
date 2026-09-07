import cv2
import numpy as np
import open3d as o3d
import copy
import math

VISTA1_LEFT = "vista1_left.jpeg"
VISTA1_RIGHT = "vista1_right.jpeg"
VISTA2_LEFT = "vista2_left.jpeg"
VISTA2_RIGHT = "vista2_right.jpeg"

BASELINE = 0.04
FOCAL = 900.0
MIN_DEPTH = 0.20
MAX_DEPTH = 1.80
MIN_DISPARITY = 1.0
VOXEL_SIZE = 0.008
ROI = (0.05, 0.95, 0.08, 0.92)

ICP_GRUESO = 0.25
ICP_FINO = 0.08


def cargar(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar: {path}")
    return img


def recortar(img):
    h, w = img.shape[:2]
    x1, x2, y1, y2 = ROI
    return img[int(h*y1):int(h*y2), int(w*x1):int(w*x2)]


def preparar_par(left_path, right_path):
    left = cargar(left_path)
    right = cargar(right_path)

    if left.shape != right.shape:
        right = cv2.resize(right, (left.shape[1], left.shape[0]))

    return recortar(left), recortar(right)


def gray(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(g)
    return cv2.GaussianBlur(g, (3, 3), 0)


def estimar_movimiento(left, right, nombre):
    g1 = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create(7000)
    kp1, des1 = orb.detectAndCompute(g1, None)
    kp2, des2 = orb.detectAndCompute(g2, None)

    if des1 is None or des2 is None:
        return 0.0, 128

    matches = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(des1, des2, k=2)

    good = []
    for par in matches:
        if len(par) == 2:
            m, n = par
            if m.distance < 0.75 * n.distance:
                good.append(m)

    if len(good) < 20:
        return 0.0, 128

    pts1 = np.float32([kp1[m.queryIdx].pt for m in good])
    pts2 = np.float32([kp2[m.trainIdx].pt for m in good])

    _, mask = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC, 1.0, 0.99)

    if mask is not None:
        pts1 = pts1[mask.ravel() == 1]
        pts2 = pts2[mask.ravel() == 1]

    if len(pts1) < 10:
        return 0.0, 128

    dx = pts1[:, 0] - pts2[:, 0]
    dy = pts1[:, 1] - pts2[:, 1]

    dx_pos = dx[(dx > 0) & (dx < 300)]
    if len(dx_pos) < 10:
        dx_pos = dx

    dy_med = float(np.median(dy))
    dx_p90 = float(np.percentile(dx_pos, 90))

    print(f"{nombre}: dy={dy_med:.2f}px, dx90={dx_p90:.2f}px")

    return dy_med, int(math.ceil(max(64, min(224, dx_p90 + 48)) / 16) * 16)


def alinear_vertical(left, right, dy):
    h, w = right.shape[:2]
    M = np.float32([[1, 0, 0], [0, 1, dy]])
    right = cv2.warpAffine(right, M, (w, h), borderMode=cv2.BORDER_CONSTANT)

    m = int(abs(round(dy))) + 2

    if 0 < m < h // 4:
        if dy > 0:
            left = left[m:, :]
            right = right[m:, :]
        elif dy < 0:
            left = left[:-m, :]
            right = right[:-m, :]

    return left, right


def disparidad(left, right, num_disp):
    block = 5

    stereo = cv2.StereoSGBM_create(
        minDisparity=0,
        numDisparities=num_disp,
        blockSize=block,
        P1=8 * block * block,
        P2=32 * block * block,
        disp12MaxDiff=1,
        uniquenessRatio=2,
        speckleWindowSize=80,
        speckleRange=2,
        preFilterCap=63,
        mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
    )

    d = stereo.compute(gray(left), gray(right)).astype(np.float32) / 16.0
    d[d < MIN_DISPARITY] = 0
    d[d > num_disp] = 0

    return cv2.medianBlur(d, 3)


def guardar_disparidad(d, nombre):
    vis = cv2.normalize(d, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    vis = cv2.applyColorMap(vis, cv2.COLORMAP_JET)
    cv2.imwrite(nombre, vis)


def nube_desde_disparidad(img, d):
    h, w = d.shape
    u, v = np.meshgrid(np.arange(w), np.arange(h))

    valid = d > MIN_DISPARITY

    Z = np.zeros_like(d, dtype=np.float64)
    Z[valid] = (FOCAL * BASELINE) / d[valid]

    valid = valid & (Z > MIN_DEPTH) & (Z < MAX_DEPTH)

    if np.count_nonzero(valid) > 100:
        z = Z[valid]
        z1, z2 = np.percentile(z, [2, 98])
        valid = valid & (Z >= z1) & (Z <= z2)

    X = (u - w / 2) * Z / FOCAL
    Y = (v - h / 2) * Z / FOCAL

    puntos = np.column_stack((X[valid], -Y[valid], Z[valid]))
    colores = img[valid][:, ::-1] / 255.0

    nube = o3d.geometry.PointCloud()

    if len(puntos) > 0:
        nube.points = o3d.utility.Vector3dVector(puntos)
        nube.colors = o3d.utility.Vector3dVector(colores)

    return nube


def limpiar(nube):
    if len(nube.points) == 0:
        return nube

    nube = nube.voxel_down_sample(VOXEL_SIZE)

    if len(nube.points) > 80:
        nube, _ = nube.remove_statistical_outlier(nb_neighbors=25, std_ratio=1.7)

    if len(nube.points) > 80:
        nube, _ = nube.remove_radius_outlier(nb_points=6, radius=0.04)

    return nube


def procesar(left_path, right_path, nombre):
    print(f"\nProcesando {nombre}")

    left, right = preparar_par(left_path, right_path)
    dy, num_disp = estimar_movimiento(left, right, nombre)
    left, right = alinear_vertical(left, right, dy)

    cv2.imwrite(f"{nombre}_left_usada.jpg", left)
    cv2.imwrite(f"{nombre}_right_usada.jpg", right)

    d = disparidad(left, right, num_disp)
    guardar_disparidad(d, f"{nombre}_disparidad_color.png")

    nube = limpiar(nube_desde_disparidad(left, d))
    o3d.io.write_point_cloud(f"{nombre}.ply", nube)

    print(f"{nombre}.ply guardado con {len(nube.points)} puntos")

    return nube


def preparar_icp(nube):
    nube = nube.voxel_down_sample(VOXEL_SIZE * 2)

    if len(nube.points) > 30:
        nube.estimate_normals(
            o3d.geometry.KDTreeSearchParamHybrid(radius=0.08, max_nn=30)
        )

    return nube


def inicial(source, target):
    T = np.eye(4)

    if len(source.points) == 0 or len(target.points) == 0:
        return T

    T[:3, 3] = np.asarray(target.points).mean(axis=0) - np.asarray(source.points).mean(axis=0)

    return T


def icp(nube1, nube2):
    print("\nAlineando con ICP")

    source = preparar_icp(copy.deepcopy(nube2))
    target = preparar_icp(copy.deepcopy(nube1))
    T0 = inicial(source, target)

    r1 = o3d.pipelines.registration.registration_icp(
        source,
        target,
        ICP_GRUESO,
        T0,
        o3d.pipelines.registration.TransformationEstimationPointToPoint()
    )

    r2 = o3d.pipelines.registration.registration_icp(
        source,
        target,
        ICP_FINO,
        r1.transformation,
        o3d.pipelines.registration.TransformationEstimationPointToPoint()
    )

    print(f"Fitness grueso: {r1.fitness:.4f}")
    print(f"RMSE grueso: {r1.inlier_rmse:.4f}")
    print(f"Fitness fino: {r2.fitness:.4f}")
    print(f"RMSE fino: {r2.inlier_rmse:.4f}")

    nube2_alineada = copy.deepcopy(nube2)
    nube2_alineada.transform(r2.transformation)

    reconstruccion = limpiar(nube1 + nube2_alineada)

    o3d.io.write_point_cloud("vista2_alineada.ply", nube2_alineada)
    o3d.io.write_point_cloud("reconstruccion_final2.ply", reconstruccion)

    print(f"reconstruccion_final2.ply guardado con {len(reconstruccion.points)} puntos")

    return nube2_alineada, reconstruccion


def ver(nube, titulo):
    if len(nube.points) > 0:
        o3d.visualization.draw_geometries([nube], window_name=titulo)


def ver_comparacion(nube1, nube2, titulo):
    a = copy.deepcopy(nube1)
    b = copy.deepcopy(nube2)

    a.paint_uniform_color([1, 0, 0])
    b.paint_uniform_color([0, 0, 1])

    o3d.visualization.draw_geometries([a, b], window_name=titulo)


def main():
    nube1 = procesar(VISTA1_LEFT, VISTA1_RIGHT, "vista1")
    nube2 = procesar(VISTA2_LEFT, VISTA2_RIGHT, "vista2")

    ver_comparacion(nube1, nube2, "Antes de ICP")

    nube2_alineada, reconstruccion = icp(nube1, nube2)

    ver_comparacion(nube1, nube2_alineada, "Después de ICP")
    ver(nube1, "Vista 1")
    ver(nube2, "Vista 2")
    ver(reconstruccion, "Reconstrucción final")


if __name__ == "__main__":
    main()