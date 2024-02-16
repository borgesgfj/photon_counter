from dataclasses import dataclass
from itertools import combinations
from remote_connector_dao.TimeTaggerMeasurementDAO import (
    TimeTaggerMeasurementDAO,
    CountRateMeasurementDto,
)
from remote_connector_dao.data.MeasurementsData import (
    MeasurementsData,
    SingleChannelDataInitializationDto,
    CoincidenceGroupsDataInitializationDto,
)
from remote_connector_dao.TimeTaggerVirtualChannelBuilder import (
    TimeTaggerVirtualChannelBuilder,
)


@dataclass
class CountRateReqDto:
    channels: list[int]
    device_serial: str
    time_tagger_network_proxy: object


class TimeTaggerMeasurementService:
    def __init__(
        self,
        time_tagger_measurement_dao: TimeTaggerMeasurementDAO,
        measurements_data: MeasurementsData,
        time_tagger_virtual_channel_builder: TimeTaggerVirtualChannelBuilder,
    ):
        self.time_tagger_measurement_dao = time_tagger_measurement_dao
        self.measurements_data = measurements_data
        self.virtual_channel_builder = time_tagger_virtual_channel_builder

    def upsert_count_rates(self, count_rate_req_dto: CountRateReqDto):
        device_serial = count_rate_req_dto.device_serial
        channels = count_rate_req_dto.channels

        count_rate_data = self.time_tagger_measurement_dao.get_count_rates(
            CountRateMeasurementDto(
                channels,
                count_rate_req_dto.time_tagger_network_proxy,
            )
        )

        if device_serial not in self.measurements_data.single_counts_rate_data:
            self.measurements_data.initialize_single_channels_data(
                SingleChannelDataInitializationDto(device_serial, channels)
            )
        channels_data = self._build_count_rate_data_per_channel(channels, count_rate_data)

        upsert_data = self.measurements_data.update_single_counts_rate(device_serial, channels_data)
        return upsert_data

    def upsert_coincidence_count_rate(self, request_dto: CountRateReqDto):
        time_tagger_proxy = request_dto.time_tagger_network_proxy

        single_channels = request_dto.channels

        device_serial = request_dto.device_serial

        coincidence_channels_group = list(combinations(single_channels, 2))

        virtual_channel = self.virtual_channel_builder.build_coincidence_virtual_channel(
            time_tagger_proxy, coincidence_channels_group
        )

        coincidence_virtual_channels_numbers = virtual_channel.getChannels()

        counts_data = self.time_tagger_measurement_dao.get_count_rates(
            CountRateMeasurementDto(
                channels=coincidence_virtual_channels_numbers,
                time_tagger_network_proxy=time_tagger_proxy,
            )
        )

        if device_serial not in self.measurements_data.coincidences_count_rate_data:
            self.measurements_data.initialize_coincidences_group_data(
                CoincidenceGroupsDataInitializationDto(device_serial, coincidence_channels_group)
            )

        group_channels_data = self._build_coincidence_data_per_channel_group(
            coincidence_channels_group, counts_data
        )

        upsert_data = self.measurements_data.update_coincidences_rate(
            device_serial, group_channels_data
        )

        return upsert_data

    def _build_count_rate_data_per_channel(self, channels: list[int], counts: list[float]):
        channels_data = {}
        for index, channel in enumerate(channels):
            channels_data[channel] = counts[index]

        return channels_data

    def _build_coincidence_data_per_channel_group(
        self, channel_groups: list[tuple[int, int]], counts: list[float]
    ):
        groups_data = {}
        for index, channel_group in enumerate(channel_groups):
            groups_data[channel_group] = counts[index]

        return groups_data
