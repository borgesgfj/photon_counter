from dataclasses import dataclass
import TimeTagger as TT
from shared.constants.constants import INTEGRATION_TIME
from time_tagger.measurement.repository import (
    MeasurementRepository,
    UpsertDataParams,
    MeasurementType,
)
import numpy as np

@dataclass
class CountRateReqParams:
    channels: list[int]
    device_serial: str
    time_tagger_network_proxy: object
    measurement_type: MeasurementType
    histogram_measurement= None
    bin_width = 50
    n_bin = 20

class MeasurementService:
    def __init__(
        self,
        measurements_data: MeasurementRepository,
    ):
        self.measurements_data = measurements_data

    def record_measurement_data(self, request_params: CountRateReqParams):
        device_serial = request_params.device_serial
        channels = request_params.channels

        count_rate_data = self._get_count_rates(
            channels, request_params.time_tagger_network_proxy
        )
        return self.measurements_data.upsert_data(
            UpsertDataParams(
                channels=channels,
                data=count_rate_data,
                device_serial=device_serial,
                measurement_type=request_params.measurement_type,
            )
        )

    def _get_count_rates(self, channels: list[int], time_tagger_network_proxy: object):

        with TT.Countrate(
            tagger=time_tagger_network_proxy,
            channels=channels,
        ) as cr:
            cr.startFor(int(INTEGRATION_TIME), clear=True)
            cr.waitUntilFinished()
            counts = cr.getData()
            return counts

    def get_accumulated_count(self, channels,time_tagger,aquisition_time):
        with TT.Countrate(
            tagger=time_tagger,
            channels=channels
        )as cr:
            cr.startFor(aquisition_time, clear=True)
            cr.waitUntilFinished()
            counts = cr.getCountsTotal()
            return counts

    #Get the measurement for the correlation histogram
    def getData_histo(self,request_params: CountRateReqParams):
        histo_type = request_params.measurement_type
        histo_measurement =request_params.histogram_measurement
        match histo_type:
            case  MeasurementType.HISTOGRAM_CORR :
                x = histo_measurement.getIndex()
                y = histo_measurement.getData()
                histo_measurement.clear()
                key = (request_params.histogram_measurement,request_params.measurement_type)
                data=(max(y),x[np.argmax(y)])
                self.measurements_data.save_data_histo(key,data)
                return [x,y]
            case MeasurementType.HISTOGRAM:
                x = histo_measurement.getIndex()
                y = histo_measurement.getData()
                histo_measurement.clear()
                key = (request_params.histogram_measurement,request_params.measurement_type)
                data=(max(y),x[np.argmax(y)])
                self.measurements_data.save_data_histo(key,data)
                return [x,y]
            case _: assert 0, "this" + histo_type.value + "correlation class doesn't exist"
