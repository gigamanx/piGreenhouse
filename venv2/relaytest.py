#this will simply test a 4 chan relay
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)


RELAY_SW_1 = 6
RELAY_SW_2 = 13
RELAY_SW_3 = 19
RELAY_SW_4 = 26


pinList = [RELAY_SW_1,RELAY_SW_2,RELAY_SW_3,RELAY_SW_4]
for i in pinList:
    print("Setting pin for relay...",i)
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)
    time.sleep(0.1)

while True:
    try:

            print("turning off all relays...")
            for i in pinList:
                print("Setting pin for relay using 0...", i)
                GPIO.output(i, GPIO.HIGH)
                time.sleep(1)

            time.sleep(5)

            print("turning on all relays")
            for i in pinList:
                print("Setting pin for relay using 1...", i)
                GPIO.output(i, GPIO.LOW)
                time.sleep(1)
            time.sleep(5)

    except Exception as e:
        print(e)