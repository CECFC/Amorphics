import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial
import keyboard

"""
======Stuff to Know======
Mac Serial Name: /dev/cu.usbserial-1440
Pi Serial Name: /dev/ttyUSB0
"""
#configuration variables
MAX_LENGTH = 60
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1) 

#set up the plot
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax2 = fig.add_subplot(1,1,1)
ax3 = fig.add_subplot(1,1,1)
ax4 = fig.add_subplot(1,1,1)

#state variables
USEPID = False
data = []
xAxis = []
perfect = []
top_tolerance=[]
bottom_tolerance=[]

FAN1_STATE = 0 
FAN2_STATE = 0
MOTOR_POS = 0

this_time=1
last_time=0

def initializeData():
    for i in range(MAX_LENGTH):
        xAxis.append(i)
        data.append(2.5)
        perfect.append(3)
        top_tolerance.append(3.05)
        bottom_tolerance.append(2.95)

def animate(i):
	global this_time
	global last_time
	print(1/(this_time-last_time))
	last_time=this_time
	this_time=time.time()
	
	
	global FAN1_STATE
	global FAN2_STATE
	global MOTOR_POS
	global USEPID
	if keyboard.is_pressed('ctrl'):
		command = input(">>> ").lower()
		parsed = ""
		if command != "":
			if command[0] == 'f' and len(command)>3:
				magnitudeStr = command[3:]
				if command[1] == '1':
					FAN1_STATE = int(magnitudeStr)
					parsed = '$F1:' + magnitudeStr + '\n'
				elif command[1] == '2':
					FAN2_STATE = int(magnitudeStr)
					parsed = '$F2:' + magnitudeStr + '\n'
			elif command[0] == 's' and len(command)>3:
				magnitudeStr = command[3:]
				mag = int(magnitudeStr)
				if command[1] == 'f':
					rotateMotor(mag)
				elif command[1] == 'b':
					rotateMotor(-mag)
			elif command == "enable":
				USEPID = True
			elif command == "disable":
				USEPID = False
			else:
				parsed = command
		print(parsed)
		parsed=parsed + '\n'
		ser.write(bytes(parsed, 'utf-8'))
		
	ax1.clear()
	ax2.plot(xAxis, perfect, color="green")
	ax3.plot(xAxis, top_tolerance, color="red")
	ax4.plot(xAxis, bottom_tolerance, color="red")
	ax1.plot(xAxis, data, color="blue")
	
	ax1.set_ylim(2.5,3.5)
	ax1.set_xlim(MAX_LENGTH,0)
	ax2.set_ylim(2.5,3.5)
	ax2.set_xlim(MAX_LENGTH,0)
	ax3.set_ylim(2.5,3.5)
	ax3.set_xlim(MAX_LENGTH,0)
	ax4.set_ylim(2.5,3.5)
	ax4.set_xlim(MAX_LENGTH,0)
	
	plt.ylabel('Diameter (mm)')
	
	ser.write(bytes('$SV?\n', 'utf-8'))
	line = ser.readline()
	sensor = 0
	sensor_str = line
	if len(sensor_str) > 0:
		sensor = int(sensor_str) * 0.00488758553
		#print(sensor)
	addData(sensor)
	
	if USEPID:
		checkSteps(sensor)
def rotateMotor(steps):
	global MOTOR_POS
	if(steps>=0):
		command_string='$SF:' + str(abs(steps)) + '\n'
		MOTOR_POS += steps
		ser.write(bytes(command_string, 'utf-8'))
	if(steps<0):
		command_string='$SB:' + str(abs(steps)) + '\n'
		MOTOR_POS += steps
		ser.write(bytes(command_string, 'utf-8'))

def addData(num):
    data.insert(0, num)
    if len(data) > MAX_LENGTH:
        del data[60]

def checkSteps(sensor):
	k = 5
	steps = (k * (sensor-3))
	print(int(steps))
	rotateMotor(int(steps))

initializeData()

ani = animation.FuncAnimation(fig, animate, interval=1)
plt.show()
