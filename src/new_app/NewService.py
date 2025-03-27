"""
Service and repo(for now) of the new app

"""
from new_app.constants import MeasurementType, CountRateReqParams
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal as Signal
import TimeTagger as TT

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
            r += [value]
        return r

    def save_data(self,key,data):
        if key in self.measurements_per_device.keys():
            self.measurements_per_device[key]+=[data]
        else:
            self.measurements_per_device[key]=[data]
    #Get the last data for the key )
    def get_last_datas(self,key,all:bool):
        if key in self.measurements_per_device.keys():
            return  self.measurements_per_device[tuple(key)][-1]
    
    #Clear the repo
    def clear(self):
        self.measurements_per_device: dict[tuple[int, MeasurementType]] = {}


#Object to have the histogram use qthread
class histo_service(QObject):
    data = Signal(tuple)
    def __init__(self,request_param):
        super().__init__()   
        self.request_params =request_param

    def getData_histo(self):
        histo_measurement =self.request_params.histogram_measurement
        histo_measurement.startFor(2e12,clear=True)
        histo_measurement.waitUntilFinished()
        x = histo_measurement.getIndex()
        y = histo_measurement.getData()
        histo_measurement.clear()
        # key = (self.request_params.histogram_measurement,self.request_params.measurement_type)
        datas=(x,y)
        self.data.emit(datas)
        

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


        
