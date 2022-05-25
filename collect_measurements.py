import configparser
import glob
import json
import re
import sys
import time
import functools
from typing import Dict, List

import Adafruit_DHT
import datadog
from meteocalc import dew_point

from config_manager import load_settings

datadog.initialize()

SENSOR_PATH = '/sys/bus/w1/devices'
SENSOR_FILE = '/w1_slave'

METRIC_TEMPERATURE = 'sfbacc.temperature'
METRIC_HUMIDITY = 'sfbacc.humidity'
METRIC_DEWPOINT = 'sfbacc.dewpoint'
DHT_SENSOR = Adafruit_DHT.DHT22
SENSOR_5_ID = 4
SENSOR_6_ID = 22
temperature_5_list = {'temp': [], 'humid': []}
temperature_6_list = {'temp': [], 'humid': []}


def _get_id_from_device_path(device_path):
  try:
    found = re.search(SENSOR_PATH + '/(.+?)' + SENSOR_FILE, device_path).group(
        1)
  except AttributeError:
    raise AttributeError('Could not get device id from path.', device_path)

  return found


@functools.lru_cache()
def _find_all_devices():
  # /sys/bus/w1/devices/28-0301a2791250/w1_slave
  device_paths = []
  for f in glob.glob(SENSOR_PATH + '/**' + SENSOR_FILE):
    device_paths.append(f)
    print("Found file: %s" % f)
  return device_paths


def good_value(h_value: int, t_value: int, history_data: Dict[str, List[int]]):
  if not h_value and t_value is None:
    return False

  # check for any data spike by comparing against running average
  if (10 >= h_value or h_value >= 90) or (-10 >= t_value or t_value >= 40):
    return False

  # check if temp and humid are in reasonable range
  if len(history_data['temp']) < 10:
    # build list at start
    history_data['humid'].append(h_value)
    history_data['temp'].append(t_value)
    return False

  t_ave = sum(history_data['temp']) / len(history_data['temp'])
  h_ave = sum(history_data['humid']) / len(history_data['humid'])

  # check for spike in data
  if abs(t_ave - t_value) >= 2 or abs(h_ave - h_value) >= 2:
    return False

  history_data['temp'].pop(0)
  history_data['temp'].append(t_value)
  history_data['humid'].pop(0)
  history_data['humid'].append(h_value)
  return True


def read_DS18B20_temp(sensor_name):
  print('Scanning %s ...' % sensor_name)
  try:
    with open(sensor_name, 'r') as f:
      lines = f.readlines()
  except Exception as e:
    print('Could not open file %s: %s' % (sensor_name, e))
    return
  temp_result = lines[1].find('t=')
  if temp_result != -1:
    temp_string = lines[1].strip()[temp_result + 2:]
    temp = float(temp_string) / 1000.0
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
      print(response)
      print('Error: ' + json.dumps(response))


def measure_and_send(settings: configparser.ConfigParser):
  devices = _find_all_devices()

  for device_path in devices:
    device_id = _get_id_from_device_path(device_path)
    temperature = read_DS18B20_temp(device_path)
    send_metric(METRIC_TEMPERATURE, temperature, settings[device_id])

    # TODO: Next Steps: Settings file should include the type of sensor that
    #  this is. Find if this is a temperature or a humidity sensor from settings

  # humidity5, temperature5, dewpoint5 = read_DHT22_temp_hum(temperature_5_list, SENSOR_5_ID)

  # print values collected
  # full_datetime = datetime.datetime.now().strftime('%m %d %Y %H:%M:%S')
  # print('\n', full_datetime,)
  # print('ice_temp: ', temperature1, temperature2, temperature3, temperature4)
  # print('airtemp: ', temperature5, temperature6)
  # print('dewpoint: ', dewpoint5, dewpoint6)
  # print('humidity: ', humidity5, humidity6)

  # send values to DataDog
  # send_metric(METRIC_TEMPERATURE, temperature2,
  #             dict(settings['sensor_2'].items()))
  # send_metric(METRIC_TEMPERATURE, temperature3,
  #             dict(settings['sensor_3'].items()))
  # send_metric(METRIC_TEMPERATURE, temperature4,
  #             dict(settings['sensor_4'].items()))
  # send_metric(METRIC_TEMPERATURE, temperature15,
  #             dict(settings['sensor_15'].items()))
  # send_metric(METRIC_HUMIDITY, humidity5, dict(settings['sensor_5'].items()))
  # # send_metric(METRIC_DEWPOINT, dewpoint_5, dict(settings['sensor_5'].items()))
  # send_metric(METRIC_TEMPERATURE, temperature6, dict(settings['sensor_6'].items()))
  # send_metric(METRIC_HUMIDITY, humidity6, dict(settings['sensor_6'].items()))
  # send_metric(METRIC_DEWPOINT, dewpoint_6, dict(settings['sensor_6'].items()))


def _prepare(settings):
  devices = _find_all_devices()
  for dp in devices:
    device_id = _get_id_from_device_path(dp)
    if device_id in settings:
      found = 'FOUND'
    else:
      # TODO: Do something loud here
      found = '... not found'
    print('Found device: ' + dp + ' ' + found)

def main():
  try:
    settings = load_settings()
  except FileNotFoundError:
    print('Change the settings file and rerun this script.')
    sys.exit(2)
  except ValueError as e:
    print('Error: ' + str(e))
    sys.exit(1)

  _prepare(settings)

  while True:
    measure_and_send(settings)
    time.sleep(10)


if __name__ == '__main__':
  main()
