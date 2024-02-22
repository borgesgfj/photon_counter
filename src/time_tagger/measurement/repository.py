from dataclasses import dataclass
from enum import Enum


class MeasurementType(Enum):
    SINGLE_COUNTS = "SINGLE_COUNTS"
    COINCIDENCES = "COINCIDENCES"


@dataclass
class UpsertDataParams:
    channels: list[int]
    data: list[float]
    device_serial: str
    measurement_type: MeasurementType


class MeasurementRepository:
    def __init__(self) -> None:
        self.single_counts_rate_data: dict[str, list[list[float]]] = {}
        self.coincidences_count_rate_data: dict[str, list[list[float]]] = {}

    def upsert_data(self, params: UpsertDataParams):
        if params.measurement_type.value == MeasurementType.SINGLE_COUNTS.value:
            return self._upsert_single_counts_rate(params)

        return self._upsert_coincidences_rate(params)

    def _upsert_single_counts_rate(self, params: UpsertDataParams):
        device_serial = params.device_serial

        if device_serial not in self.single_counts_rate_data:
            self.single_counts_rate_data[device_serial] = [
                [] for channel in params.channels
            ]

        for index, value in enumerate(params.data):
            recorded_data = self.single_counts_rate_data[device_serial][index]

            recorded_data.append(value)

            if len(recorded_data) > 50:
                recorded_data.pop(0)

        return self.single_counts_rate_data[device_serial]

    def _upsert_coincidences_rate(self, params: UpsertDataParams):
        device_serial = params.device_serial

        if device_serial not in self.coincidences_count_rate_data:
            self.coincidences_count_rate_data[device_serial] = [
                [] for channel in params.channels
            ]

        for index, value in enumerate(params.data):
            recorded_data = self.coincidences_count_rate_data[device_serial][index]

            recorded_data.append(value)

            if len(recorded_data) > 50:
                recorded_data.pop(0)

        return self.coincidences_count_rate_data[device_serial]
