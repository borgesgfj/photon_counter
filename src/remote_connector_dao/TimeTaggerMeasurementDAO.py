from dataclasses import dataclass
import TimeTagger as TT
from remote_connector_dao.constants import INTEGRATION_TIME


@dataclass
class CountRateMeasurementDto:
    channels: list[int]
    time_tagger_network_proxy: object


class TimeTaggerMeasurementDAO:
    def __init__(self) -> None:
        pass

    def get_count_rates(self, count_rate_measurement_dto: CountRateMeasurementDto):
        channels = count_rate_measurement_dto.channels

        with TT.Countrate(
            tagger=count_rate_measurement_dto.time_tagger_network_proxy,
            channels=channels,
        ) as cr:

            cr.startFor(int(INTEGRATION_TIME), clear=True)
            cr.waitUntilFinished()

            counts = cr.getData()

            return counts
