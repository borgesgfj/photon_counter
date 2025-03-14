from itertools import combinations
import TimeTagger as TT
from  new_app.struct_and_enum import CountRateReqParams, MeasurementType
from PyQt5.QtCore import QObject,  pyqtSignal as Signal, pyqtSlot
# import PyQt5.QtCore.pyqtSignal as Signal


def build_coincidence_virtual_channel(
    time_tagger_network_proxy: object,
    coincidence_channels: list[int],
):
    # coincidence_channels_group = list(combinations(single_channels, 2))

    return TT.Coincidences(
        time_tagger_network_proxy,
        [coincidence_channels],
        coincidenceWindow=500,
    )

"""
Build the histogram measurment
Need: CountRateReqParams
"""
def build_histogram_measurment(params: CountRateReqParams):
    measurment_type = params.measurement_type
    time_tagger_network_proxy = params.time_tagger
    channels_list = params.channels
    bin_width = params.bin_width
    n_bin = params.n_bin
    match measurment_type:
        case  MeasurementType.HISTOGRAM_CORR : return TT.Correlation(time_tagger_network_proxy,*channels_list,bin_width, n_bin)
        case  MeasurementType.HISTOGRAM : return TT.Histogram(time_tagger_network_proxy,*channels_list,bin_width,n_bin)
        case _: assert 0, "this" + measurment_type.value + "correlation class doesn't exist"



class histo_thread(QObject):
    data = Signal(tuple)
    def __init__(self,request_param):
        super().__init__()
        # self.    
        self.request_params =request_param
        self.build_histogram_measurment()

    def build_histogram_measurment(self,):
        measurment_type = self.request_params.measurement_type
        time_tagger_network_proxy = self.request_params.time_tagger
        channels_list = self.request_params.channels
        bin_width = self.request_params.bin_width
        n_bin = self.request_params.n_bin
        match measurment_type:
            case  MeasurementType.HISTOGRAM_CORR :self.histo = TT.Correlation(time_tagger_network_proxy,*channels_list,bin_width, n_bin)
            case  MeasurementType.HISTOGRAM : self.histo = TT.Histogram(time_tagger_network_proxy,*channels_list,bin_width,n_bin)
            case _: assert 0, "this" + measurment_type.value + "correlation class doesn't exist"
    
    
    # @pyqtSlot()
    def getData_histo(self):
        # histo_type = self.request_params.measurement_type
        histo_measurement =self.histo
        histo_measurement.startFor(2e12,clear=True)
        histo_measurement.waitUntilFinished()
        x = histo_measurement.getIndex()
        y = histo_measurement.getData()
        histo_measurement.clear()
        key = (self.request_params.histogram_measurement,self.request_params.measurement_type)
        datas=(x,y)
        # repo.save_data_histo(key,data)
        self.data.emit(datas)
        # return [x,y]
          