import http.client, urllib
from urllib.parse import urlencode, quote_plus
import thingspeak
import time

API_KEY="NHD6B1QL37OFWNK1"

def SendData(temp=0,humidity=0,light=0,moisture=0):

    try:
        ch = thingspeak.Channel(1, API_KEY)
        ch.update({"field1": temp, "field2": humidity, "field5": light, "field6": moisture})
    except Exception as e:
        print("ThingSpeak connection failed", e)


#test program
#SendData(32,50)