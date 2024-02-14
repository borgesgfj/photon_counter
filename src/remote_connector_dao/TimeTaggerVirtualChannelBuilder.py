import TimeTagger as TT


class TimeTaggerVirtualChannelBuilder:
    def __init__(self) -> None:
        pass

    def build_coincidence_virtual_channel(
        self,
        time_tagger_network_proxy: object,
        coincidence_channels_group: list[list[int]],
    ):
        return TT.Coincidences(
            time_tagger_network_proxy,
            coincidence_channels_group,
            coincidenceWindow=4000,
        )
