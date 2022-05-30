import datetime
import functools
import glob
import json
import re
import sys
import time
import Adafruit_DHT
import datadog

from configparser import ConfigParser
from retry import retry
from datadog.api.exceptions import DatadogException
from meteocalc import dew_point

from config_manager import load_local
from config_manager import load_settings

SENSOR_PATH = '/sys/bus/w1/devices'
SENSOR_FILE = '/w1_slave'

METRIC_TEMPERATURE = 'sfbacc.temperature'
METRIC_HUMIDITY = 'sfbacc.humidity'
METRIC_DEWPOINT = 'sfbacc.dewpoint'
DHT_SENSOR = Adafruit_DHT.DHT22

datadog.initialize()


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


def good_value(h_value: int, t_value: int):
  if not h_value and t_value is None:
    return False

  if (10 >= h_value or h_value >= 90) or (-10 >= t_value or t_value >= 40):
    return False

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


def read_DHT22_temp_hum(sensor_name):
  humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, sensor_name)
  if not good_value(humidity, temperature):
    return None, None, None
  dewpoint = dew_point(temperature, humidity)
  return round(humidity, 5), round(temperature, 5), round(dewpoint, 5)


@retry(exceptions=[DatadogException], tries=3)
def send_metric(metric, value, tags: dict):
  if value is None:
    return

  response = datadog.api.Metric.send(
    metric=metric,
    points=value,
    tags=list(map(lambda kv: f'{kv[0]}:{kv[1]}', tags.items()))
  )
  if response['status'] != 'ok':
    print(response)
    print('Error: ' + json.dumps(response))



def measure_and_send(settings: ConfigParser, local: ConfigParser):
  devices = _find_all_devices()

  for device_path in devices:
    device_id = _get_id_from_device_path(device_path)
    temperature = read_DS18B20_temp(device_path)
    tags = dict(settings[device_id].items())
    offset = float(tags.pop('offset'))
    temperature -= offset
    send_metric(METRIC_TEMPERATURE, temperature, tags)

  for sensor in local:
    if sensor == 'DEFAULT':
      continue
    print('Reading DHT from ' + sensor)
    tags = dict(local[sensor].items())
    pin = int(tags.pop('pin_id'))

    humidity, temperature, dewpoint = read_DHT22_temp_hum(pin)
    if None in (humidity, temperature, dewpoint):
      print('Bad values')
      continue

    # print values collected
    full_datetime = datetime.datetime.now().strftime('%m %d %Y %H:%M:%S')
    print(full_datetime, 'T/H/D', (temperature, humidity, dewpoint))

    send_metric(METRIC_TEMPERATURE, temperature, tags)
    send_metric(METRIC_HUMIDITY, humidity, tags)
    send_metric(METRIC_DEWPOINT, dewpoint, tags)


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
  settings = load_settings()
  try:
    local = load_local()
  except FileNotFoundError:
    print('Copy "local_template.ini" to "local.ini" and set the values there')
    sys.exit(2)

  _prepare(settings)

  while True:
    measure_and_send(settings, local)
    time.sleep(10)


if __name__ == '__main__':
  main()
