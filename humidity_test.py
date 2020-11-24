import sys

import mock

ada_mock = mock.MagicMock()
mock.patch.dict('sys.modules', Adafruit_DHT=ada_mock).start()

def test_abc():
    ada_mock.read_retry.return_value = (None, None)
    import humidity

    assert 1 + 1 == 2
