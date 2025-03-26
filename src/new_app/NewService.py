"""
Service and repo(for now) of the new app

"""
from new_app.constants import MeasurementType
import numpy as np

"""
Measurement repo hold the data 

"""

class MeasurementRepository:
    def __init__(self) -> None:
        self.measurements_per_device: dict[tuple[int, MeasurementType]] = {}

    def upsert_data(self, params: CountRateReqParams,data):
        r = []
        for index, value in enumerate(data):
            key = (params.channels[index],params.measurement_type)
            if key not in self.measurements_per_device.keys():
                self.measurements_per_device[key] = []
            recorded_data = self.measurements_per_device[key]
            recorded_data.append(value)
            r += [recorded_data]
        return r

    def save_data_histo(self,key,data):
         self.measurements_per_device[key]=[data]

    def clear(self):
        self.measurements_per_device: dict[tuple[int, MeasurementType]] = {}

    def get_datas(self,key,all:bool):
        if all:
            if key in self.measurements_per_device.keys():
                return  self.measurements_per_device[tuple(key)][-1]
        else :
            if key in self.measurements_per_device.keys():
                if key[1]==MeasurementType.HISTOGRAM or key[1] ==MeasurementType.HISTOGRAM_CORR:
                    data = self.measurements_per_device[key][-1]
                    return  (np.max(data[1]),data[0][np.argmax(data[1])])
                else:
                    return self.measurements_per_device[key][-1]