from remote_connector_dao.SignalCounter import SignalCounter


def calculate_graphs_vertical_axis_limit(signal_counter: SignalCounter):
    single_counts_max_value = max(
        [max(signal_counter.channel1), max(signal_counter.channel2)]
    )
    single_counts_min_value = min(
        [min(signal_counter.channel1), min(signal_counter.channel2)]
    )

    coincidences_max_value = max(signal_counter.coincidences)
    coincidences_min_value = min(signal_counter.coincidences)

    padding_rate = 0.1

    axis_padding = {
        "single_count_up_padding": single_counts_max_value * padding_rate
        if single_counts_max_value
        else 10,
        "single_count_bottom_padding": single_counts_min_value * padding_rate
        if single_counts_min_value
        else 1,
        "coincidences_up_padding": coincidences_max_value * padding_rate
        if coincidences_max_value
        else 10,
        "coincidences_bottom_padding": coincidences_min_value * padding_rate
        if coincidences_min_value
        else 1,
    }

    return {
        "single_counts_axis_max": single_counts_max_value
        + axis_padding["single_count_up_padding"],
        "single_counts_axis_min": single_counts_min_value
        - axis_padding["single_count_bottom_padding"],
        "coincidences_axis_max": coincidences_max_value
        + axis_padding["coincidences_up_padding"],
        "coincidences_axis_min": coincidences_min_value
        - axis_padding["coincidences_bottom_padding"],
    }
