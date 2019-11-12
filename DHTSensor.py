# DHT sensor imports
import Adafruit_DHT
import  RPi.GPIO as GPIO
import os
import time
# Humidity sensor static variables


def readTemperature(DHT_PIN):
    try:
        DHT_SENSOR = Adafruit_DHT.DHT22
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

        if humidity is not None and temperature is not None:
            temperature = temperature * 9 / 5.0 + 32
            outputText = temperature
        else:
            outputText = "Failed to retrieve temperature from sensor"

        return outputText
    except Exception as e:
        print("DHTSensor.py error", e)
        return "Error reading sensor on port" + str(DHT_PIN) + e

def readHumidity(DHT_PIN):
    try:
        DHT_SENSOR = Adafruit_DHT.DHT22
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

        if humidity is not None and temperature is not None:
            outputText = humidity
        else:
            outputText = "Failed to retrieve humidity from sensor"

        return outputText
    except Exception as e:
        print ("DHTSensor.py error",e)
        return "Error reading sensor on port" + str(DHT_PIN) + e

# test code for this module
# GPIO.setmode(GPIO.BCM)
# while True:
#     print(readTemperature(27))
#     time.sleep(2)