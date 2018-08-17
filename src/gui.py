import tkinter as tk
from tkinter import Label, Button, StringVar, Entry, Scale
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
import time
import main

current_loop_timestamp=1 # stores the timestamp of the current animation loop execution
last_loop_timestamp=0 # stores the timestamp of the previous animation loop execution

MAX_LENGTH = 60 # How many data values to keep before dumping
data = [] # Stores the sensor data to be graphed 
xAxis = [] # The x-axis grid (1...MAX_LENGTH)

pid_active = True # Whether the PID Loop is active
show_fps = False # Whether the FPS is shown

# Initialize the data
for i in range(MAX_LENGTH):
        xAxis.append(i)
        data.append(0)

def toggle_pid():
    global pid_active
    pid_active = not pid_active
    if pid_active:
        pid_button.config(text='PID ENABLED')
    else:
        pid_button.config(text='PID DISABLED')

# Toggle FPS
def toggle_fps(e):
    global show_fps
    if e.char == 'f':
        show_fps = not show_fps

style.use('fivethirtyeight')

# ---------------- WIDGETS ----------------
# Root Widget
fig = plt.figure()
root = tk.Toplevel()
root.geometry('1920x1080+0+0')
root.title('Amorphics')
root.protocol('WM_DELETE_WINDOW', exit)
title_label = Label(root, text='AMORPHICS', font=('Aller Display', 70))

# PID Widgets
kp_label = Label(root, text='P: \t\t0', font=('Avenir LT Std 35 Light', 30))
ki_label = Label(root, text='I: \t\t0', font=('Avenir LT Std 35 Light', 30))
kd_label = Label(root, text='D: \t\t0', font=('Avenir LT Std 35 Light', 30))
pid_button = Button(root, text='PID DISABLED', width=13, command=toggle_pid)

# Graph Widgets
diameter_label = Label(root, text='Diameter: \t0', font=('Avenir LT Std 35 Light', 30))
canvas = FigureCanvasTkAgg(fig, master=root)
canvasWidget = canvas.get_tk_widget()

# Terminal Widgets
current_command = StringVar()
current_command.set('')
terminal_entry = Entry(root, textvariable=current_command)
def commandEntered(p0):
    main.execute_command(terminal_entry.get())
    terminal_entry.delete(0, 'end')
terminal_entry.bind('<Return>', commandEntered)

# Fan Widgets
f1_slider = Scale(root, command=main.set_fan1, from_=100, to=0, label='Fan 1', length=450, width=30, font=('Avenir LT Std 35 Light', 10))
f2_slider = Scale(root, command=main.set_fan2, from_=100, to=0, label='Fan 2', length=450, width=30, font=('Avenir LT Std 35 Light', 10))

# Motor Widget
motor_label = Label(root, text='Motor Position: \t0', font=('Avenir LT Std 35 Light', 30))

# FPS Widget - for debugging
fps_label = Label(root, text='0 FPS', font=('Avenir LT Std 35 Light', 15))
root.bind('<KeyPress>', toggle_fps)

# --------- Drawing to the Screen ---------
canvasWidget.place(x=800, y=0)
title_label.place(x=10, y=10)
fps_label.place(x=10, y=100)
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

toggle_pid()

def animate(i):
    global current_loop_timestamp, last_loop_timestamp, show_fps
    if show_fps:
        last_loop_timestamp=current_loop_timestamp
        current_loop_timestamp=time.time()
        fps = 1/(current_loop_timestamp-last_loop_timestamp)
        fps_str = 'FPS: ' + str(fps)[0:4]
        fps_label.config(text=fps_str)
    else:
        fps_label.config(text='')
    main.loop()
    ax1.clear()
    ax1.plot(xAxis, data)
    dia_str = 'Diameter: \t' + str(data[MAX_LENGTH-1]) + 'mm'
    diameter_label.config(text=dia_str)
    return ax1.lines[0],

def add_random_data():
    num = random.randrange(1023)
    add_data(num)

def add_data(num):
    data.append(num)
    if len(data) > MAX_LENGTH:
        del data[0]

ani = animation.FuncAnimation(fig, animate, interval=1, blit=True)
root.mainloop()
