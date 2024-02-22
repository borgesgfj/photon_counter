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
