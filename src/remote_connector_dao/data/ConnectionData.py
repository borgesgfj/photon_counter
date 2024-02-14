from dataclasses import dataclass
from enum import Enum


class ConnectionStatusEnum(Enum):
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class TimeTaggerConnectionResDto:
    time_tagger_aliases: str
    tagger_proxy: object
    connection_status: ConnectionStatusEnum
    serial_number: str = None


class TimeTaggerConnectionData:
    def __init__(self) -> None:
        self._registered_devices: dict[str, TimeTaggerConnectionResDto] = {}

    def save_time_tagger_connection_info(
        self, connection_response: TimeTaggerConnectionResDto
    ):
        self._registered_devices[connection_response.time_tagger_aliases] = (
            connection_response
        )

    def get_time_taggers_by_connection_status(
        self, connection_status: ConnectionStatusEnum
    ) -> list[TimeTaggerConnectionResDto]:

        return [
            device
            for device in self._registered_devices.values()
            if device.connection_status == connection_status
        ]

    def get_time_tagger_by_alias(self, time_tagger_alias: str):

        if time_tagger_alias in self._registered_devices:
            return self._registered_devices[time_tagger_alias]

        raise NameError(f"Device {time_tagger_alias} not found")
