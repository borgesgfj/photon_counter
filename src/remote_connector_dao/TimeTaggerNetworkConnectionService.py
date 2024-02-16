from dataclasses import dataclass
import TimeTagger as TT
from remote_connector_dao.data.ConnectionData import (
    TimeTaggerConnectionInfoDto,
    TimeTaggerConnectionData,
    ConnectionStatusEnum,
)
from remote_connector_dao.TimeTaggerHardwarePropertiesService import (
    TimeTaggerHardwarePropertiesService,
)
from remote_connector_dao.ErrorMessageEnum import ErrorMessageEnum


@dataclass
class TimeTaggerAddressInfoDto:
    host_address: str
    port: str
    time_tagger_name: str


@dataclass
class TimeTaggerConnectionRes:
    connected_devices: list[TimeTaggerConnectionInfoDto]
    connection_failed_devices: list[TimeTaggerConnectionInfoDto]


class TimeTaggerNetworkConnectionService:
    def __init__(
        self,
        time_tagger_connection_data: TimeTaggerConnectionData,
        time_tagger_hardware_service: TimeTaggerHardwarePropertiesService,
    ):
        self.connection_data = time_tagger_connection_data
        self.time_tagger_hardware_service = time_tagger_hardware_service

    def connect_to_time_tagger_server(
        self,
        time_taggers_info: list[TimeTaggerAddressInfoDto],
    ) -> TimeTaggerConnectionRes:

        connected_devices = []
        connection_failed_devices = []

        for time_tagger in time_taggers_info:
            try:
                self._validate_time_tagger_name(time_tagger.time_tagger_name)

                tagger = TT.createTimeTaggerNetwork(
                    f"{time_tagger.host_address}:{time_tagger.port}"
                )
                serial_number = self.time_tagger_hardware_service.get_time_tagger_serial_number(
                    tagger
                )

                connection_info_res = self.connection_data.upsert_time_tagger_connection_info(
                    TimeTaggerConnectionInfoDto(
                        time_tagger_name=time_tagger.time_tagger_name,
                        tagger_proxy=tagger,
                        connection_status=ConnectionStatusEnum.SUCCESS.value,
                        serial_number=serial_number,
                    ),
                )

                connected_devices.append(connection_info_res)

            except RuntimeError:
                connection_failed_info = self.connection_data.upsert_time_tagger_connection_info(
                    TimeTaggerConnectionInfoDto(
                        time_tagger_name=time_tagger.time_tagger_name,
                        tagger_proxy={},
                        connection_status=ConnectionStatusEnum.FAILED.value,
                    )
                )
                connection_failed_devices.append(connection_failed_info)
                continue
            except ValueError as er:
                raise er

        return TimeTaggerConnectionRes(
            connected_devices=connected_devices, connection_failed_devices=connection_failed_devices
        )

    def close_time_tagger_connection(
        self, time_tagger_name: str, time_tagger_network_proxy: object
    ):
        TT.freeTimeTagger(time_tagger_network_proxy)
        self.connection_data.delete_connection_data(time_tagger_name)

        print(f"connection of {time_tagger_name} closed!")

    def get_connection_failed_time_taggers_name(self) -> list[str]:
        connection_failed_devices = self.connection_data.get_time_taggers_by_connection_status(
            ConnectionStatusEnum.FAILED.value
        )

        return [device.time_tagger_name for device in connection_failed_devices]

    def _validate_time_tagger_name(self, new_time_tagger_name: str):
        connected_devices_name = self.connection_data.get_time_tagger_name_by_connection_status(
            ConnectionStatusEnum.SUCCESS.value
        )

        if not new_time_tagger_name:
            raise ValueError(ErrorMessageEnum.CANNOT_ASSIGN_EMPTY_STRING.value)

        if new_time_tagger_name in connected_devices_name:
            raise ValueError(ErrorMessageEnum.DEVICE_NAME_ALREADY_IN_USE.value)
