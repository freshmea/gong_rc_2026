#!/usr/bin/env python
# coding: utf-8

# In[9]:


#openCV
import cv2
from pop import Util

Util.enable_imshow()
Util.createIMG()


# In[10]:


#image 크기
image = cv2.imread("img.jpg", cv2.IMREAD_COLOR)
#h, w, c
h, w, c = image.shape
print("width : %d, height : %d, channel : %d" % (w, h, c))


# In[11]:


#color / gray 출력
from pop.Util import imshow
imshow("color", image)
image_gray = cv2.imread("img.jpg", cv2.IMREAD_GRAYSCALE)
imshow("gray", image_gray)


# In[17]:


#cam 크기 설정
cam = Util.gstrmer(width = 640, height = 480)


# In[18]:


#camera 
camera = cv2.VideoCapture(cam, cv2.CAP_GSTREAMER)
if not camera.isOpened():
    print("Not found camera")
width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
print("init width %d, init hegiht %d" % (width, height))


# In[16]:


for _ in range(120):
    ret, frame = camera.read()
    if not ret:
        print("no")
        break
    cv2.imshow("soda", frame)

camera.release()
cv2.destroyAllWindows()


# In[21]:


#배열 numpy
import numpy as np

arr = np.array([1,2,3])
print(arr)


# In[28]:


#array -> list
arr = np.array([-2, 0, 2, 4, 6, 8, 10])
print(arr.tolist())


# In[64]:


#10개 데이터 저장배열 0으로 초기화
#cds값 10개 배열에 저장
#배열 2행5열 배열로 바꿔라
from pop import Cds as cds
from ipywidgets import widgets
import time
lab=[]
Cds = cds
arr = np.zeros(10, dtype = int)
arr2 = np.resize(arr,(5,2))
print(arr2)
print(arr.tolist())
print(arr)


# In[91]:


from pop import Cds as cds
import time

Cds = cds
cds=Cds(7)

arr = np.zeros(10, dtype = int)
count = 0
while count < 10:
    arr[count] = cds.read()
    time.sleep(0.1)
    print("count : ", count, end = ", ")
    print("Cds : ", arr[count])
    count = count + 1
print("arr : ", arr)
reshape_arr = np.reshape(arr,(2,5))
print("reshape_arr : ")
print(reshape_arr)

