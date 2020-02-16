import Adafruit_DHT
import time
import datetime
import json
import logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4


clientId = "raspberry"
host = "a3g6ufdmmeh2vi-ats.iot.us-west-2.amazonaws.com"
port = "8883"

rootCAPath = './creds/root-CA.crt'
privateKeyPath = "./creds/raspberrypi1.private.key"
certificatePath = "./creds/raspberrypi1.cert.pem"

print(host)

# logger = logging.getLogger("AWSIoTPythonSDK.core")
# logger.setLevel(logging.DEBUG)
# streamHandler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# streamHandler.setFormatter(formatter)
# logger.addHandler(streamHandler)


# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None

myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect to AWS IoT
myAWSIoTMQTTClient.connect()

time.sleep(2)

topic = "raspberry/dht22"

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second
        calendar_date = str(year) + "-" + str(month) + "-" + str(day)
        calendar_time = str(hour) + "-" + str(minute) + "-" + str(second)
        celsius = round(temperature, 2)
        fahrenheit = round(temperature*9/5+32,2)
        epoch = int(round(time.time(),0))
        humidity = round(humidity, 2)

        message = {
            "calendar_date" : calendar_date,
            "calendar_time" : calendar_time,
            "epoch" : epoch,
            "celsius": celsius,
            "fahrenheit": fahrenheit,
            "humidity": humidity
        }

        messageJson = json.dumps(message)

        print(messageJson)

        myAWSIoTMQTTClient.publish(topic, messageJson, 1)

    else:
        print("Failed to retrieve data from humidity sensor")
    
    time.sleep(60*5) # sleep for specified number of seconds before sending data again