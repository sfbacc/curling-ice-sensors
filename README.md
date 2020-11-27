# curling-ice-sensors

![img](sensor_ice_layout.png)

## Installation

First install python dependencies:

```shell script
pip install -r requirements.txt
```

If all goes successful - create your default `settings.ini` by running 

```shell script
python collect_measurements.py
```

You will see an error:

```
$ python collect_measurements.py
Creating a new "settings.ini" file with default values.
Change the settings file and rerun this script.
```

Your default settings.ini will look something like this;

```ini
[sensor_1]
# home center away
loc_x = home

# outside warmroom 1 2 3 4 5
loc_y = 3

# ice_base ice_surface 5ft 15ft
loc_z = ice_base


[sensor_2]
# home center away
loc_x = home

# outside warmroom 1 2 3 4 5
loc_y = 3

# ice_base ice_surface 5ft 15ft
loc_z = ice_base
```

Modify values for the particular sensor you're all set.

## Running the code & Sending data to Datadog

Once the setup is complete and settings are configured run the same script again to start sending data to Datadog!

```shell script
$ python collect_measurements.py
```