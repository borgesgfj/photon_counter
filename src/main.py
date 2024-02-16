from remote_connector_dao.AppController import AppController, CloseConnectionDto
from shared.constants.constants import TRIGGER_VOLTAGE
from time_tagger.connection.repository import ConnectionRepository
from time_tagger.connection.service import (
    TimeTaggerAddressInfoDto,
    ConnectionService,
)
from time_tagger.hardware_properties.service import (
    SetTriggerLevelDto,
    TimeTaggerHardwarePropertiesService,
)
from time_tagger.measurement.dao import MeasurementDao
from time_tagger.measurement.repository import MeasurementRepository
from time_tagger.measurement.service import CountRateReqDto, ServiceRepository
from time_tagger.builder import TimeTaggerBuilder
from time_tagger.connection.dao import ConnectionDao

# test_run()
# run_real_time_graph()
# tagger = connect_to_TimeTagger_server()
# print(tagger, "executed")

# test_signal_run()
"""
    This file is a mess because I am only using this for testing.
"""

connection_data = ConnectionRepository()

time_tagger_hardware_properties_service = TimeTaggerHardwarePropertiesService()

connection_dao = ConnectionDao()

time_tagger_network_connection_service = ConnectionService(
    connection_data, time_tagger_hardware_properties_service, connection_dao
)

time_tagger_measurement_dao = MeasurementDao()

measurement_data = MeasurementRepository()

virtual_channel_builder = TimeTaggerBuilder()

time_tagger_measurement_service = ServiceRepository(
    time_tagger_measurement_dao, measurement_data, virtual_channel_builder
)

app_controller = AppController(
    time_tagger_network_connection_service,
    time_tagger_measurement_service,
    time_tagger_hardware_properties_service,
)

# The first connection should fails because there is no server on this port.
req = app_controller.connect_to_time_taggers_network(
    [
        TimeTaggerAddressInfoDto(
            host_address="192.168.10.100",
            port="43101",
            time_tagger_name="Bob_tagger",
        ),
        TimeTaggerAddressInfoDto(
            host_address="192.168.10.100",
            port="41101",
            time_tagger_name="Alice_tagger",
        ),
    ]
)

print(req, end="\n\n")

print(req.connection_failed_devices, "connection failed devices", end="\n\n")

tagger = req.connected_devices[0].tagger_proxy
connected_device_name = req.connected_devices[0].time_tagger_name

set_trigger_level_res = app_controller.set_time_tagger_channels_trigger_level(
    SetTriggerLevelDto(
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


single_counts = app_controller.get_single_counts_rate_time_series(
    CountRateReqDto(
        channels=[1, 2, 3, 4],
        device_serial=serial,
        time_tagger_network_proxy=tagger,
    )
)
print(single_counts, "single counts", end="\n\n")

coincidences_counts = app_controller.get_coincidence_counts_rate_time_series(
    CountRateReqDto(
        time_tagger_network_proxy=tagger,
        channels=[1, 2, 3, 4],
        device_serial=serial,
    )
)

print(coincidences_counts, "coincidences counts", end="\n\n")


app_controller.close_time_tagger_network_connections(
    [CloseConnectionDto(connected_device_name, tagger)]
)
