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
from time_tagger.measurement.dao import MeasurementDao
from time_tagger.measurement.repository import MeasurementRepository
from time_tagger.measurement.service import MeasurementService
from time_tagger.builder import TimeTaggerBuilder
from time_tagger.connection.dao import ConnectionDao
from ui.MainWindow import MainWindow

"""
    This file is a mess because I am only using this for testing.
"""

channels = [1, 2]
connection_data = ConnectionRepository()

time_tagger_hardware_properties_service = TimeTaggerHardwarePropertiesDao()

connection_dao = ConnectionDao()

time_tagger_network_connection_service = ConnectionService(
    connection_data, time_tagger_hardware_properties_service, connection_dao
)

time_tagger_builder = TimeTaggerBuilder()

time_tagger_measurement_dao = MeasurementDao(time_tagger_builder)

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
            host_address="192.168.10.100",
            port="41101",
            time_tagger_name="Alice_tagger",
        ),
        TimeTaggerAddressInfo(
            host_address="192.168.10.100",
            port="43101",
            time_tagger_name="Bob_tagger",
        ),
    ]
)

print(req, end="\n\n")

print(req.connection_failed_devices, "connection failed devices", end="\n\n")

tagger = req.connected_devices[0].tagger_proxy
connected_device_name = req.connected_devices[0].time_tagger_name

coincidence_virtual_channel = time_tagger_builder.build_coincidence_virtual_channel(
    tagger, channels
)

cc_virtual_channel_numbers = coincidence_virtual_channel.getChannels()

set_trigger_level_res = app_controller.set_time_tagger_channels_trigger_level(
    SetTriggerLevelParams(
        time_tagger_network_proxy=tagger,
        channels_voltage={
            1: TRIGGER_VOLTAGE,
            2: TRIGGER_VOLTAGE,
            3: TRIGGER_VOLTAGE,
            4: TRIGGER_VOLTAGE,
        },
    )
)

print(set_trigger_level_res, end="\n\n")

serial = req.connected_devices[0].serial_number
print(serial, "serial number of connceted TT", end="\n\n")

app = QtWidgets.QApplication(sys.argv)
window = MainWindow(
    channels=channels,
    device_serial_number=serial,
    timetagger_proxy=tagger,
    app_controller=app_controller,
    coincidence_virtual_channels=cc_virtual_channel_numbers,
    measurement_service=time_tagger_measurement_service,
)

window.show()
app.exec()

app_controller.close_time_tagger_network_connections(
    [CloseConnectionPrams(connected_device_name, tagger)]
)
