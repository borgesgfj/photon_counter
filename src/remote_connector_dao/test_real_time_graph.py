from remote_connector_dao.remote_connector_dao import connect_to_server
from remote_connector_dao.real_time_plot import plot_real_time_graph
from remote_connector_dao.constants import TRIGGER_VOLTAGE
from remote_connector_dao.virtual_channels_builder import (
    build_coincidences_virtual_channel,
)


def run_real_time_graph():
    tagger_controller, timetagger_proxy = connect_to_server("192.168.1.162:23000")
    single_channels_list = [1, 2]

    coincidences_virtual_channel = build_coincidences_virtual_channel(
        timetagger_proxy, tagger_controller, single_channels_list
    )

    channels = [*single_channels_list, coincidences_virtual_channel.getChannels()[0]]

    for channel in single_channels_list:
        tagger_controller.setTriggerLevel(channel, TRIGGER_VOLTAGE)

    plot_real_time_graph(timetagger_proxy, tagger_controller, channels)
