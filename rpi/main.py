import random
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

MAX_LENGTH = 60

data = []
xAxis = []

def initializeData():
    for i in range(MAX_LENGTH):
        xAxis.append(i)
        data.append(0)

def animate(i):
    addRandomData()
    ax1.clear()
    ax1.plot(xAxis, data)

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
ani = animation.FuncAnimation(fig, animate, interval=300)
plt.show()
