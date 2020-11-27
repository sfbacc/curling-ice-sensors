import configparser
import sys

SETTINGS_FILE_NAME = 'settings.ini'
ALLOWED_X_VALUES = ('home', 'center', 'away')
ALLOWED_Y_VALUES = ('outside', 'warmroom', '1', '2', '3', '4', '5')
ALLOWED_Z_VALUES = ('ice_base', 'ice_surface', '5ft', '15ft')


def load_settings():
    config = configparser.ConfigParser(allow_no_value=True)
    dataset = config.read(SETTINGS_FILE_NAME)
    if len(dataset) == 0:
        write_default_config(config)
        raise FileNotFoundError()
    try:
        verify_config_values(config)
    except AssertionError as e:
        raise ValueError(e)
    return config


def verify_config_values(config):
    assert config.has_section('sensor_1'), 'Settings should have section "sensor_1"'
    assert config.has_section('sensor_2'), 'Settings should have section "sensor_2"'

    assert 'loc_x' in config['sensor_1'], "sensor_1 section should have loc_x"
    assert 'loc_y' in config['sensor_1'], "sensor_1 section should have loc_y"
    assert 'loc_z' in config['sensor_1'], "sensor_1 section should have loc_z"

    assert 'loc_x' in config['sensor_2'], "sensor_2 section should have loc_x"
    assert 'loc_y' in config['sensor_2'], "sensor_2 section should have loc_y"
    assert 'loc_z' in config['sensor_2'], "sensor_2 section should have loc_z"


def write_default_config(config):
    config.remove_section('DEFAULT')
    config.add_section('sensor_1')
    config.add_section('sensor_2')
    print('Creating a new "settings.ini" file with default values.')
    config.set('sensor_1', '# ' + ' '.join(ALLOWED_X_VALUES), None)
    config['sensor_1']['loc_x'] = 'home\n'
    config.set('sensor_1', '# ' + ' '.join(ALLOWED_Y_VALUES), None)
    config['sensor_1']['loc_y'] = '3\n'
    config.set('sensor_1', '# ' + ' '.join(ALLOWED_Z_VALUES), None)
    config['sensor_1']['loc_z'] = 'ice_base\n'
    config.set('sensor_2', '# ' + ' '.join(ALLOWED_X_VALUES), None)
    config['sensor_2']['loc_x'] = 'home\n'
    config.set('sensor_2', '# ' + ' '.join(ALLOWED_Y_VALUES), None)
    config['sensor_2']['loc_y'] = '3\n'
    config.set('sensor_2', '# ' + ' '.join(ALLOWED_Z_VALUES), None)
    config['sensor_2']['loc_z'] = 'ice_base\n'
    with open(SETTINGS_FILE_NAME, 'w+') as configfile:
        config.write(configfile)