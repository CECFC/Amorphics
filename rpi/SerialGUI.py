import serial
import sys
import os
import time

SERIAL_NAME = "/dev/cu.usbserial-1440"
# SERIAL_NAME = "/dev/ttyUSB0"

while True:
    print("-------------SERIAL CONTROLLER----------")
    print("ADJUST FAN SPEED -> F[1/2]:[Speed]")
    print("TURN MOTOR       -> S[F/R]:[Num Steps]")
    print("----------------------------------------")
    command = input(">>> ")

    time.sleep(2)
    sys.stdout.flush()
    os.system('clear')
