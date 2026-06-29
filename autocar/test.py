from pop import Pilot

car = Pilot.AutoCar()

car.forward()
car.backward()
car.joystick()
car.camPan(10)
car.camTilt(10)

value = car.getGyro()
print(value)

