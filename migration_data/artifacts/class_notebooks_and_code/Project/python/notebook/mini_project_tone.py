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


# In[5]:


import pyaudio
import numpy as np
import time


# In[6]:


class Tone:
    def __init__(self, volume = 1, rate=48000, channels=1):
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


# In[7]:


#vector [각도. 거리. 데이터신뢰도]
from IPython.display import clear_output 

Car.forward(10)

print("Start")
start = time.time()
tone = Tone(.7, 48000, 1)
stop = time.time()
print("End")
print("time : ", stop - start)


# In[11]:


Car.stop()


# In[8]:


#vector [각도. 거리. 데이터신뢰도]
import time
Car.forward(10)
while True:
    vectors = lidar.getVectors()
    for v in vectors:
        #if v[0] >= 300 or v[0] <= 60: #전방 120도
         if 170 <= v[0] <= 190:
            if v[1] <= 200: # 20cm 이하
                print(v[0], " good ", v[1])
                time.sleep(0.2)
                break
            else:
                print(v[0], " bad ", v[1])
                time.sleep(0.2)
                clear_output()
    
    if v[1] <= 200:
        print("break : ", v[0], " ", v[1])
        break

Car.stop()


# In[9]:


Car.forward(10)


# In[14]:


from IPython.display import clear_output 
import time
while True:
    vectors = lidar.getVectors()
    for v in vectors:
        #if v[0] >= 340 or v[0] <= 20: #전방 120도
        if 170 <= v[0] <= 190:
            if 500 <=v[1] and v[1] <= 700: # 20cm 이하
                print(v[0], " 500 ~ 700 ", v[1])
                tone.play(1, 1, 4)
            if 300 <=v[1] and v[1] < 500:
                print(v[0], " 300 ~ 500 ", v[1])
                tone.play(2, 1, 4)
                
            if 0 <=v[1] and v[1] < 300:
                print(v[0], " 0 ~ 300 ", v[1])
                tone.play(3, 1, 4)
            else:
                print(v[0], " nothing", v[1])
                clear_output()


Car.stop()


# In[15]:


Car.stop()


# In[5]:


from IPython.display import clear_output
print("Hi")
clear_output()


# In[15]:


lidar.stopMotor()


# In[21]:


import asyncio
from IPython.display import clear_output

async def process_lidar_data(lidar, tone):
    while True:
        vectors = await get_lidar_vectors(lidar)
        for v in vectors:
            if 170 <= v[0] <= 190:
                if 500 <= v[1] and v[1] <= 700:
                    print(v[0], " 400 ~ 600 ", v[1])
                    await tone.play(1, 1, 4)
                if 300 <= v[1] and v[1] < 500:
                    print(v[0], " 200 ~ 400 ", v[1])
                    clear_output()
                    await tone.play(2, 1, 4)
                if 0 <= v[1] and v[1] < 300:
                    print(v[0], " 0 ~ 200 ", v[1])
                    await tone.play(3, 1, 4)
                else:
                    print(v[0], " nothing", v[1])

async def get_lidar_vectors(lidar):
    # Simulate fetching lidar data asynchronously (replace with actual async call)
    await asyncio.sleep(1)  # Simulated delay
    return [(175, 450), (185, 250)]

class Tone:
    def __init__(self, volume=1, rate=48000, channels=1):
        self.volume = volume
        self.rate = rate
        self.channels = channels
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=self.channels, rate=self.rate, output=True)
        
    async def play(self, octave, note, duration):
        f = 2**(octave) * 55 * 2**(((note) - 10) / 12)
        sample = (np.sin(2 * np.pi * np.arange(self.rate * duration) * f / self.rate)).astype(np.float32)
        self.stream.write(self.volume * sample)

async def main():
    tone = Tone(1.4, 48000, 1)
    print("End")
    await process_lidar_data(lidar, tone)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    lidar = None  # Replace with your lidar initialization
    loop.run_until_complete(main())

