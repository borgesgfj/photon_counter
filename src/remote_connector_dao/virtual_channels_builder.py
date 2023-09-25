from itertools import combinations


def build_coincidences_virtual_channel(
    timetagger_proxy, tagger_controller, single_channels_list
):
    coincidence_channels_group = list(combinations(single_channels_list, 2))

    return timetagger_proxy.Coincidences(
        tagger_controller,
        coincidence_channels_group,
        coincidenceWindow=4000,
    )
