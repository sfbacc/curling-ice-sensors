#!/bin/bash
echo 'Run this as sudo'
cp ice_sensors.service /etc/systemd/system/
systemctl start ice_sensors
systemctl enable ice_sensors
