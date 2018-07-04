import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial
import keyboard

ser=serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

MAX_LENGTH=60
TARGET_DIAMETER=3
TOLERANCE=0.05

fig = plt.figure(num='Sensor Data')
plt.style.use('ggplot')
ax = fig.add_subplot(1,1,1)


x_axis 			= np.arange(0, MAX_LENGTH, 1)
perfection 		= np.full(MAX_LENGTH, TARGET_DIAMETER)
high_tolerance 	= np.full(MAX_LENGTH, TARGET_DIAMETER+TOLERANCE)
low_tolerance 	= np.full(MAX_LENGTH, TARGET_DIAMETER-TOLERANCE)
data 			= np.full(MAX_LENGTH, 0)

last_time=0
this_time=1

def addData(n):
	global data
	n_array=np.array([n])
	data=np.delete(data, MAX_LENGTH-1)
	data=np.append(n_array, data)

def animate(i):
	global last_time
	global this_time
	print(1/(this_time-last_time))
	last_time=this_time
	this_time=time.time()
	
	global data

	#get new sensor value
	ser.write(bytes('$SV?\n', 'utf-8'))
	sensor_str = ser.readline()
	if len(sensor_str) > 0:
		sensor = int(sensor_str) * 0.00488758553
		addData(sensor)

	#check for commands to send to Arduino
	if keyboard.is_pressed('ctrl'):
		command = input(">>> ").lower()
		if command!='' and command !='\n':
			if command[0]!='$':
				command = '$' + command
			command = command + '\n'
			ser.write(bytes(command, 'utf-8'))

	#redraw graph
	ax.clear()
	line1, = ax.plot(x_axis, data, color='blue', lw=2)
	line2, = ax.plot(x_axis, perfection, color='green', lw=2)
	line3, = ax.plot(x_axis, high_tolerance, color='red', lw=2)
	line4, = ax.plot(x_axis, low_tolerance, color='red', lw=2)
	ax.set_ylabel('Diameter (mm)')
	ax.set_ylim(2.7,3.3)
	ax.set_xlim(MAX_LENGTH,0) #invert x-axis

	return (ax.lines)

def rotateMotor(steps):
	if(steps>=0):
		command_string='$SF:' + str(abs(steps)) + '\n'
		MOTOR_POS += steps
		ser.write(bytes(command_string, 'utf-8'))
	if(steps<0):
		command_string='$SB:' + str(abs(steps)) + '\n'
		MOTOR_POS += steps
		ser.write(bytes(command_string, 'utf-8'))#rotates the stepper motor a number of steps

ani=animation.FuncAnimation(fig, animate, interval=1, blit=True)
plt.show()
