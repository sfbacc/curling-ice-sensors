import Adafruit_DHT
import time
import datadog

DATADOG_API_KEY='565893d17f4370e4474975a941c5a468'
DATADOG_API_URL='https://api.datadoghq.com/api/v1/series?api_key=' + DATADOG_API_KEY
datadog.initialize(api_key=DATADOG_API_KEY)



def send_temperature_to_datadog(name, value):
    datadog.api.Metric.send(
        metric='sfbacc.temperature',
        points=value,
        tags=['sensor:' + name]
    )
def send_humidity_to_datadog(name, value):
    datadog.api.Metric.send(
        metric='sfbacc.humidity',
        points=value,
        tags=['sensor:' + name]
    )
    
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN1 = 4
DHT_PIN2 = 9

def measure_and_send():
    humidity1, temperature1 = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN1)
    humidity2, temperature2 = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN2)
    
    if humidity1 is not None and temperature1 is not None and humidity2 is not None and temperature2 is not None:
        send_temperature_to_datadog('sensor-3T', temperature1)
        send_humidity_to_datadog('sensor-3H', humidity1)
        send_temperature_to_datadog('sensor-4T', temperature2)
        send_humidity_to_datadog('sensor-4H', humidity2)
       
        print("Temp1={0:0.1f}*C Humidity1={1:0.1f}%".format(temperature1, humidity1))
        print("Temp2={0:0.1f}*C Humidity2={1:0.1f}%".format(temperature2, humidity2))
    else:
        print("fail")
       
if __name__ == '__main__':
    while True:
        measure_and_send()
        time.sleep(10)   
