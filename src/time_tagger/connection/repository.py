from dataclasses import dataclass
from enum import Enum


class ConnectionStatusEnum(Enum):
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class TimeTaggerConnectionInfoDto:
    time_tagger_name: str
    tagger_proxy: object
    connection_status: ConnectionStatusEnum
    serial_number: str = None


class ConnectionRepository:
    def __init__(self) -> None:
        self._registered_devices: dict[str, TimeTaggerConnectionInfoDto] = {}

    def upsert_time_tagger_connection_info(
        self, connection_response: TimeTaggerConnectionInfoDto
    ):
        self._registered_devices[connection_response.time_tagger_name] = (
            connection_response
        )

        return self._registered_devices[connection_response.time_tagger_name]

    def get_time_taggers_by_connection_status(
        self, connection_status: ConnectionStatusEnum
    ) -> list[TimeTaggerConnectionInfoDto]:

        return [
            device
            for device in self._registered_devices.values()
            if device.connection_status == connection_status.value
        ]

    def get_time_tagger_name_by_connection_status(
        self, connection_status: ConnectionStatusEnum
    ):
        devices_connection_info = self.get_time_taggers_by_connection_status(
            connection_status
        )

        return [device.time_tagger_name for device in devices_connection_info]

    def delete_connection_data(self, time_tagger_name: str):
        self._registered_devices.pop(time_tagger_name, None)
