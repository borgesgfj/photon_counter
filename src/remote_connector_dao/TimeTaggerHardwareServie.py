from dataclasses import dataclass
import TimeTagger as TT


@dataclass
class SetTriggerLevelDto:
    time_tagger_network_proxy: object
    channels_voltage: dict[int, float]


class TimeTaggerHardwareService:
    def __init__(self) -> None:
        pass

    def setTriggerLevel(self, set_trigger_level_dto: SetTriggerLevelDto):
        for channel in set_trigger_level_dto.channels_voltage:
            TT.TimeTaggerNetwork.setTriggerLevel(
                set_trigger_level_dto.time_tagger_network_proxy,
                channel=channel,
                voltage=set_trigger_level_dto.channels_voltage[channel],
            )

    def getTimeTaggerSerialNumber(self, time_tagger_network_proxy):

        return TT.TimeTaggerNetwork.getSerial(time_tagger_network_proxy)
