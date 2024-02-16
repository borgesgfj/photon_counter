from dataclasses import dataclass
from time_tagger.connection.repository import ConnectionRepository
from time_tagger.connection.service import (
    TimeTaggerAddressInfoDto,
    ConnectionService,
)
from time_tagger.hardware_properties.service import (
    SetTriggerLevelDto,
    TimeTaggerHardwarePropertiesService,
)

from time_tagger.measurement.service import CountRateReqDto, ServiceRepository


@dataclass
class CloseConnectionDto:
    time_tagger_name: str
    time_taggers_proxy: object


class AppController:
    def __init__(
        self,
        time_tagger_network_connection_service: ConnectionService,
        time_tagger_measurement_service: ServiceRepository,
        time_tagger_hardware_service: TimeTaggerHardwarePropertiesService,
    ) -> None:
        self.time_tagger_network_connection_service = time_tagger_network_connection_service
        self.time_tagger_measurement_service = time_tagger_measurement_service
        self.time_tagger_hardware_service = time_tagger_hardware_service

    def connect_to_time_taggers_network(
        self, time_tagger_addresses_info: list[TimeTaggerAddressInfoDto]
    ) -> ConnectionRepository:
        return self.time_tagger_network_connection_service.connect_to_time_tagger_server(
            time_tagger_addresses_info
        )

    def get_single_counts_rate_time_series(self, count_rate_req_dto: CountRateReqDto):
        counts_per_channel = self.time_tagger_measurement_service.upsert_count_rates(
            count_rate_req_dto
        )

        return counts_per_channel

    def get_coincidence_counts_rate_time_series(self, count_rate_req_dto: CountRateReqDto):
        coincidences_per_channel_group = (
            self.time_tagger_measurement_service.upsert_coincidence_count_rate(count_rate_req_dto)
        )

        return coincidences_per_channel_group

    def set_time_tagger_channels_trigger_level(self, set_trigger_level_dto: SetTriggerLevelDto):
        self.time_tagger_hardware_service.set_trigger_level(set_trigger_level_dto)

        channels = list(set_trigger_level_dto.channels_voltage.keys())
        return self.time_tagger_hardware_service.get_channels_trigger_level(
            time_tagger_proxy=set_trigger_level_dto.time_tagger_network_proxy, channels=channels
        )

    def close_time_tagger_network_connections(self, time_taggers_info: list[CloseConnectionDto]):
        for time_tagger in time_taggers_info:
            self.time_tagger_network_connection_service.close_time_tagger_connection(
                time_tagger.time_tagger_name, time_tagger.time_taggers_proxy
            )
