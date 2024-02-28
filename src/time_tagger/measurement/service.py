from dataclasses import dataclass
from time_tagger.builder import TimeTaggerBuilder


from time_tagger.measurement.dao import CountRateMeasurementReqParams, MeasurementDao
from time_tagger.measurement.repository import (
    MeasurementRepository,
    UpsertDataParams,
    MeasurementType,
)


@dataclass
class CountRateReqParams:
    channels: list[int]
    device_serial: str
    time_tagger_network_proxy: object
    measurement_type: MeasurementType
    #Params added for the histogram plot
    histogram_measurement= None
    bin_width = 100
    n_bin = 100

class MeasurementService:
    def __init__(
        self,
        time_tagger_measurement_dao: MeasurementDao,
        measurements_data: MeasurementRepository,
        time_tagger_virtual_channel_builder: TimeTaggerBuilder,
    ):
        self.time_tagger_measurement_dao = time_tagger_measurement_dao
        self.measurements_data = measurements_data
        self.virtual_channel_builder = time_tagger_virtual_channel_builder

    def record_measurement_data(self, request_params: CountRateReqParams):
        device_serial = request_params.device_serial

        
        channels = request_params.channels
        measurement_type =request_params.measurement_type.value
        if measurement_type in ["HISTOGRAM","HISTOGRAM_START_STOP","HISTOGRAM_CORR"]:
            if request_params.histogram_measurement == None:
                time_tagger = request_params.time_tagger_network_proxy
                request_params.histogram_measurement = self.virtual_channel_builder.build_histogram_measurment(time_tagger,
                                                                                                    channels,
                                                                                                    measurement_type,
                                                                                                    request_params.bin_width,request_params.n_bin)
            return self._getData_histo(request_params)
        else:
            count_rate_data = self.time_tagger_measurement_dao.get_count_rates(
                CountRateMeasurementReqParams(
                    channels,
                    request_params.time_tagger_network_proxy,
                )
            )
            return self.measurements_data.upsert_data(
                UpsertDataParams(
                    channels=channels,
                    data=count_rate_data,
                    device_serial=device_serial,
                    measurement_type=measurement_type,
                )
            )

    def _getData_histo(self,request_params: CountRateReqParams):
        histo_type = request_params.measurement_type.value
        histo_measurement =request_params.histogram_measurement
        match histo_type:
            case  "HISTOGRAM_START_STOP" : 
                return histo_measurement.getData()
            case  "HISTOGRAM_CORR" : 
                x = histo_measurement.getIndex()
                y = histo_measurement.getData() 
                return [x,y]
            case "HISTOGRAM" :
                x = histo_measurement.getIndex()
                y = histo_measurement.getData() 
                return [x,y]
            case _: assert 0, "this" + histo_type + "correlation class doesn't exist"