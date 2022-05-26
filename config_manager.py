import configparser

SETTINGS_FILE_NAME = 'settings.ini'
LOCAL_FILE_NAME = 'local.ini'
ALLOWED_X_VALUES = ('home', 'center', 'away')
ALLOWED_Y_VALUES = ('outside', 'warmroom', '1', '2', '3', '4', '5')
ALLOWED_Z_VALUES = ('ice_base', 'ice_surface', '5ft', '15ft')


def load_settings():
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE_NAME)
    return config


def load_local():
    config = configparser.ConfigParser(allow_no_value=True)
    dataset = config.read(LOCAL_FILE_NAME)
    if len(dataset) == 0:
        raise FileNotFoundError()

    return config
