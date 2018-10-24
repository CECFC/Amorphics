import tkinter as tk
from tkinter import Label, Button, StringVar, Entry, Scale

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.animation as animation
import math
import random
import sys
import datetime

import main
import log

current_loop_timestamp=1 # stores the timestamp of the current animation loop execution
last_loop_timestamp=0 # stores the timestamp of the previous animation loop execution

# MAX_LENGTH = 60 # How many data values to keep before dumping
# data = [] # Stores the sensor data to be graphed 
# xAxis = [] # The x-axis grid (1...MAX_LENGTH)
# update_graph = True

win = None

# Initialize the data
# for i in range(MAX_LENGTH):
        # xAxis.append(i)
        # data.append(0)

def toggle_pause():
    print('Toggled (does nothing yet...)')

def reset_log():
    log.log = []
    log.x_axis = []

def plot_graph(date, batch, percent, type_str):
	print("plot_graph()")
	log.plot_pdf(date, batch, percent, type_str)
	win.destroy()
	

def save_graph():
	global win
	date = datetime.datetime.now().date()
	date_str = str(date.month) + '/' + str(date.day) + '/' + str(date.year)[2:]
	if update_graph:
		toggle_pause()
	# Variables
	date = StringVar()
	date.set(date_str)
	batch = StringVar()
	batch.set('1')
	type_str = StringVar()
	type_str.set('PLA')
	percent = StringVar()
	percent.set('12')
	
	win = tk.Toplevel()
	win.wm_title("Save Graph")
	win.geometry('400x500+0+0')
	
	date_label = Label(win, text="Date", font =('Roboto Slab', 20), )
	date_label.pack()
	date_entry = Entry(win, textvariable=date, font=('Roboto Slab', 20))
	date_entry.pack(pady=10)
	
	batch_label = Label(win, text="Batch #", font=('Roboto Slab', 20))
	batch_label.pack()
	batch_entry = Entry(win, textvariable=batch, font=('Roboto Slab', 20))
	batch_entry.pack(pady=10)
	
	type_label = Label(win, text="Plastic Type", font=('Roboto Slab', 20))
	type_label.pack()
	type_entry = Entry(win, textvariable=type_str, font=('Roboto Slab', 20))
	type_entry.pack(pady=10)
	
	percent_label = Label(win, text="% of Pellets", font=('Roboto Slab', 20))
	percent_label.pack()
	percent_entry = Entry(win, textvariable=percent, font=('Roboto Slab', 20))
	percent_entry.pack(pady=10)
	
	save_button = Button(win, command=lambda: plot_graph(date.get(), batch.get(), percent.get(), type_str.get()), text='Save', width=10, font=('Roboto Slab', 20))
	save_button.pack(pady=10)

# Root Widget
fig = plt.figure()
root = tk.Toplevel()
root.geometry('1450x600+0+0')
root.title('Amorphics')
root.protocol('WM_DELETE_WINDOW', exit)
title_label = Label(root, text='AMORPHICS', font=('Aller Display', 70))


# Graph Widgets 
diameter_label = Label(root, text='Diameter: \t0', font=('Roboto Slab', 30))
graph_pause_button = Button(root, text='Pause', width=10, command=toggle_pause, font=('Roboto Slab', 20))
reset_button = Button(root, text='Reset Log', width=10, command=log.reset, font=('Roboto Slab', 20))
save_button = Button(root, text='Save Graph', width=10, command=save_graph, font=('Roboto Slab', 20))
canvas = FigureCanvasTkAgg(fig, master=root)
canvasWidget = canvas.get_tk_widget()

# Terminal Widgets
terminal_label = Label(root, text='Console', font=('Roboto Slab', 30))
current_command = StringVar()
current_command.set('')
terminal_entry = Entry(root, textvariable=current_command, font=('Roboto Mono', 20))
terminal_entry.config(width='32')
def commandEntered(p0):
    main.execute_command(terminal_entry.get())
    terminal_entry.delete(0, 'end')
terminal_entry.bind('<Return>', commandEntered)

# Fan Widgets
f1_slider = Scale(root, command=main.set_fan1, from_=100, to=0, label='Fan 1', length=570, width=30, font=('Roboto Slab', 10))
f2_slider = Scale(root, command=main.set_fan2, from_=100, to=0, label='Fan 2', length=570, width=30, font=('Roboto Slab', 10))

# Motor Widget
motor_label = Label(root, text='Motor Position: \t0', font=('Roboto Slab', 30))

# --------- Drawing to the Screen ---------
# canvasWidget.place(x=800, y=0)
title_label.place(x=10, y=10)
motor_label.place(x=10, y=100)
f1_slider.place(x=550, y=15)
f2_slider.place(x=650, y=15)
diameter_label.place(x=800, y=480)
graph_pause_button.place(x=800, y=540)
reset_button.place(x=1000, y=540)
save_button.place(x=1200, y=540)
terminal_label.place(x=10, y=500)
terminal_entry.place(x=10, y=550)

# ax1 = fig.add_subplot(1,1,1)
# line, = ax1.plot(xAxis, data)




# ani = animation.FuncAnimation(fig, animate, interval=0, blit=True)
root.mainloop()
