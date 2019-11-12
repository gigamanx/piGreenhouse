#global imports
import time
import board
import sys
import RPi.GPIO as GPIO
import WriteThingSpeak
import smbus2
import busio
import datetime


#local imports
import DHTSensor #For temp/humidity sensor
from gpiozero import LightSensor #For light sensor
import adafruit_tca9548a #For i2c multiplexer
import adafruit_ads1x15.ads1115 as ADS #For analog multiplexer
from adafruit_ads1x15.analog_in import AnalogIn #For analog multiplexer

###STATIC GPIO.BCM PIN SETUP FOR RasberryPi###
DHT_TEMP1_PIN = 27
LIGHT_PIN = 4
RELAY_SW_1 = 6
RELAY_SW_2 = 13
RELAY_SW_3 = 19
RELAY_SW_4 = 26

#the raspberry pi bus number (probably located on /dev/i2c-1)
rpi_bus_number = 1
multiplexer_address = 0x70
I2C_ch_0 = 0B00000001
I2C_ch_1 = 0B00000010
I2C_ch_2 = 0B00000100
I2C_ch_3 = 0B00001000
I2C_ch_4 = 0B00010000
I2C_ch_5 = 0B00100000
I2C_ch_6 = 0B01000000
I2C_ch_7 = 0B10000000
bus = smbus2.SMBus(rpi_bus_number)
i2c = busio.I2C(board.SCL, board.SDA)

###STATIC PIN SETUP FOR RasberryPi###
GPIO.setmode(GPIO.BCM)




HeatingOn = False
HeatStart = 0
HeatEnd = 0
CoolingOn = False
WateringOn = False

#Set relay switch defaults
pinList = [RELAY_SW_1,RELAY_SW_2,RELAY_SW_3,RELAY_SW_4]
for i in pinList:
    print("Setting pin for relay...",i)
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)
    time.sleep(0.1)

#Turn on/off heat lamp
def toggleHeat(switch="off"):
    try:
        if (switch=="off"):
            GPIO.output(RELAY_SW_4, GPIO.HIGH)
            print("Switching off heating...")
            HeatEnd = time.time()
        else:
            GPIO.output(RELAY_SW_4, GPIO.LOW)
            print("Switching on heating...")
            HeatStart = time.time()
        time.sleep(0.1)
    except:
        print("Error in Relay Board Module during ToggleHeat")
#End Turn on/off heat lamp

def toggleCool(switch="off"):
    try:
        if (switch=="off"):
            GPIO.output(RELAY_SW_1, GPIO.HIGH)
            print ("Switching off cooling...")
        else:
            GPIO.output(RELAY_SW_1, GPIO.LOW)
            print ("Switching on cooling...")
        time.sleep(0.1)
    except:
        print("Error in Relay Board Module during toggleCool")
        print(sys.exc_info()[0])

def toggleWatering(switch="off"):
    try:
        if (switch=="off"):
            GPIO.output(RELAY_SW_3, GPIO.HIGH)
            print ("Switching off watering...")
        else:
            GPIO.output(RELAY_SW_3, GPIO.LOW)
            print ("Switching on watering...")
        time.sleep(0.1)
    except:
        print("Error in Relay Board Module during toggleCool")
        print(sys.exc_info()[0])

def readMoisture():
    try:
        # This switches to i2c multiplexer channel 0
        bus.write_byte(multiplexer_address, I2C_ch_0)
        ads = ADS.ADS1115(i2c)
        analog0 = AnalogIn(ads, ADS.P0)
        analog1 = AnalogIn(ads, ADS.P1)
        analog2 = AnalogIn(ads, ADS.P2)
        analog3 = AnalogIn(ads, ADS.P3)

        #get the average only if a sensor is detected
        avg: float = 0
        divisible: int = 0
        if (analog0.value > 10000):
            avg += analog0.value
            divisible += 1
        if (analog1.value > 10000):
            avg += analog1.value
            divisible += 1
        if (analog2.value > 10000):
            avg += analog2.value
            divisible += 1
        if (analog3.value > 10000):
            avg += analog3.value
            divisible += 1
        if (avg / divisible > 18000):
            print("Moisture dry", avg/divisible)
        else:
            print("Moisture Detected", avg/divisible)

        print("Moisture Sensors: ", analog0.value, analog1.value, analog2.value, analog3.value)
        return avg/divisible


    except Exception as e:
        print("Error in Analog reader for Moisture ", e)
        return 0

#MAIN PROGRAM
try:
    ###main program loop
    HeatingOn=False
    CoolingOn=False
    WateringOn=False

    #initiate internal air flow
    print("Starting internal fan...")
    GPIO.output(RELAY_SW_2, GPIO.LOW)
    light = LightSensor(LIGHT_PIN)
    time.sleep(0.1)

    while True:
        try:
            currentTemp = DHTSensor.readTemperature(DHT_TEMP1_PIN)
            currentHumidity = DHTSensor.readHumidity(DHT_TEMP1_PIN)
            currentMoisture = readMoisture()

            print("Current Temp: {0:.2f}*F".format(currentTemp))
            print("Current Humidity: {0:.2f}%".format(currentHumidity))
            print("Heating On: ", HeatingOn, "|| Cooling On: ", CoolingOn, "|| Watering On: ", WateringOn)

            time.sleep(0.1)
            #temperature control applications
            if(currentTemp < 72 and HeatingOn == False):
                toggleHeat("on")
                HeatingOn=True
                HeatStart=datetime.datetime.now().replace(microsecond=0)
                WriteThingSpeak.SendData(temp=currentTemp, humidity=currentHumidity, light=light.value, moisture=currentMoisture)
            if(currentTemp > 78 and HeatingOn == True):
                toggleHeat("off")
                HeatingOn=False
                HeatEnd = datetime.datetime.now().replace(microsecond=0)
                print("Time to heat greenhouse: ", HeatEnd - HeatStart)
                WriteThingSpeak.SendData(temp=currentTemp, humidity=currentHumidity, light=light.value, moisture=currentMoisture)
            if (currentTemp > 82 and CoolingOn == False):
                toggleCool("on")
                CoolingOn=True
                WriteThingSpeak.SendData(temp=currentTemp, humidity=currentHumidity, light=light.value, moisture=currentMoisture)
            if (currentTemp < 78 and CoolingOn == True):
                toggleCool("off")
                CoolingOn=False
                WriteThingSpeak.SendData(temp=currentTemp, humidity=currentHumidity, light=light.value, moisture=currentMoisture)
            #Water control applications.
            #Only turn on pump for 10 sec at a time until ground is saturated
            if (currentMoisture < 1000):
                toggleWatering("on")
                time.sleep(10)
                toggleWatering("off")

        except Exception as e:
            toggleHeat("off")
            HeatingOn=False
            toggleCool("off")
            CoolingOn=False
            print ("Error in main program...", e)

#       polling the system every 15 seconds
        time.sleep(15)
    ####end main program while loop
except:
    print("Programmed exited with faults")