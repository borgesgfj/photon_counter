from itertools import combinations
import TimeTagger as TT


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
    Need:
        the type of measurment
        bin width in ps
        number of bin
    """
    def build_histogram_measurment(self, time_tagger_network_proxy: object,
        channels_list: list[int], measurment_type,bin_width=100, n_bin=1000):
        match measurment_type:
            case  "HISTOGRAM_START_STOP" : return TT.StartStop(time_tagger_network_proxy,*channels_list,bin_width)
            case  "HISTOGRAM_CORR" : return TT.Correlation(time_tagger_network_proxy,*channels_list,bin_width, n_bin)
            case "HISTOGRAM" : return TT.Histogram(time_tagger_network_proxy,*channels_list,bin_width,n_bin)
            case _: assert 0, "this" + measurment_type + "correlation class doesn't exist"