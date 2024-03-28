from itertools import combinations
import TimeTagger as TT
import time_tagger
from time_tagger.measurement.repository import MeasurementType
from time_tagger.measurement.service import CountRateReqParams

class TimeTaggerBuilder:
    def __init__(self) -> None:
        pass

    def build_coincidence_virtual_channel(
        self,
        time_tagger_network_proxy: object,
        single_channels: list[int],
    ):
        coincidence_channels_group = list(combinations(single_channels, 2))

        return TT.Coincidences(
            time_tagger_network_proxy,
            coincidence_channels_group,
            coincidenceWindow=4000,
        )

    """
    Build the histogram measurment
    Need: CountRateReqParams
    """
    def build_histogram_measurment(self, params: CountRateReqParams):
        measurment_type = params.measurement_type
        time_tagger_network_proxy = params.time_tagger_network_proxy
        channels_list = params.channels
        bin_width = params.bin_width
        n_bin = params.n_bin
        match measurment_type:
            case  MeasurementType.HISTOGRAM_START_STOP : return TT.StartStop(time_tagger_network_proxy,*channels_list,bin_width)
            case  MeasurementType.HISTOGRAM_CORR : return TT.Correlation(time_tagger_network_proxy,*channels_list,bin_width, n_bin)
            case  MeasurementType.HISTOGRAM : return TT.Histogram(time_tagger_network_proxy,*channels_list,bin_width,n_bin)
            case _: assert 0, "this" + measurment_type + "correlation class doesn't exist"
