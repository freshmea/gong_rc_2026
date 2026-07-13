#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pop import LiDAR, Pilot


# In[2]:


Car = Pilot.AutoCar()


# In[3]:


lidar = LiDAR.Rplidar()
lidar.connect()
lidar.startMotor()


# In[4]:


Car.setSpeed(99)
Car.steering = 0


# In[5]:


Car.stop()


# In[6]:


import pyaudio
import numpy as np
import time


# In[7]:


class Tone:
    def __init__(self, volume=.5, rate=48000, channels=1):
        self.volume= volume
        self.rate= rate
        self.channels= channels
        self.p= pyaudio.PyAudio()
        self.stream= self.p.open(format=pyaudio.paFloat32, channels=self.channels, rate=self.rate, output=True)
        
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def play(self, octave, note, duration):
        f = 2**(octave) * 55 * 2**(((note) -10) / 12)
        sample = (np.sin(2 * np.pi* np.arange(self.rate* duration) * f / self.rate)).astype(np.float32)
        self.stream.write(self.volume* sample)


# In[12]:


#vector [각도. 거리. 데이터신뢰도]
from IPython.display import clear_output 

Car.forward(10)

tone = Tone(.8, 48000, 1)

print("Start")


# In[ ]:


while True:
    vectors = lidar.getVectors()
    for v in vectors:
        if v[0] >= 340 or v[0] <= 20: #전방 120도
            if 400 <=v[1] and v[1] <= 600: # 20cm 이하
                print(v[0], " 400 ~ 600 ", v[1])
                tone.play(1, 1, 2)
            if 200 <=v[1] and v[1] < 400:
                print(v[0], " 200 ~ 400 ", v[1])
                tone.play(2, 1, 2)
            if 0 <=v[1] and v[1] < 200:
                print(v[0], " 0 ~ 200 ", v[1])
                tone.play(3, 1, 2)
            else:
                print(v[0], " nothing", v[1])
                clear_output()

Car.stop()


# In[14]:


Car.stop()


# In[138]:


from IPython.display import clear_output
print("Hi")
clear_output()


# In[15]:


lidar.stopMotor()

