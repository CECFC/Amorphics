#!/usr/bin/python3
import time
import sys
import gui
import log
import electronics
print("hehe")

# -------- PID LOOP --------
K_p = 2 #constant for the proportional component of the control loop
K_i = 2 #constant for the integral component of the control loop
K_d = 0 #constant for the derivative component of the control loop
PID_WINDUP_LIMIT = 100 #maximum magnitude of the value in the pid integral term

#state variables
PID_ENABLE = False #whether or not to compute and execute control loop
pid_accumulator=0

current_loop_timestamp=1 #stores the timestamp of the current animation loop execution
last_loop_timestamp=0 #stores the timestamp of the previous animation loop execution

# Log file
log_file = open("log.txt", "a")

# Steady Timer
time.sleep(time.time() % 1.0)
start_time = time.time()
frame_interval = 0.5

def set_fan1(value):
    electronics.setFan(1, value)
    
def set_fan2(value):
    electronics.setFan(2, value)


def loop():
    global PID_ENABLE
    global FAN1_STATE, FAN2_STATE
    global start_time
    # print(time.time() - start_time)
	
				
    #get new data from sensor
    sensor_data = electronics.getSensorData()
    if time.time() - start_time >= frame_interval:
        log.log_diameter(sensor_data, frame_interval)
        start_time = time.time()
    gui.add_data(sensor_data)
			
    #update fan speeds
    try:
        fan1_pwm.ChangeDutyCycle(FAN1_STATE)
        fan2_pwm.ChangeDutyCycle(FAN2_STATE)
    except:
        x = 0

    #run control loop if enabled
    if PID_ENABLE:
        checkSteps(data[0])
	
    # Sleep
    # time.sleep(frame_interval - ((time.time() - start_time) % frame_interval))

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

def execute_command(command):
	print('[command]', command)
	if len(command) == 0:
            print("[response] Empty command")
	elif command[0] == 'f':
		if command[1] == '1':
			magnitude = int(command[3:])
			gui.f1_slider.set(magnitude)
		elif command[1] == '2':
			magnitude = int(command[3:])
			gui.f2_slider.set(magnitude)
	elif command[0] == 'm':
		electronics.turnMotor(int(command.split(' ')[1]))
		motor_str = 'Motor Position: \t' + str(electronics.motor_pos)
		gui.motor_label.config(text=motor_str)
	elif command[0] == 's':
            split = command.split(' ')
            date = ''
            batch = ''
            percent = ''
            if len(split) >= 4:
                date = split[1]
                batch = split[2]
                percent = split[3]
            else:
                date = 'test'
                batch = '1'
                percent = '0'
            log.plot_pdf(date, batch, percent)
            
        

def logData(diameter):
    # Diameter is in mm
    gui.add_data(diameter)
    log_file.write(str(diameter)[:5] + "\n")
