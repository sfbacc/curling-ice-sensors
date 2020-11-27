import configparser
import sys
import time

import Adafruit_DHT
import datadog

from config_manager import load_settings

DATADOG_API_KEY = '565893d17f4370e4474975a941c5a468'
DATADOG_API_URL = 'https://api.datadoghq.com/api/v1/series?api_key=' + DATADOG_API_KEY
METRIC_TEMPERATURE = 'sfbacc.temperature'
METRIC_HUMIDITY = 'sfbacc.humidity'

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN1 = 4
DHT_PIN2 = 9

datadog.initialize(api_key=DATADOG_API_KEY)


def send_metric(metric, value, tags: dict):
    datadog.api.Metric.send(
        metric=metric,
        points=value,
        tags=list(map(lambda kv: f'{kv[0]}:{kv[1]}', tags.items()))
    )


def measure_and_send(settings: configparser.ConfigParser):
    humidity1, temperature1 = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN1)
    humidity2, temperature2 = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN2)

    if humidity1 is not None and temperature1 is not None:
        send_metric(METRIC_TEMPERATURE, temperature1, dict(settings['sensor_1'].items()))
        send_metric(METRIC_HUMIDITY, humidity1, dict(settings['sensor_1'].items()))

    if humidity2 is not None and temperature2 is not None:
        send_metric(METRIC_TEMPERATURE, temperature2, dict(settings['sensor_2'].items()))
        send_metric(METRIC_HUMIDITY, humidity2, dict(settings['sensor_2'].items()))

    print("Temp1={0:0.1f}*C Humidity1={1:0.1f}%".format(temperature1, humidity1))
    print("Temp2={0:0.1f}*C Humidity2={1:0.1f}%".format(temperature2, humidity2))


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
