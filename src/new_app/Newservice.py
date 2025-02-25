import TimeTagger as TT
from new_app.struct_and_enum import *
import time_tagger
import numpy as np

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
            # if len(recorded_data) > 50:
            #     recorded_data.pop(0)
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


def record_measurement_data(request_params: CountRateReqParams,repo: MeasurementRepository,time):
    time_tagger = request_params.time_tagger
    channels = request_params.channels

    with TT.Countrate(
        tagger=time_tagger,
        channels=channels,
    ) as cr:
        cr.startFor(int(time), clear=True)
        cr.waitUntilFinished()
        counts = cr.getData()
    return repo.upsert_data(request_params,counts)


def get_accumulated_count(request_params: CountRateReqParams,repo:MeasurementRepository,time):
    device_serial = request_params.device_serial
    time_tagger = request_params.time_tagger
    channels = request_params.channels
    with TT.Countrate(
        tagger=time_tagger,
        channels=channels
    )as cr:
        cr.startFor(time, clear=True)
        cr.waitUntilFinished()
        counts = cr.getCountsTotal()
    return repo.upsert_data(request_params,counts)

#Get the measurement for the correlation histogram
def getData_histo(request_params: CountRateReqParams,repo:MeasurementRepository):
    histo_type = request_params.measurement_type
    histo_measurement =request_params.histogram_measurement
    match histo_type:
        case  MeasurementType.HISTOGRAM_CORR :
            histo_measurement.startFor(2e12,clear=True)
            histo_measurement.waitUntilFinished()
            x = histo_measurement.getIndex()
            y = histo_measurement.getData()
            histo_measurement.clear()
            key = (request_params.histogram_measurement,request_params.measurement_type)
            data=(x,y)
            repo.save_data_histo(key,data)
            return [x,y]
        case MeasurementType.HISTOGRAM:
            histo_measurement.startFor(2e12,clear=True)
            histo_measurement.waitUntilFinished()
            x = histo_measurement.getIndex()
            y = histo_measurement.getData()
            histo_measurement.clear()
            key = (request_params.histogram_measurement,request_params.measurement_type)
            data=(x,y)
            repo.save_data_histo(key,data)
            return [x,y]
        case _: assert 0, "this" + histo_type.value + "measurement class doesn't exist"
