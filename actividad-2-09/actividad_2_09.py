import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv
# Prohibited to use pyrealsense2, kornia, torch, opencv-contrib-python (cv2.rgbd.depthTo3d function), PyntCloud, o3d or Pillow libraries

# 1. Load the K matrix from the CSV file
K = []
with open("camera_intrinsics.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        
        # Ignore comments or empty rows
        if len(row) == 0:
            continue
        if row[0].startswith("#"):
            continue
        K.append([float(value) for value in row])
K = np.array(K)
print("Camera Intrinsic Matrix:")
print(K)

# Extract intrinsic parameters
fx = K[0, 0]
fy = K[1, 1]
cx = K[0, 2]
cy = K[1, 2]

# 2.a Load the aligned color image
color_image = cv2.imread("aligned_color.png")
color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
# 2.b Read the raw 16-bit depth
depth_image = cv2.imread("aligned_depth_raw.png", cv2.IMREAD_UNCHANGED)

# 3. 3D Coordinate Calculation
height, width = depth_image.shape
points = []
colors = []
depth_scale = 0.001  # mm -> meters
step = 2

for v in range(0, height, step):
    for u in range(0, width, step):

        # Depth in meters
        z = depth_image[v, u] * depth_scale

        # Ignore invalid values
        if z <= 0:
            continue

        # Ignore far points
        if z > 3.0:
            continue

        x = (u - cx) * z / fx
        y = (v - cy) * z / fy

        points.append([x, y, z])
        colors.append(color_image[v, u] / 255.0)

points = np.array(points)
colors = np.array(colors)
print("Total 3D points:", len(points))

# 4. Display the 3D result
X = points[:, 0]
Y = points[:, 1]
Z = points[:, 2]

fig = plt.figure(figsize=(12,10))
ax = fig.add_subplot(111, projection='3d')

ax.scatter(X,Y,Z,c=colors,s=0.3)
ax.set_title("3D Point Cloud - Intel RealSense D435i")

ax.set_xlabel("X [m]")
ax.set_ylabel("Y [m]")
ax.set_zlabel("Z [m]")

ax.view_init(elev=-90, azim=-90)
ax.set_box_aspect([1,1,1])
plt.show()

# 5. Export to PLY format (for MeshLab)
ply_filename = "ply_act9.ply"

with open(ply_filename, "w") as ply_file:

    # Header
    ply_file.write("ply\n")
    ply_file.write("format ascii 1.0\n")
    ply_file.write(f"element vertex {len(points)}\n")

    ply_file.write("property float x\n")
    ply_file.write("property float y\n")
    ply_file.write("property float z\n")

    ply_file.write("property uchar red\n")
    ply_file.write("property uchar green\n")
    ply_file.write("property uchar blue\n")

    ply_file.write("end_header\n")

    # Write points
    for i in range(len(points)):
        x, y, z = points[i]
        r, g, b = (colors[i] * 255).astype(np.uint8)
        ply_file.write(f"{x} {y} {z} {r} {g} {b}\n")
print(f"PLY file saved as: {ply_filename}")