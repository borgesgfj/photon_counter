from dataclasses import dataclass
import TimeTagger as TT
from remote_connector_dao.data.ConnectionData import (
    TimeTaggerConnectionResDto,
    TimeTaggerConnectionData,
    ConnectionStatusEnum,
)


@dataclass
class TimeTaggerAddressInfoDto:
    host_address: str
    port: str
    time_tagger_alias: str


class TimeTaggerNetworkConnectionService:
    def __init__(
        self,
        time_tagger_connection_data: TimeTaggerConnectionData,
    ):
        self.connection_data = time_tagger_connection_data

    def connect_to_TimeTagger_server(
        self,
        time_taggers_info: list[TimeTaggerAddressInfoDto],
    ):
        for time_tagger in time_taggers_info:
            try:
                tagger = TT.createTimeTaggerNetwork(
                    f"{time_tagger.host_address}:{time_tagger.port}"
                )

                serial_number = TT.TimeTaggerNetwork.getSerial(tagger)

                self.connection_data.save_time_tagger_connection_info(
                    TimeTaggerConnectionResDto(
                        time_tagger_aliases=time_tagger.time_tagger_alias,
                        tagger_proxy=tagger,
                        connection_status=ConnectionStatusEnum.SUCCESS.value,
                        serial_number=serial_number,
                    ),
                )

                print(serial_number, "serial number")

            except Exception:
                self.connection_data.save_time_tagger_connection_info(
                    TimeTaggerConnectionResDto(
                        time_tagger_aliases=time_tagger.time_tagger_alias,
                        tagger_proxy={},
                        connection_status=ConnectionStatusEnum.FAILED.value,
                    )
                )
                continue

        return self.connection_data.get_time_taggers_by_connection_status(
            ConnectionStatusEnum.SUCCESS.value
        )

    def close_time_tagger_connection(self, time_tagger_alias: str):
        time_tagger_info = self.connection_data.get_time_tagger_by_alias(time_tagger_alias)

        TT.freeTimeTagger(time_tagger_info.tagger_proxy)

        print(f"connection of {time_tagger_alias} closed!")
