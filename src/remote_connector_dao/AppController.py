from dataclasses import dataclass
from time_tagger.connection.service import (
    TimeTaggerAddressInfo,
    ConnectionService,
)
from time_tagger.hardware_properties.dao import (
    SetTriggerLevelParams,
    TimeTaggerHardwarePropertiesDao,
)

from time_tagger.measurement.service import MeasurementService, CountRateReqParams


@dataclass
class CloseConnectionPrams:
    time_tagger_name: str
    time_taggers_proxy: object


class AppController:
    def __init__(
        self,
        time_tagger_network_connection_service: ConnectionService,
        time_tagger_hardware_properties: TimeTaggerHardwarePropertiesDao,
        time_tagger_measurement_service: MeasurementService,
    ) -> None:
        self.time_tagger_network_connection_service = (
            time_tagger_network_connection_service
        )
        self.time_tagger_hardware_service = time_tagger_hardware_properties
        self.time_tagger_measurement_service = time_tagger_measurement_service

    def connect_to_time_taggers_network(
        self, time_tagger_addresses_info: list[TimeTaggerAddressInfo]
    ):
        return self.time_tagger_network_connection_service.connect_to_time_tagger_server(
            time_tagger_addresses_info
        )

    def set_time_tagger_channels_trigger_level(
        self, set_trigger_level_dto: SetTriggerLevelParams
    ):
        self.time_tagger_hardware_service.set_trigger_level(set_trigger_level_dto)

        channels = list(set_trigger_level_dto.channels_voltage.keys())
        return self.time_tagger_hardware_service.get_channels_trigger_level(
            time_tagger_proxy=set_trigger_level_dto.time_tagger_network_proxy,
            channels=channels,
        )

    def close_time_tagger_network_connections(
        self, time_taggers_info: list[CloseConnectionPrams]
    ):
        for time_tagger in time_taggers_info:
            self.time_tagger_network_connection_service.close_time_tagger_connection(
                time_tagger.time_tagger_name, time_tagger.time_taggers_proxy
            )

    def get_measurement_data(
        self, count_rate_req: CountRateReqParams
    ) -> list[list[float]]:
        return self.time_tagger_measurement_service.record_measurement_data(
            count_rate_req
        )
