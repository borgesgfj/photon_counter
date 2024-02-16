from dataclasses import dataclass


@dataclass
class SingleChannelDataInitializationDto:
    device_serial: str
    channels: list[int]


@dataclass
class CoincidenceGroupsDataInitializationDto:
    device_serial: str
    channels_group: list[tuple[int, int]]


class MeasurementRepository:
    def __init__(self) -> None:
        self.single_counts_rate_data: dict[str, dict[int, list[float]]] = {}
        self.coincidences_count_rate_data: dict[str, dict[tuple[int, int], list[float]]] = {}

    def update_single_counts_rate(self, device_serial: str, data_per_channel: dict[int, float]):
        for channel in data_per_channel:
            self.single_counts_rate_data[device_serial][channel].append(data_per_channel[channel])

        return self.single_counts_rate_data[device_serial]

    def update_coincidences_rate(
        self, device_serial: str, channel_group_data: dict[tuple[int, int], float]
    ):
        for channel_group in channel_group_data:
            self.coincidences_count_rate_data[device_serial][channel_group].append(
                channel_group_data[channel_group]
            )

        return self.coincidences_count_rate_data[device_serial]

    def initialize_single_channels_data(
        self, initialization_dto: SingleChannelDataInitializationDto
    ):
        channels_data = {}
        device = initialization_dto.device_serial

        for channel in initialization_dto.channels:
            channels_data[channel] = []

        self.single_counts_rate_data[device] = channels_data

    def initialize_coincidences_group_data(
        self, initialization_dto: CoincidenceGroupsDataInitializationDto
    ):
        channels_group_data = {}
        device = initialization_dto.device_serial

        for channel_group in initialization_dto.channels_group:
            channels_group_data[channel_group] = []

        self.coincidences_count_rate_data[device] = channels_group_data
