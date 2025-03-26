#!/usr/bin/python3

import sys
from PyQt5 import QtWidgets
from AppController import AppController, CloseConnectionPrams
from shared.constants.constants import TRIGGER_VOLTAGE
from time_tagger.connection.repository import ConnectionRepository
from time_tagger.connection.service import (
    TimeTaggerAddressInfo,
    ConnectionService,
)
from time_tagger.hardware_properties.dao import (
    SetTriggerLevelParams,
    TimeTaggerHardwarePropertiesDao,
)
from time_tagger.measurement.repository import MeasurementRepository
from time_tagger.measurement.service import MeasurementService
from time_tagger.builder import TimeTaggerBuilder
from time_tagger.connection.dao import ConnectionDao
from new_app.MainUINew import MainWindow
import json 


#----------------------------------
# This file need a  json file as input to get the data
# the json file should be structure this way :
"""
{
    Name:"a name to id the tagger",
    addr:"the ip address of the tagger",
    port:"port of the tagger",
    Chan_Numb:Number of channels needed (<= of the  number available on the tagger),
    Trigger_v:{"1":V,...}
}

"""
arg = sys.argv

if len(arg) < 2:
    print("Error no file provided")
    quit()

f = open(arg[1],"r")
data = json.load(f)


connection_data = ConnectionRepository()

time_tagger_hardware_properties_service = TimeTaggerHardwarePropertiesDao()

connection_dao = ConnectionDao()

time_tagger_network_connection_service = ConnectionService(
    connection_data, time_tagger_hardware_properties_service, connection_dao
)

time_tagger_builder = TimeTaggerBuilder()



measurement_data = MeasurementRepository()


time_tagger_measurement_service = MeasurementService(measurement_data)

app_controller = AppController(
    time_tagger_network_connection_service=time_tagger_network_connection_service,
    time_tagger_measurement_service=time_tagger_measurement_service,
    time_tagger_hardware_properties=time_tagger_hardware_properties_service,
)

# The first connection should fails because there is no server on this port.
req = app_controller.connect_to_time_taggers_network(
    [
        TimeTaggerAddressInfo(
            host_address=data["addr"],
            port=data["port"],
            time_tagger_name=data["Name"],
        )
    ]
)

print(req, end="\n\n")

print(req.connection_failed_devices, "connection failed devices", end="\n\n")

tagger = req.connected_devices[0].tagger_proxy
connected_device_name = req.connected_devices[0].time_tagger_name

channels_voltage ={}
for key,value in data["Trigger_v"].items():
    channels_voltage[int(key)] = value

set_trigger_level_res = app_controller.set_time_tagger_channels_trigger_level(
    SetTriggerLevelParams(
        time_tagger_network_proxy=tagger,
        channels_voltage = channels_voltage 
    )
)

print(set_trigger_level_res, end="\n\n")

serial = req.connected_devices[0].serial_number
print(serial, "serial number of connceted TT", end="\n\n")
chan_number = data["Chan_Numb"] #tagger.getChannelList()[-1]
app = QtWidgets.QApplication(sys.argv)
window = MainWindow(
    device_serial_number=serial,
    timetagger_proxy=tagger,
    chan_number=chan_number,
)

window.show()
app.exec()

app_controller.close_time_tagger_network_connections(
    [CloseConnectionPrams(connected_device_name, tagger)]
)
