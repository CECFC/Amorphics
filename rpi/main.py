import time
import sys
import smbus
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import keyboard

GPIO.setwarnings(False) #ain't nobody need no warnin'

#configuration variables
X_AXIS_LENGTH = 60 #how long to make the x-axis of the graph

TARGET_DIAMETER=3 #the diameter the controller is aiming for
DIAMETER_TOLERANCE = 0.07 #acceptable deviation from target diameter
Y_LOWER_LIM = 2.5 #lower y bound of the plot
Y_UPPER_LIM = 3.5 #upper y bound of the plot
PLOT_NAME = 'Sensor Data' #name of the matplotlib window

ADC_I2C_ADDR = 0x49 #I2C address of the ADC
STP_PIN = 20 #GPIO pin connected to the STP pin of the BED
DIR_PIN = 21 #GPIO pin connected to the DIR pin of the BED

K_p = 2 #constant for the proportional component of the control loop
K_i = 2 #constant for the integral component of the control loop
K_d = 0 #constant for the derivative component of the control loop
PID_WINDUP_LIMIT = 100 #maximum magnitude of the value in the pid integral term

CURSOR_UP_ONE='\x1b[1A'
ERASE_LINE='\x1b[2K'

FPS_DEBUG_ENABLE 	= True #print current FPS to console
SENSOR_DEBUG_ENABLE = True #print current diameter to console
MOTOR_DEBUG_ENABLE 	= True #print current motor position to console
PID_DEBUG_ENABLE	= True #print PID information to console

#state variables
PID_ENABLE = False #whether or not to compute and execute control loop
pid_accumulator=0

xAxis = [] #array of x values for the plot
data = [] #for plot of realtime sensor values
target = [] #for plot of target line
top_tolerance=[] #for plot of maximum allowable diameter
bottom_tolerance=[] #for plot of minimum allowable diameter

FAN1_STATE = 0 #state of fan1
FAN2_STATE = 0 #state of fan2
MOTOR_POS = 0 #rotational state of the stepper motor
CURRENT_FPS = 0 #current framerate of the plot

current_loop_timestamp=1 #stores the timestamp of the current animation loop execution
last_loop_timestamp=0 #stores the timestamp of the previous animation loop execution

#GPIO init
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STP_PIN, GPIO.OUT)

#I2C init
bus=smbus.SMBus(1)
bus.write_byte(0x49, 0x0C)
time.sleep(0.5)

#plot init
fig = plt.figure(num='Sensor Data')
ax1 = fig.add_subplot(1,1,1)
ax2 = fig.add_subplot(1,1,1)
ax3 = fig.add_subplot(1,1,1)
ax4 = fig.add_subplot(1,1,1)

def initializeData():
    for i in range(X_AXIS_LENGTH):
        xAxis.append(i)
        data.append(None)
        target.append(TARGET_DIAMETER)
        top_tolerance.append(TARGET_DIAMETER+DIAMETER_TOLERANCE)
        bottom_tolerance.append(TARGET_DIAMETER-DIAMETER_TOLERANCE)

def clearlines(num_of_lines):
	for i in range(0, num_of_lines):
		sys.stdout.write(CURSOR_UP_ONE)
		sys.stdout.write(ERASE_LINE)
		
def print_status():
	global PID_ENABLE
	global CURRENT_FPS
	objects=0
	if FPS_DEBUG_ENABLE:
		objects+=1
	if SENSOR_DEBUG_ENABLE:
		objects+=1
	if MOTOR_DEBUG_ENABLE:
		objects+=1
	if PID_DEBUG_ENABLE:
		objects+=4
		
	if objects>0:
		clearlines(objects+1)
		print("=====STATUS=====")
		
	if SENSOR_DEBUG_ENABLE:
		print("DIA: "+str(data[0]))
	if MOTOR_DEBUG_ENABLE:
		print("MTR: "+str(MOTOR_POS))
	if PID_DEBUG_ENABLE:
		status=""
		if PID_ENABLE:
			status="ENABLED"
		if not PID_ENABLE:
			status="DISABLED"
		print("PID: " + status)
		print("K_p: " + str(K_p))
		print("K_i: " + str(K_i))
		print("K_d: " + str(K_d))
		
	if FPS_DEBUG_ENABLE:
		print("FPS: "+str(CURRENT_FPS))

def animate(i):
	global CURRENT_FPS
	global PID_ENABLE	
	if FPS_DEBUG_ENABLE: #get current framerate if enabled
		global current_loop_timestamp
		global last_loop_timestamp
		CURRENT_FPS = 1/(current_loop_timestamp-last_loop_timestamp)
		last_loop_timestamp=current_loop_timestamp
		current_loop_timestamp=time.time()
	
	#check for new commands from user
	if keyboard.is_pressed('ctrl'):
		command = input(">>> ").lower()
		clearlines(1)
		parsed = ""
		if command != "":
			if command[0] == 'f' and len(command)>3:
				magnitudeStr = command[3:]
				if command[1] == '1':
					pass
					#update fan1 state
				elif command[1] == '2':
					pass
					#update fan2 state
			elif command[0] == 's' and len(command)>3:
				magnitudeStr = command[3:]
				mag = int(magnitudeStr)
				if command[1] == 'f':
					rotateMotor(mag)
				elif command[1] == 'b':
					rotateMotor(-mag)
			elif command == "enable":
				PID_ENABLE = True
			elif command == "disable":
				PID_ENABLE = False
				
	#get new data from sensor			
	adc_i2c_bytearray = bus.read_i2c_block_data(ADC_I2C_ADDR, 0x00, 2)
	adc_numeric=adc_i2c_bytearray[0]*256 + adc_i2c_bytearray[1]
	if adc_numeric > 32767:
		adc_numeric -= 65536
	adc_mm= adc_numeric * 0.00244140625
	if adc_numeric>=0 and adc_numeric<2048:	
		addData(adc_mm)

	
	#update plot	
	ax1.clear()
	ax2.plot(xAxis, target, color="green")
	ax3.plot(xAxis, top_tolerance, color="red")
	ax4.plot(xAxis, bottom_tolerance, color="red")
	ax1.plot(xAxis, data, color="blue")
	
	#reset x and y limits
	ax1.set_ylim(Y_LOWER_LIM, Y_UPPER_LIM)
	ax1.set_xlim(X_AXIS_LENGTH,0)
	ax2.set_ylim(Y_LOWER_LIM, Y_UPPER_LIM)
	ax2.set_xlim(X_AXIS_LENGTH,0)
	ax3.set_ylim(Y_LOWER_LIM, Y_UPPER_LIM)
	ax3.set_xlim(X_AXIS_LENGTH,0)
	ax4.set_ylim(Y_LOWER_LIM, Y_UPPER_LIM)
	ax4.set_xlim(X_AXIS_LENGTH,0)
	plt.ylabel('Diameter (mm)')
	
	
	#set background color to yellow if outside tolerance
	if data[0]!=None:
		if abs(data[0]-TARGET_DIAMETER) > DIAMETER_TOLERANCE:
				ax1.set_facecolor('yellow')
				ax2.set_facecolor('yellow')
				ax3.set_facecolor('yellow')
				ax4.set_facecolor('yellow')
		else:
			ax1.set_facecolor('white')
			ax1.set_facecolor('white')
			ax1.set_facecolor('white')
			ax1.set_facecolor('white')
	
	#run control loop if enabled
	if PID_ENABLE:
		checkSteps(data[0])
		
	print_status()
			
def rotateMotor(steps):
	global MOTOR_POS
	if steps<0:
		GPIO.output(DIR_PIN, GPIO.HIGH)
		for i in range(abs(steps)):
			GPIO.output(STP_PIN, GPIO.LOW)
			time.sleep(0.01)
			GPIO.output(STP_PIN, GPIO.HIGH)
			MOTOR_POS-=1
			time.sleep(0.01)
	if steps>0:
		GPIO.output(DIR_PIN, GPIO.LOW)
		for i in range(abs(steps)):
			GPIO.output(STP_PIN, GPIO.LOW)
			time.sleep(0.01)
			GPIO.output(STP_PIN, GPIO.HIGH)
			MOTOR_POS+=1
			time.sleep(0.01)

def addData(num):
    data.insert(0, num)
    if len(data) > X_AXIS_LENGTH:
        del data[X_AXIS_LENGTH]

def checkSteps(sensor):
	global K_p
	global K_i
	global K_d
	global pid_accumulator
	global PID_ENABLE
	error=sensor-TARGET_DIAMETER
	if abs(error)<1:
		if pid_accumulator>=-PID_WINDUP_LIMIT and pid_accumulator<=PID_WINDUP_LIMIT:
			pid_accumulator=pid_accumulator + error
		steps = (K_p * error + K_i * pid_accumulator)
		rotateMotor(int(steps))
	else:
		PID_ENABLE=False

ani = animation.FuncAnimation(fig, animate, interval=1, init_func=initializeData)
plt.show()
