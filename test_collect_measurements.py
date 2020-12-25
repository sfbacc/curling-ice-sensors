import mock

import config_manager

ada_mock = mock.MagicMock()
ada_mock.read_retry.return_value = (1, 1)
mock.patch.dict('sys.modules', Adafruit_DHT=ada_mock).start()

import collect_measurements


@mock.patch('datadog.api.Metric.send')
def test_measure_and_send(dd_send: mock.Mock):
    config = {
        'sensor_1': {'test_key': 'test_value'},
        'sensor_2': {'test_key': 'test_value'}
    }

    with mock.patch.object(collect_measurements, 'send_metric') as send_metric:
        collect_measurements.measure_and_send(config)

    assert send_metric.call_count == 4
    assert send_metric.call_args_list[0].args[2]['test_key'] == 'test_value'


@mock.patch('datadog.api.Metric.send')
def test_datadog_tags(dd_send: mock.Mock):
    dd_send.return_value = {'status': 'ok'}
    config = {
        'sensor_1': {'test_key': 'test_value'},
        'sensor_2': {'test_key': 'test_value'}
    }

    collect_measurements.measure_and_send(config)

    assert dd_send.call_count == 4
    assert dd_send.call_args.kwargs['tags'][0] == 'test_key:test_value'


def test_load_config():
    try:
        config_manager.load_settings()
    except FileNotFoundError:
        pass

    config_manager.load_settings()
