import numpy as np
import cv2
import dlib
from scipy.spatial import distance as dist
from scipy.spatial import ConvexHull
from PIL import Image
from PIL import ImageTk
import cv2, threading, os, time
from threading import Thread
from os import listdir
from os.path import isfile, join

import dlib
from imutils import face_utils, rotate_bound
import math

overlay = []

PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"

FULL_POINTS = list(range(0, 68))
FACE_POINTS = list(range(17, 68))

JAWLINE_POINTS = list(range(0, 17))
RIGHT_EYEBROW_POINTS = list(range(17, 22))
LEFT_EYEBROW_POINTS = list(range(22, 27))
NOSE_POINTS = list(range(27, 36))
RIGHT_EYE_POINTS = list(range(36, 42))
LEFT_EYE_POINTS = list(range(42, 48))
MOUTH_OUTLINE_POINTS = list(range(48, 61))
MOUTH_INNER_POINTS = list(range(61, 68))

detector = dlib.get_frontal_face_detector()

predictor = dlib.shape_predictor(PREDICTOR_PATH)

def eye_size(eye):
  eyeWidth = dist.euclidean(eye[0], eye[3])
  hull = ConvexHull(eye)
  eyeCenter = np.mean(eye[hull.vertices, :], axis=0)

  eyeCenter = eyeCenter.astype(int)

  return int(eyeWidth), eyeCenter

def place_eye(frame, eyeCenter, eyeSize):
  eyeSize = int(eyeSize * 1.5)

  x1 = int(eyeCenter[0,0] - (eyeSize/2))
  x2 = int(eyeCenter[0,0] + (eyeSize/2))
  y1 = int(eyeCenter[0,1] - (eyeSize/2))
  y2 = int(eyeCenter[0,1] + (eyeSize/2))

  h, w = frame.shape[:2]

   # check for clipping
  if x1 < 0:
    x1 = 0
  if y1 < 0:
    y1 = 0
  if x2 > w:
    x2 = w
  if y2 > h:
    y2 = h

   # re-calculate the size to avoid clipping
  eyeOverlayWidth = x2 - x1
  eyeOverlayHeight = y2 - y1

   # calculate the masks for the overlay
  eyeOverlay = cv2.resize(imgEye, (eyeOverlayWidth,eyeOverlayHeight), interpolation = cv2.INTER_AREA)
  mask = cv2.resize(orig_mask, (eyeOverlayWidth,eyeOverlayHeight), interpolation = cv2.INTER_AREA)
  mask_inv = cv2.resize(orig_mask_inv, (eyeOverlayWidth,eyeOverlayHeight), interpolation = cv2.INTER_AREA)

   # take ROI for the verlay from background, equal to size of the overlay image
  roi = frame[y1:y2, x1:x2]

   # roi_bg contains the original image only where the overlay is not, in the region that is the size of the overlay.
  roi_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)

   # roi_fg contains the image pixels of the overlay only where the overlay should be
  roi_fg = cv2.bitwise_and(eyeOverlay,eyeOverlay,mask = mask)

   # join the roi_bg and roi_fg
  dst = cv2.add(roi_bg,roi_fg)

   # place the joined image, saved to dst back over the original image
  frame[y1:y2, x1:x2] = dst

def eye():
    left_eye = landmarks[LEFT_EYE_POINTS]
    right_eye = landmarks[RIGHT_EYE_POINTS]

     # cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)

    leftEyeSize, leftEyeCenter = eye_size(left_eye)
    rightEyeSize, rightEyeCenter = eye_size(right_eye)

    place_eye(frame, leftEyeCenter, leftEyeSize)
    place_eye(frame, rightEyeCenter, rightEyeSize)






 #---------------------------------------------------------
 # Load and pre-process the eye-overlay
 #---------------------------------------------------------
 # Load the image to be used as our overlay

### Eye section ###
imgEye = cv2.imread('Eye.png',-1)

 # Create the mask from the overlay image
orig_mask = imgEye[:,:,3]

 # Create the inverted mask for the overlay image
orig_mask_inv = cv2.bitwise_not(orig_mask)

 # Convert the overlay image image to BGR
 # and save the original image size
imgEye = imgEye[:,:,0:3]
origEyeHeight, origEyeWidth = imgEye.shape[:2]
### Eye section ###

### Other overlay functions ###

def draw_over(frame, sprite, x_offset, y_offset):
    (h,w) = (sprite.shape[0], sprite.shape[1])
    (imgH,imgW) = (frame.shape[0], frame.shape[1])

    if y_offset+h >= imgH: #if sprite gets out of image in the bottom
        sprite = sprite[0:imgH-y_offset,:,:]

    if x_offset+w >= imgW: #if sprite gets out of image to the right
        sprite = sprite[:,0:imgW-x_offset,:]

    if x_offset < 0: #if sprite gets out of image to the left
        sprite = sprite[:,abs(x_offset)::,:]
        w = sprite.shape[1]
        x_offset = 0

    #for each RGB chanel
    for c in range(3):
            #chanel 4 is alpha: 255 is not transpartne, 0 is transparent background
            frame[y_offset:y_offset+h, x_offset:x_offset+w, c] =  \
            sprite[:,:,c] * (sprite[:,:,3]/255.0) +  frame[y_offset:y_offset+h, x_offset:x_offset+w, c] * (1.0 - sprite[:,:,3]/255.0)
    return frame

def adjust_over2head(sprite, head_width, head_ypos, ontop = True,fct=1.0):
    (h_sprite,w_sprite) = (sprite.shape[0], sprite.shape[1])
    factor = fct*head_width/w_sprite
    sprite = cv2.resize(sprite, (0,0), fx=factor, fy=factor) # adjust to have the same width as head
    (h_sprite,w_sprite) = (sprite.shape[0], sprite.shape[1])

    y_orig =  head_ypos-h_sprite if ontop else head_ypos # adjust the position of sprite to end where the head begins
    if (y_orig < 0): #check if the head is not to close to the top of the image and the sprite would not fit in the screen
            sprite = sprite[abs(y_orig)::,:,:] #in that case, we cut the sprite
            y_orig = 0 #the sprite then begins at the top of the image
    return (sprite, y_orig)

def apply_over(image, over_path,w,x,y, angle, ontop = True,fct = 1.0):
    sprite = cv2.imread(over_path,-1)
    #print sprite.shape
    sprite = rotate_bound(sprite, angle)
    (sprite, y_final) = adjust_over2head(sprite, w, y, ontop,fct)
    image = draw_over(image,sprite,x, y_final)

    return image




def calculate_boundbox(list_coordinates):
    x = min(list_coordinates[:,0])
    y = min(list_coordinates[:,1])
    w = max(list_coordinates[:,0]) - x
    h = max(list_coordinates[:,1]) - y
    return (x,y,w,h)

def get_face_boundbox(points, face_part):
    if face_part == 1:
        (x,y,w,h) = calculate_boundbox(points[17:22]) #left eyebrow
    elif face_part == 2:
        (x,y,w,h) = calculate_boundbox(points[22:27]) #right eyebrow
    elif face_part == 3:
        (x,y,w,h) = calculate_boundbox(points[36:42]) #left eye
    elif face_part == 4:
        (x,y,w,h) = calculate_boundbox(points[42:48]) #right eye
    elif face_part == 5:
        (x,y,w,h) = calculate_boundbox(points[29:36]) #nose
    elif face_part == 6:
        (x,y,w,h) = calculate_boundbox(points[48:68]) #mouth
    return (x,y,w,h)

def calculate_inclination(point1, point2):
    x1,x2,y1,y2 = point1[0], point2[0], point1[1], point2[1]
    incl = 180/math.pi*math.atan((float(y2-y1))/(x2-x1))
    return incl






 # Start capturing the WebCam
video_capture = cv2.VideoCapture(0)

while True:
  ret, frame = video_capture.read()

  if ret:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rects = detector(gray, 0)

    for rect in rects:
      x = rect.left()
      y = rect.top()
      x1 = rect.right()
      y1 = rect.bottom()
      w = rect.width()
      h = rect.height()

      shape = predictor(gray, rect)
      shape = face_utils.shape_to_np(shape)
      incl = calculate_inclination(shape[17], shape[26]) #inclination based on eyebrows

      landmarks = np.matrix([[p.x, p.y] for p in predictor(frame, rect).parts()])

      is_mouth_open = (shape[66][1] -shape[62][1]) >= 10



      for o in overlay:
          if o == 'eye':
              eye()
          if o == 'hat':
             frame = apply_over(frame, "hat.png",w,x,y, incl,fct=1.0)
          if o == 'glasses':
              (x3,y3,_,h3) = get_face_boundbox(shape, 1)
              frame = apply_over(frame, "glasses.png",w,x,y3, incl, ontop = False)
          if o == 'dog_e':
              frame = apply_over(frame, "doggy_ears.png",w,x,y, incl)
          if o == 'dog_n':
              (x3,y3,w3,h3) = get_face_boundbox(shape, 5) #nose
              frame = apply_over(frame, "doggy_nose.png",w3,x3-15,y3, incl, ontop = False,fct=1.7)

              if is_mouth_open:
                  (x0,y0,w0,h0) = get_face_boundbox(shape, 6)
                  frame=apply_over(frame, "doggy_tongue.png",w0,x0,y0, incl, ontop = False)
          if o == 'mus':
              (x1,y1,w1,h1) = get_face_boundbox(shape, 6)
              frame = apply_over(frame, "mustache.png",w1+20,x1-10,y1, incl)






    cv2.imshow("Faces with Overlay", frame)

  ch = 0xFF & cv2.waitKey(1)

  if ch == 27:
    break
  if ch == ord('q'):
      if 'eye' not in overlay:
          overlay.append('eye')
      else:
          overlay.remove('eye')
  if ch == ord('w'):
      if 'hat' not in overlay:
          overlay.append('hat')
      else:
          overlay.remove('hat')
  if ch == ord('e'):
      if 'glasses' not in overlay:
          overlay.append('glasses')
      else:
          overlay.remove('glasses')
  if ch == ord('r'):
      if 'dog_e' not in overlay:
          overlay.append('dog_e')
      else:
          overlay.remove('dog_e')
  if ch == ord('t'):
      if 'dog_n' not in overlay:
          overlay.append('dog_n')
      else:
          overlay.remove('dog_n')

  if ch == ord('y'):
      if 'mus' not in overlay:
          overlay.append('mus')
      else:
          overlay.remove('mus')



cv2.destroyAllWindows()
