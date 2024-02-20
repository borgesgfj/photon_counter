from dataclasses import dataclass
import TimeTagger as TT


@dataclass
class SetTriggerLevelParams:
    time_tagger_network_proxy: object
    channels_voltage: dict[int, float]


class TimeTaggerHardwarePropertiesDao:
    def __init__(self) -> None:
        pass

    def set_trigger_level(self, set_trigger_level_params: SetTriggerLevelParams):
        for channel, voltage in set_trigger_level_params.channels_voltage.items():
            TT.TimeTaggerNetwork.setTriggerLevel(
                set_trigger_level_params.time_tagger_network_proxy,
                channel=channel,
                voltage=voltage,
            )

    def get_time_tagger_serial_number(self, time_tagger_network_proxy):

        return TT.TimeTaggerNetwork.getSerial(time_tagger_network_proxy)

    def get_channels_trigger_level(self, channels: list[int], time_tagger_proxy):

        return {
            channel: TT.TimeTaggerNetwork.getTriggerLevel(time_tagger_proxy, channel)
            for channel in channels
        }
