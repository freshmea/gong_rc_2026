#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pop import LiDAR, Pilot
import time


# In[2]:


from IPython.display import clear_output


# In[3]:


Car = Pilot.AutoCar()


# In[4]:


lidar = LiDAR.Rplidar()
lidar.connect()


# In[6]:


lidar.stopMotor()
Car.stop()


# In[5]:


lidar.startMotor()


# In[8]:


from pop.Util import imshow
lidar_map = lidar.getMap(limit_distance = 2000, size =(300, 300))
imshow("map", lidar_map)


# In[15]:


vectors = lidar.getVectors()
for v in vectors:
    print(v[0],v[1],v[2])
    clear_output()


# In[7]:


Car.setSpeed(99)
Car.steering = 0


# In[13]:


Car.stop()


# In[21]:


#vector [각도. 거리. 데이터신뢰도]

Car.forward(90)
while True:
    vectors = lidar.getVectors()
    for v in vectors:
        if v[0] >= 300 or v[0] <= 60: #전방 120도
         #if 170 <= v[0] <= 190:
            if v[1] <= 800: # 20cm 이하
                print(v[0], " good ", v[1])

                break
                
            else:
                print(v[0], " bad ", v[1])
                
    
    if v[1] <= 800:
        print("break : ", v[0], " ", v[1])
        break

Car.stop()
    


# In[32]:


Car.backward(70)


# In[33]:


Car.stop()


# In[16]:


Car.joystick()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[8]:


Car.stop()


# In[ ]:


from IPython.display import clear_output 
import time
clear_output

while True:
    vectors = lidar.getVectors()
    for v in vectors:
        if v[0] >= 300 or v[0] <= 60:
            if v[1] <= 200:                
                print(v[0], " good ", v[1])
                break
            else:
                clear_output()
                print(v[0], " bad ", v[1])

                
    if v[1] <= 200:
        print("break : ", v[0], " ", v[1])
        time.sleep(1)
        break


# In[32]:


from IPython.display import clear_output
print("Hi")
clear_output()


# In[33]:


lidar.stopMotor()


# In[ ]:




