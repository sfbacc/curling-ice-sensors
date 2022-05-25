import mock

import config_manager
from config_manager import load_settings

ada_mock = mock.MagicMock()
ada_mock.read_retry.return_value = (1, 1)
mock.patch.dict('sys.modules', Adafruit_DHT=ada_mock).start()

import collect_measurements as cm

settings = load_settings()


def _find_devices_patch():
  patch = mock.patch.object(cm, '_find_all_devices', return_value=[
      cm.SENSOR_PATH + '/sensor_1' + cm.SENSOR_FILE,
      cm.SENSOR_PATH + '/sensor_2' + cm.SENSOR_FILE,
  ])
  return patch


@mock.patch('collect_measurements.read_DS18B20_temp')
def test_measure_and_send(_read_temp: mock.Mock):
  config = {
      'sensor_1': {'test_key': 'test_value'},
      'sensor_2': {'test_key': 'test_value'}
  }
  with mock.patch.object(cm, 'send_metric') as send_metric, \
      _find_devices_patch() as _find_all_devices:
    cm.measure_and_send(config)

  send_metric.assert_called()


@mock.patch('datadog.api.Metric.send', name='dd_send',
            return_value={'status': 'ok'})
@mock.patch('collect_measurements.read_DS18B20_temp')
def test_datadog_tags(read_temp, dd_send: mock.Mock):
  config = {
      'sensor_1': {'test_key': 'test_value'},
      'sensor_2': {'test_key': 'test_value'}
  }

  with _find_devices_patch() as _find_all_devices:
    cm.measure_and_send(config)

  dd_send.assert_called_with(metric='sfbacc.temperature', points=read_temp(),
                             tags=['test_key:test_value'])


def test_load_config():
  try:
    config_manager.load_settings()
  except FileNotFoundError:
    pass

  config_manager.load_settings()
