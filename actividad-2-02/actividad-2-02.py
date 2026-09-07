import time
import sys
sys.path.append('/home/ed/Documents/CoppeliaSim_Edu_V4_10_0_rev0_Ubuntu22_04/programming/zmqRemoteApi/clients/python/src')
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import numpy as np
import cv2

client = RemoteAPIClient()
sim = client.getObject('sim')

sensor1Handle = sim.getObject('/Vision_sensor')

sim.startSimulation()

time.sleep(2)

img, [resX, resY] = sim.getVisionSensorImg(sensor1Handle)
img = np.frombuffer(img, dtype=np.uint8).reshape(resY, resX, 3)

img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
img = cv2.flip(img, 0)

cv2.imwrite('resultado.png', img)

sim.stopSimulation()