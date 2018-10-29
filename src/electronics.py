from sys import platform

debug = True

if platform == "linux" or platform == "linux2":
    debug = False

if not debug:
    import RPi.GPIO as GPIO
    import smbus
    import time

    GPIO.setwarnings(False) #ain't nobody need no warnin'

    ADC_I2C_ADDR = 0x49 #I2C address of the ADC
    PWM_FREQ = 100 #PWM frequency to use for controlling fan speed
    STP_PIN = 20 #GPIO pin connected to the STP pin of the BED
    DIR_PIN = 21 #GPIO pin connected to the DIR pin of the BED
    FAN1_PIN = 19 #GPIO pin connected to the channel 1 enable on the L298
    FAN2_PIN = 13 #GPIO pin connected to the channel 2 enable on the L298

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

    # States
    motor_pos = 0
    fan1_state = 0
    fan2_state = 0



def getSensorData():
    if debug:
        x = 0
    else:
        adc_i2c_bytearray = bus.read_i2c_block_data(ADC_I2C_ADDR, 0x00, 2)
        adc_numeric=adc_i2c_bytearray[0]*256 + adc_i2c_bytearray[1]
        if adc_numeric > 32767:
            adc_numeric -= 65536
        adc_mm= adc_numeric * 0.00244140625
        return adc_mm

def setFan(index, magnitude):
    value = float(magnitude)
    print("[electronics] Setting fan", index, "to", magnitude)
    if not debug:
        if index == 1:
            fan1_pwm.ChangeDutyCycle(value)
        elif index == 2:
            fan2_pwm.ChangeDutyCycle(value)
        else:
            print("Invalid fan index")

def turnMotor(steps):
    global motor_pos
    print("[electronics] Turning motor", steps, "steps")
    if not debug:
        x = 0
        if steps<0:
            GPIO.output(DIR_PIN, GPIO.HIGH)
            for i in range(abs(steps)):
                GPIO.output(STP_PIN, GPIO.LOW)
                time.sleep(0.01)
                GPIO.output(STP_PIN, GPIO.HIGH)
                motor_pos-=1
                time.sleep(0.01)
        if steps>0:
            GPIO.output(DIR_PIN, GPIO.LOW)
            for i in range(abs(steps)):
                GPIO.output(STP_PIN, GPIO.LOW)
                time.sleep(0.01)
                GPIO.output(STP_PIN, GPIO.HIGH)
                motor_pos += 1
                time.sleep(0.01)