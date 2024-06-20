from dataclasses import dataclass
from enum import Enum

class MeasurementType(Enum):
    SINGLE_COUNTS = "SINGLE_COUNTS"
    COINCIDENCES = "COINCIDENCES"
    HISTOGRAM = "HISTOGRAM"
    HISTOGRAM_CORR = "HISTOGRAM_CORR"

@dataclass
class UpsertDataParams:
    channels: list[int]
    data: list[float]
    device_serial: str
    measurement_type: MeasurementType


class MeasurementRepository:
    def __init__(self) -> None:
        self.measurements_per_device: dict[tuple[int, MeasurementType]] = {}

    def upsert_data(self, params: UpsertDataParams):
        r = []
        for index, value in enumerate(params.data):
            key = (params.channels[index],params.measurement_type)
            if key not in self.measurements_per_device.keys():
                self.measurements_per_device[key] = []
            recorded_data = self.measurements_per_device[key]
            recorded_data.append(value)
            if len(recorded_data) > 50:
                recorded_data.pop(0)
            r += [recorded_data]
        return r

    def save_data_histo(self,key,data):
         self.measurements_per_device[key]=[data]

    def clear(self):
        self.measurements_per_device: dict[tuple[int, MeasurementType]] = {}

    def get_last_value(self,key):
        if key in self.measurements_per_device.keys():
            return self.measurements_per_device[key][-1]

    def save_data(self):
        f= open("save.csv","a")
        print("saving")
        for value in self.measurements_per_device.values():
            f.write(f"{value[-1]},")
        f.write("\n")
        f.close()
