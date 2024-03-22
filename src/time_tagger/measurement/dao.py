from dataclasses import dataclass
import TimeTagger as TT
from shared.constants.constants import INTEGRATION_TIME
from time_tagger.builder import TimeTaggerBuilder


@dataclass
class CountRateMeasurementReqParams:
    channels: list[int]
    time_tagger_network_proxy: object


class MeasurementDao:
    def __init__(self, time_tagger_builder: TimeTaggerBuilder) -> None:
        self.time_tagger_builder = time_tagger_builder

    def get_count_rates(
        self, count_rate_measurement_params: CountRateMeasurementReqParams
    ):
        channels = count_rate_measurement_params.channels

        with TT.Countrate(
            tagger=count_rate_measurement_params.time_tagger_network_proxy,
            channels=channels,
        ) as cr:

            cr.startFor(int(INTEGRATION_TIME), clear=True)
            cr.waitUntilFinished()

            counts = cr.getData()

            return counts