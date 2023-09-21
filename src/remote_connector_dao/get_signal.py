import time
from remote_connector_dao.virtual_channels_builder import (
    build_coincidences_virtual_channel,
)
from remote_connector_dao.constants import TRIGGER_VOLTAGE, SLEEP_TIME, INTEGRATION_TIME


def get_count_rates(timetagger_proxy, tagger_controller, single_channels_list):
    for channel in single_channels_list:
        tagger_controller.setTriggerLevel(channel, TRIGGER_VOLTAGE)

    coincidences_virtual_channel = build_coincidences_virtual_channel(
        timetagger_proxy, tagger_controller, single_channels_list
    )

    channels = [*single_channels_list, coincidences_virtual_channel.getChannels()[0]]

    with timetagger_proxy.Countrate(tagger_controller, channels) as cr:
        cr.startFor(int(INTEGRATION_TIME), clear=True)

        while cr.isRunning():
            time.sleep(SLEEP_TIME)

        counts = cr.getData()

        timetagger_proxy.freeTimeTagger(tagger_controller)

        return counts
