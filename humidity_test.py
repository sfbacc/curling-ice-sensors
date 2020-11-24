import sys

import mock

ada_mock = mock.MagicMock()
ada_mock.read_retry.return_value = (1, 1)
mock.patch.dict('sys.modules', Adafruit_DHT=ada_mock).start()

@mock.patch('datadog.api.Metric.send')
def test_temperature(dd_send):
    import humidity

    with mock.patch.object(humidity, 'send_temperature_to_datadog') as dd_temperature:
        humidity.measure_and_send()

    assert dd_temperature.call_count == 2

@mock.patch('datadog.api.Metric.send')
def test_humidity(dd_send):
    import humidity

    with mock.patch.object(humidity, 'send_humidity_to_datadog') as dd_humidity:
        humidity.measure_and_send()

    assert dd_humidity.call_count == 2
