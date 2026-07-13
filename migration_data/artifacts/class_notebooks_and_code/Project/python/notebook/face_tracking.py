#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#얼굴 추적
import cv2
from pop import Util

Util.enable_imshow()

haar_face='/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_face)
cam = Util.gstrmer(width = 640, height = 480)
camera = cv2.VideoCapture(cam, cv2.CAP_GSTREAMER)
if not camera.isOpened():
    print("Not Found Camera")


# In[2]:


import subprocess as sp, time
import time
from pop import Pilot


# In[3]:


Car=Pilot.AutoCar()


# In[4]:


margin_x = 30
margin_y = 30
_pos_x = pos_x = 90
_pos_y = pos_y = 0


# In[5]:


Car.camPan(pos_x)
Car.camTilt(pos_y)


# In[ ]:


while True:
    ret, img = camera.read()
    if not ret:
        print("ret : ",ret)
        print("Failed to retrieve frame")
        break
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    frame = cv2.flip(img, 1)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3 ,minNeighbors=1,minSize=(100,100))
    
    
    for(x,y,w,h) in faces:
        center_x = x + w/2
        center_y = y + y/2
        print("x : %d, y : %d, w : %d, h : %d" %(x,y,w,h))
        # tilt 0 ~ 90 # pan 5 ~ 180
        if center_x < 320 - margin_x:
            print("pan left")
            if pos_x - 1 >= 5:
                pos_x = pos_x - 1
                _pos_x = pos_x
            else:
                pos_x = 5
                _pos_x = pos_x

        elif center_x > 320 + margin_x:
            print("pan right")
            if pos_x + 1 <= 180:
                pos_x = pos_x + 1
                _pos_x = pos_x
            else:
                pos_x = 180
                _pos_x = pos_x   
        else:
            print("pan stop")
            pos_x = _pos_x
        Car.camPan(pos_x)
        
        
        if center_y < 240 - margin_y:
            if pos_y + 1 <= 90:
                print("tilt up")
                pos_y = pos_y + 1
                _pos_y = pos_y
            else:
                pos_y = 90
                _pos_y = pos_y

        elif center_y > 240 + margin_y:
            if pos_y - 1 >= 0:
                print("tilt down")
                pos_y = pos_y - 1
                _pos_y = pos_y
            else:
                pos_y = 0
                _pos_y = pos_y
        else:
            print("tilt stop")
            pos_y = _pos_y
        
        Car.camTilt(pos_y)
        print('pos_x : %d, pos_y : %d' %(pos_x, pos_y))
    cv2.imshow("frame", frame)
    cv2.imshow("img", img)
    cv2.rectangle(img,(x,y), (x+w, y+h), (255,0,0),2)
        
        

camera.release()
cv2.destroyAllWindows()

