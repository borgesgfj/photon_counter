from dataclasses import dataclass
from enum import Enum


class MeasurementType(Enum):
    SINGLE_COUNTS = "SINGLE_COUNTS"
    COINCIDENCES = "COINCIDENCES"

    HISTOGRAM = "HISTOGRAM"
    HISTOGRAM_START_STOP = "HISTOGRAM_START_STOP"
    HISTOGRAM_CORR = "HISTOGRAM_CORR"

@dataclass
class UpsertDataParams:
    channels: list[int]
    data: list[float]
    device_serial: str
    measurement_type: MeasurementType


class MeasurementRepository:
    def __init__(self) -> None:
        self.measurements_per_device: dict[tuple[str, MeasurementType]] = {}

    def upsert_data(self, params: UpsertDataParams):
        measurement_key = (params.device_serial, params.measurement_type)

        if measurement_key not in self.measurements_per_device:
            self.measurements_per_device[measurement_key] = [
                [] for channel in params.channels
            ]

        for index, value in enumerate(params.data):
            recorded_data = self.measurements_per_device[measurement_key][index]

            recorded_data.append(value)

            if len(recorded_data) > 50:
                recorded_data.pop(0)

        return self.measurements_per_device[measurement_key]

    
    def clear(self):
        self.measurements_per_device: dict[tuple[str, MeasurementType]] = {}
    

