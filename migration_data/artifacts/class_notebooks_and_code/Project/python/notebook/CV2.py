#!/usr/bin/env python
# coding: utf-8

# In[6]:


import cv2
from pop import Util

Util.enable_imshow()

cam = Util.gstrmer(width=640, height=480)

camera = cv2.VideoCapture(cam, cv2.CAP_GSTREAMER)
if not camera.isOpened():
    print("Not found camera")
width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
print("initwidth: %d, initheight: %d" % (width,height))

for _ in range(120):
    ret, frame = camera.read()
    if not ret:
        break

    cv2.imshow("soda", frame)

camera.release()
cv2.destroyAllWindows()


# In[11]:


import cv2
from pop import Util

Util.enable_imshow()


# In[ ]:


cam = Util.gstrmer(width = 640, height = 480)
camera = cv2.VideoCapture(cam, cv2.CAP_GSTREAMER)
if not camera.isOpened():
    print("Not found camera")


# In[13]:


fourcc = cv2.VideoWriter_fourcc(*"X264")
out = cv2.VideoWriter("soda.avi", fourcc, 30, (640,480))


# In[14]:


for _ in range(120):
    ret, frame = camera.read()
    framGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    out.write(frame)
    
    cv2.imshow("soda", framGray)


# In[11]:


import subprocess as sp, time
from IPython.display import display, Javascript
from ipywidgets import widgets
from pop import Util


# In[1]:


#얼굴인식
import cv2
from pop import Util

Util.enable_imshow()

haar_face='/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_face)
cam = Util.gstrmer(width = 640, height = 480)
camera = cv2.VideoCapture(cam, cv2.CAP_GSTREAMER)
if not camera.isOpened():
    print("Not Found Camera")


# In[ ]:


while True:
    ret, img = camera.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3 ,minNeighbors=1,minSize=(100,100))
    cv2.imshow("img", img)
    for(x,y,w,h) in faces:
        cv2.rectangle(img,(x,y), (x+w, y+h), (255,0,0),2)
        cv2.imshow('img', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()


# In[ ]:





# In[1]:


import cv2
from pop import Util

Util.enable_imshow()

haar_face = '/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_face)

cam = Util.gstrmer(width=640, height=480)
camera = cv2.VideoCapture(cam, cv2.CAP_GSTREAMER)
if not camera.isOpened():
    print("Not found camera")

while True:
    ret, img = camera.read()
    if not ret:
        print("Failed to retrieve frame")
        break
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=1, minSize=(100, 100))

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        print(f"face at (x: {x}, y: {y}), width: {w}, height: {h}")
    
    cv2.imshow('img', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()

