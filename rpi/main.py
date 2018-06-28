import random
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import serial
import keyboard

"""
======Stuff to Know======
Mac Serial Name: /dev/cu.usbserial-1440
Pi Serial Name: /dev/ttyUSB0
"""

# style.use('dark_background')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax2 = fig.add_subplot(1,1,1)
ax3 = fig.add_subplot(1,1,1)
ax4 = fig.add_subplot(1,1,1)



MAX_LENGTH = 60

data = []
xAxis = []
perfect = []
top = []
bottom = []

ser = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)

def initializeData():
    for i in range(MAX_LENGTH):
        xAxis.append(i)
        data.append(0)
        top.append(5)
        perfect.append(3)
        bottom.append(0)

def animate(i):
	
	if keyboard.is_pressed('y'):
		command = input(">>> ")
		ser.write(bytes(command, 'utf-8'))
    # addRandomData()
	ax1.clear()
	ax2.plot(xAxis, perfect, color="green")
	ax3.plot(xAxis, top, color="white")
	ax4.plot(xAxis, bottom, color="white")
	ax1.plot(xAxis, data, color="blue")
	ser.write(bytes('s', 'utf-8'))
	line = ser.readline()
	sensor = 0
	sensor_str = line
	if len(sensor_str) > 0:
		sensor = int(sensor_str) * 0.00488758553
	addData(sensor)


def popData():
    for i in range(len(data)-1):
        data[i] = data[i+1]
    del data[-1]

def addRandomData():
    num = random.randrange(1023)
    addData(num)

def addData(num):
    data.append(num)
    if len(data) > MAX_LENGTH:
        popData()

initializeData()


ani = animation.FuncAnimation(fig, animate, interval=1)
plt.show()
