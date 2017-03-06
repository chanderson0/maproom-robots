import sys
sys.path.append('..')

import time
import json
import argparse

import cv2
import cv2.aruco as A
import numpy as np

from maproom.camera import MaproomCamera
import maproom.constants as c
import maproom.util as u

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--camera", type=int, default=0,
  help="Which camera to use")
ap.add_argument("-d", "--display", type=bool, default=True,
  help="Whether or not frames should be displayed")
ap.add_argument("-x", "--width", type=int, default=c.resolution[0],
  help="Width of image")
ap.add_argument("-y", "--height", type=int, default=c.resolution[1],
  help="Height of image")
args = vars(ap.parse_args())

#Start capturing images for calibration
resolution = (args['width'], args['height'])
camera = MaproomCamera(args['camera'], resolution)
camera.load(loadCameraMatrix=False, loadPerspective=False, loadHeight=False)

REQUIRED_COUNT = 25

allCorners = []
allIds = []

# Only update few frames so we get more diverse data
frameIdx = 0
frameSpacing = 5
success = False

camera.start()
while True:
  frame, gray = camera.update(gray=True)
  markerCorners, markerIds = camera.detectAruco()

  if len(markerCorners) > 0 and frameIdx % frameSpacing == 0:
    ret, charucoCorners, charucoIds = cv2.aruco.interpolateCornersCharuco(markerCorners, markerIds, gray, c.charucoBoard)
    if charucoCorners is not None and charucoIds is not None and len(charucoCorners) > 3:
      allCorners.append(charucoCorners)
      allIds.append(charucoIds)

    cv2.aruco.drawDetectedMarkers(gray, markerCorners, markerIds)

  if args['display']:
    cv2.imshow('frame',gray)

  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

  frameIdx += 1
  print("Found: " + str(len(allIds)) + " / " + str(REQUIRED_COUNT))

  if len(allIds) >= REQUIRED_COUNT:
    success = true
    break

if success:
  print('Done collecting data, computing...')

  try:
    err, cameraMatrix, distCoeffs, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(allCorners,allIds,c.charucoBoard,c.resolution,None,None)
    print('Calibrated with err', err)

    out = json.dumps({
      'cameraMatrix': cameraMatrix.tolist(),
      'distCoeffs': distCoeffs.tolist(),
      'err': err
    })
    filename = 'calibrations/video'+str(cameraID)+'.json'
    print('Saving calibration to file:', filename)
    with open(filename, 'w') as f:
      f.write(out)

    print('...done!')
  except Exception as err:
    print(err)
    success = false

  camera.setCameraMatrix(cameraMatrix, distCoeffs)
  while True:
    camera.update(gray=False)
    frame = camera.undistort(gray=False)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

camera.stop()
cv2.destroyAllWindows()