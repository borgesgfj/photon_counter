from dataclasses import dataclass
from time_tagger.builder import TimeTaggerBuilder


from time_tagger.measurement.dao import CountRateMeasurementReqParams, MeasurementDao
from time_tagger.measurement.repository import (
    MeasurementRepository,
    UpsertDataParams,
    MeasurementType,
)


@dataclass
class CountRateReqParams:
    channels: list[int]
    device_serial: str
    time_tagger_network_proxy: object
    measurement_type: MeasurementType


class MeasurementService:
    def __init__(
        self,
        time_tagger_measurement_dao: MeasurementDao,
        measurements_data: MeasurementRepository,
        time_tagger_virtual_channel_builder: TimeTaggerBuilder,
    ):
        self.time_tagger_measurement_dao = time_tagger_measurement_dao
        self.measurements_data = measurements_data
        self.virtual_channel_builder = time_tagger_virtual_channel_builder

    def record_measurement_data(self, request_params: CountRateReqParams):
        device_serial = request_params.device_serial
        channels = request_params.channels

        count_rate_data = self.time_tagger_measurement_dao.get_count_rates(
            CountRateMeasurementReqParams(
                channels,
                request_params.time_tagger_network_proxy,
            )
        )
        return self.measurements_data.upsert_data(
            UpsertDataParams(
                channels=channels,
                data=count_rate_data,
                device_serial=device_serial,
                measurement_type=request_params.measurement_type,
            )
        )
