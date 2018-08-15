import tkinter as tk
from tkinter import *
from tkinter.ttk import Button
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.animation as animation
import math
import random
import sys
import time # just for debugging purposes, delete later

current_loop_timestamp=1 #stores the timestamp of the current animation loop execution
last_loop_timestamp=0 #stores the timestamp of the previous animation loop execution

MAX_LENGTH = 60
data = []
xAxis = []

pid_active = True

def togglePID():
    global pid_active
    pid_active = not pid_active
    if pid_active:
        pid_button.config(text="PID ENABLED")
    else:
        pid_button.config(text="PID DISABLED")

def initializeData():
    for i in range(MAX_LENGTH):
        xAxis.append(i)
        data.append(0)

style.use('fivethirtyeight')

fig = plt.figure()

root = tk.Tk()
root.geometry("1920x1080+0+0")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().place(x=800, y=0)

# Tkinter Widgets
title_label = Label(root, text="AMORPHICS", font=('Aller Display', 70))
title_label.place(x=10, y=10)
motor_label = Label(root, text="Motor Position: \t0", font=('Avenir LT Std 35 Light', 30))
kp_label = Label(root, text="P: \t\t0", font=('Avenir LT Std 35 Light', 30))
ki_label = Label(root, text="I: \t\t0", font=('Avenir LT Std 35 Light', 30))
kd_label = Label(root, text="D: \t\t0", font=('Avenir LT Std 35 Light', 30))
pid_button = Button(root, text="PID DISABLED", width=13, command=togglePID)
diameter_label = Label(root, text="Diameter: \t0", font=('Avenir LT Std 35 Light', 30))
current_command = StringVar()
current_command.set("hi")


terminal_entry = Entry(root, textvariable=current_command)
def commandEntered(p0):
    print("Command: " + terminal_entry.get())
    terminal_entry.delete(0, 'end')
terminal_entry.bind("<Return>", commandEntered)
# Fans
f1_slider = Scale(root, from_=100, to=0, label="Fan 1", length=450, width=30, font=('Avenir LT Std 35 Light', 10))
f2_slider = Scale(root, from_=100, to=0, label="Fan 2", length=450, width=30, font=('Avenir LT Std 35 Light', 10))

pid_button.place(x=10, y=150)
kp_label.place(x=10, y=200)
ki_label.place(x=10, y=250)
kd_label.place(x=10, y=300)
motor_label.place(x=10, y=350)
f1_slider.place(x=550, y=15)
f2_slider.place(x=650, y=15)
diameter_label.place(x=800, y=480)
terminal_entry.place(x=10, y=400)

ax1 = fig.add_subplot(1,1,1)
line, = ax1.plot(xAxis, data)

togglePID()

def animate(i):
    global current_loop_timestamp, last_loop_timestamp
    last_loop_timestamp=current_loop_timestamp
    current_loop_timestamp=time.time()
    #print(1/(current_loop_timestamp-last_loop_timestamp))
    addRandomData()
    ax1.clear()
    ax1.plot(xAxis, data)
    dia_str = "Diameter: \t" + str(data[MAX_LENGTH-1]) + "mm"
    diameter_label.config(text=dia_str)
    return ax1.lines[0],

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


def on_closing():
    root.quit()
    root.destroy()
    sys.exit(0)

root.protocol("WM_DELETE_WINDOW", on_closing)

ani = animation.FuncAnimation(fig, animate, init_func = initializeData(), interval=1, blit=True)
root.mainloop()
