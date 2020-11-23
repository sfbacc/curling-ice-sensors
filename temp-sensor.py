import time
import datetime
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
    
    
temp_sensor_1 = '/sys/bus/w1/devices/28-0301a2791250/w1_slave'
temp_sensor_2 = '/sys/bus/w1/devices/28-0301a279c9a7/w1_slave'

def read_temp_raw(ttsensor):
    file = open(ttsensor, 'r')
    lines = file.readlines()
    file.close
    return lines

def read_temp(tsensor):
    lines = read_temp_raw(tsensor)
    while lines[0].strip()[-3:] != 'YES':
        sleep(0.2)
        lines = read_temp_raw()
        
    temp_result = lines[1].find('t=')
    
    if temp_result != -1:
        temp_string = lines[1].strip()[temp_result + 2:]
        temp = float(temp_string)/1000.0
        return temp
   
while True:
    sensor1_data = read_temp(temp_sensor_1)
    sensor2_data = read_temp(temp_sensor_2)

    full_datetime = datetime.datetime.now().strftime('%m %d %Y %H:%M:%S')
    print(full_datetime, 'sensor1: ',sensor1_data, 'sensor2: ', sensor2_data)
    send_temperature_to_datadog('sensor-1', sensor1_data)
    send_temperature_to_datadog('sensor-2', sensor2_data)
 
     
    time.sleep(60)
    
        

