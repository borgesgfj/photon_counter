from dataclasses import dataclass
import TimeTagger as TT


@dataclass
class SetTriggerLevelDto:
    time_tagger_network_proxy: object
    channels_voltage: dict[int, float]


class TimeTaggerHardwarePropertiesDao:
    def __init__(self) -> None:
        pass

    def set_trigger_level(self, set_trigger_level_dto: SetTriggerLevelDto):
        for channel in set_trigger_level_dto.channels_voltage:
            TT.TimeTaggerNetwork.setTriggerLevel(
                set_trigger_level_dto.time_tagger_network_proxy,
                channel=channel,
                voltage=set_trigger_level_dto.channels_voltage[channel],
            )

    def get_time_tagger_serial_number(self, time_tagger_network_proxy):

        return TT.TimeTaggerNetwork.getSerial(time_tagger_network_proxy)

    def get_channels_trigger_level(self, channels: list[int], time_tagger_proxy):
        triggers_level = {}

        for channel in channels:
            triggers_level[channel] = TT.TimeTaggerNetwork.getTriggerLevel(
                time_tagger_proxy, channel
            )

        return triggers_level
