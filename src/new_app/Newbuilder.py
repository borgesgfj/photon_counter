from itertools import combinations
import TimeTagger as TT
from  new_app.struct_and_enum import CountRateReqParams, MeasurementType

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
