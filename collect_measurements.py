import time
import datetime
import sys
import configparser
import json
import Adafruit_DHT
import datadog
from config_manager import load_settings
from meteocalc import dew_point
datadog.initialize()

METRIC_TEMPERATURE = 'sfbacc.temperature'
METRIC_HUMIDITY = 'sfbacc.humidity'
METRIC_DEWPOINT = 'sfbacc.dewpoint'
DHT_SENSOR = Adafruit_DHT.DHT22
SENSOR_1_ID = '/sys/bus/w1/devices/28-0301a279a2cc/w1_slave'
SENSOR_2_ID = '/sys/bus/w1/devices/28-3c01b556cfa8/w1_slave'
SENSOR_3_ID = '/sys/bus/w1/devices/28-3c01b5562191/w1_slave'
SENSOR_4_ID = '/sys/bus/w1/devices/28-3c01b55698c0/w1_slave'
SENSOR_5_ID = 4
SENSOR_6_ID = 22
temperature_5_list = {'temp': [], 'humid': []}
temperature_6_list = {'temp': [], 'humid': []}


def good_value(h_value, t_value, list):
    if h_value or t_value is not None:
        # check for any data spike by comparing against running average
        if 10 < h_value < 90 and -10 < t_value < 40:
            # check if temp and humid are in reasonable range
            if len(list['temp']) < 10:
                # build list at start
                list['humid'].append(h_value)
                list['temp'].append(t_value)
                return False
            else:
                t_ave = sum(list['temp'])/len(list['temp'])
                h_ave = sum(list['humid'])/len(list['humid'])
                if abs(t_ave - t_value) < 2 and abs(h_ave - h_value) < 2:
                    # check for spike in data
                    list['temp'].pop(0)
                    list['temp'].append(t_value)
                    list['humid'].pop(0)
                    list['humid'].append(h_value)
                    return True
        return False
    return False


def read_DS18B20_temp(sensor_name):
    with open(sensor_name, 'r') as f:
        lines = f.readlines()
    temp_result = lines[1].find('t=')
    if temp_result != -1:
        temp_string = lines[1].strip()[temp_result + 2:]
        temp = float(temp_string)/1000.0
        return temp
    return


def read_DHT22_temp_hum(list_name, sensor_name):
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, sensor_name)
    if good_value(humidity, temperature, list_name) is True:
        humidity = round(humidity, 5)
        temperature = round(temperature, 5)
        dewpoint = round(dew_point(temperature, humidity), 5)
        return humidity, temperature, dewpoint
    else:
        print('bad', humidity, temperature)
        return None, None, None


def send_metric(metric, value, tags: dict):
    if value is not None:
        response = datadog.api.Metric.send(
            metric=metric,
            points=value,
            tags=list(map(lambda kv: f'{kv[0]}:{kv[1]}', tags.items()))
        )

        if response['status'] != 'ok':
            print('Error: ' + json.dumps(response))


def measure_and_send(settings: configparser.ConfigParser):
    # collect readings from sensors
    temperature1 = read_DS18B20_temp(SENSOR_1_ID)
    temperature2 = read_DS18B20_temp(SENSOR_2_ID)
    temperature3 = read_DS18B20_temp(SENSOR_3_ID)
    temperature4 = read_DS18B20_temp(SENSOR_4_ID)
    humidity5, temperature5, dewpoint5 = read_DHT22_temp_hum(temperature_5_list, SENSOR_5_ID)
    humidity6, temperature6, dewpoint6 = read_DHT22_temp_hum(temperature_6_list, SENSOR_6_ID)
    # print values collected
    full_datetime = datetime.datetime.now().strftime('%m %d %Y %H:%M:%S')
    print('\n', full_datetime,)
    print('ice_temp: ', temperature1, temperature2, temperature3, temperature4)
    print('airtemp: ', temperature5, temperature6)
    print('dewpoint: ', dewpoint5, dewpoint6)
    print('humidity: ', humidity5, humidity6)
    # send values to DataDog
    send_metric(METRIC_TEMPERATURE, temperature1, dict(settings['sensor_1'].items()))
    send_metric(METRIC_TEMPERATURE, temperature2, dict(settings['sensor_2'].items()))
    send_metric(METRIC_TEMPERATURE, temperature3, dict(settings['sensor_3'].items()))
    send_metric(METRIC_TEMPERATURE, temperature4, dict(settings['sensor_4'].items()))
    send_metric(METRIC_TEMPERATURE, temperature5, dict(settings['sensor_5'].items()))
    send_metric(METRIC_HUMIDITY, humidity5, dict(settings['sensor_5'].items()))
    # send_metric(METRIC_DEWPOINT, dewpoint_5, dict(settings['sensor_5'].items()))
    send_metric(METRIC_TEMPERATURE, temperature6, dict(settings['sensor_6'].items()))
    send_metric(METRIC_HUMIDITY, humidity6, dict(settings['sensor_6'].items()))
    # send_metric(METRIC_DEWPOINT, dewpoint_6, dict(settings['sensor_6'].items()))


def main():
    try:
        settings = load_settings()
    except FileNotFoundError:
        print('Change the settings file and rerun this script.')
        sys.exit(2)
    except ValueError as e:
        print('Error: ' + str(e))
        sys.exit(1)

    while True:
        measure_and_send(settings)
        time.sleep(10)


if __name__ == '__main__':
    main()
