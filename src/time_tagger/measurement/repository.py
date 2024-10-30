from dataclasses import dataclass
from enum import Enum
import numpy as np

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
            # if len(recorded_data) > 50:
            #     recorded_data.pop(0)
            r += [recorded_data]
        return r

    def save_data_histo(self,key,data):
         self.measurements_per_device[key]=[data]

    def clear(self):
        self.measurements_per_device: dict[tuple[int, MeasurementType]] = {}

    def get_last_value(self,key):
        if key in self.measurements_per_device.keys():
            if key[1]==MeasurementType.HISTOGRAM or key[1] ==MeasurementType.HISTOGRAM_CORR:
                data = self.measurements_per_device[key][-1]
                return  (np.max(data[1]),data[0][np.argmax(data[1])])
            else:
                return self.measurements_per_device[key][-1]

    def get_datas(self,key):
        if key in self.measurements_per_device.keys():
            return  self.measurements_per_device[key][-1]
