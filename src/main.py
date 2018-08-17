import time
import sys
import smbus
import RPi.GPIO as GPIO
import gui

GPIO.setwarnings(False) #ain't nobody need no warnin'

ADC_I2C_ADDR = 0x49 #I2C address of the ADC
PWM_FREQ = 100 #PWM frequency to use for controlling fan speed
STP_PIN = 20 #GPIO pin connected to the STP pin of the BED
DIR_PIN = 21 #GPIO pin connected to the DIR pin of the BED
FAN1_PIN = 19 #GPIO pin connected to the channel 1 enable on the L298
FAN2_PIN = 13 #GPIO pin connected to the channel 2 enable on the L298

K_p = 2 #constant for the proportional component of the control loop
K_i = 2 #constant for the integral component of the control loop
K_d = 0 #constant for the derivative component of the control loop
PID_WINDUP_LIMIT = 100 #maximum magnitude of the value in the pid integral term

CURSOR_UP_ONE='\x1b[1A'
ERASE_LINE='\x1b[2K'

#state variables
PID_ENABLE = False #whether or not to compute and execute control loop
pid_accumulator=0
print("START!")

FAN1_STATE = None #state of fan1
FAN2_STATE = None #state of fan2
MOTOR_POS = 0 #rotational state of the stepper motor
CURRENT_FPS = 0 #current framerate of the plot

current_loop_timestamp=1 #stores the timestamp of the current animation loop execution
last_loop_timestamp=0 #stores the timestamp of the previous animation loop execution

#GPIO init
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STP_PIN, GPIO.OUT)
GPIO.setup(FAN1_PIN, GPIO.OUT)
GPIO.setup(FAN2_PIN, GPIO.OUT)
fan1_pwm = GPIO.PWM(FAN1_PIN, PWM_FREQ)
fan2_pwm = GPIO.PWM(FAN2_PIN, PWM_FREQ)
fan1_pwm.start(0)
fan2_pwm.start(0)

#I2C init
bus=smbus.SMBus(1)
bus.write_byte(0x49, 0x0C)
time.sleep(0.5)

def clearlines(num_of_lines):
	for i in range(0, num_of_lines):
		sys.stdout.write(CURSOR_UP_ONE)
		sys.stdout.write(ERASE_LINE)

def loop():
	global PID_ENABLE
	global FAN1_STATE, FAN2_STATE
	
				
	#get new data from sensor			
	adc_i2c_bytearray = bus.read_i2c_block_data(ADC_I2C_ADDR, 0x00, 2)
	adc_numeric=adc_i2c_bytearray[0]*256 + adc_i2c_bytearray[1]
	if adc_numeric > 32767:
		adc_numeric -= 65536
	adc_mm= adc_numeric * 0.00244140625
	if adc_numeric>=0 and adc_numeric<2048:	
		gui.add_data(adc_mm)
			
	#update fan speeds
	try:
		fan1_pwm.ChangeDutyCycle(FAN1_STATE)
		fan2_pwm.ChangeDutyCycle(FAN2_STATE)
	except:
		x = 0

	#run control loop if enabled
	if PID_ENABLE:
		checkSteps(data[0])
			
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

def set_fan1(value):
	fan1_pwm.ChangeDutyCycle(float(value))

def set_fan2(value):
	fan2_pwm.ChangeDutyCycle(float(value))

def execute_command(command):
	"""
	f1 100
	f2 100
	mf 100
	mb 100
	"""
	print('Executing Command:', command)
	if command[0] == 'f':
		if command[1] == '1':
			magnitude = int(command[3:])
			set_fan1(magnitude)
		elif command[1] == '2':
			magnitude = int(command[3:])
			set_fan2(magnitude)
	elif command[0] == 'm':
		if command[1] == 'f':
			rotateMotor(int(command[3:]))
		elif command[1] == 'b':
			rotateMotor(-int(command[3:]))
