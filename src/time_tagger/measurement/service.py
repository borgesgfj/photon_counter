from collections import defaultdict
from dataclasses import dataclass
import TimeTagger as TT
from shared.constants.constants import INTEGRATION_TIME, SOURCE_RATE
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
    #Params added for the histogram plot
    histogram_measurement= None
    bin_width = 100
    n_bin = 100


class MeasurementService:
    def __init__(
        self,

        measurements_data: MeasurementRepository,
    ):
        self.measurements_data = measurements_data

    def record_measurement_data(self, request_params: CountRateReqParams):
        device_serial = request_params.device_serial
        channels = request_params.channels

        count_rate_data = self._get_count_rates(
            channels, request_params.time_tagger_network_proxy
        )
        return self.measurements_data.upsert_data(
            UpsertDataParams(
                channels=channels,
                data=count_rate_data,
                device_serial=device_serial,
                measurement_type=request_params.measurement_type,
            )
        )

    def _get_count_rates(self, channels: list[int], time_tagger_network_proxy: object):

        with TT.Countrate(
            tagger=time_tagger_network_proxy,
            channels=channels,
        ) as cr:

            cr.startFor(int(INTEGRATION_TIME), clear=True)
            cr.waitUntilFinished()

            counts = cr.getData()

            return counts

    def _getData_histo(self,request_params: CountRateReqParams):
        histo_type = request_params.measurement_type.value
        histo_measurement =request_params.histogram_measurement
        match histo_type:
            case  "HISTOGRAM_START_STOP" :
                return histo_measurement.getData()
            case  "HISTOGRAM_CORR" :
                x = histo_measurement.getIndex()
                y = histo_measurement.getData()
                return [x,y]
            case "HISTOGRAM" :
                x = histo_measurement.getIndex()
                y = histo_measurement.getData()
                return [x,y]
            case _: assert 0, "this" + histo_type + "correlation class doesn't exist"s

    def _get_channel_delay(self, channels: list[int], time_tagger_network_proxy: object, inspection_len = 200):
        timestamps_per_channel = defaultdict(list)

        with TT.TimeTagStream(
            tagger = time_tagger_network_proxy,
            n_max_events = (INTEGRATION_TIME * SOURCE_RATE * 1.1) / 1e12,
            channels = channels,
        ) as ts:

            ts.startFor(int(INTEGRATION_TIME))
            ts.waitUntilFinished()
            sb = ts.getData()

            for timestamp, event_type, channel in zip(sb.getTimestamps(), sb.getEventTypes(), sb.getChannels()):
                if event_type == 0:
                    timestamps_per_channel[channel].append(timestamp)

        alice = timestamps_per_channel[channels[0]]
        bob = timestamps_per_channel[channels[1]]

        errors = []
        global_min = float('inf')
        global_min_time = 0
        global_min_index = 0

        #Create a small slice from middle of Alice data
        alice_slice = alice[int(len(alice) / 2 - inspection_len/2): int(len(alice) / 2 + inspection_len/2)]
        alice_start_time = alice_slice[0]

        #Shift Alice data to start with 0
        alice_diffs = []
        for a in alice_slice:
            alice_diffs.append(a - alice_slice[0])

        # we will use whole bobs buffer to find alice fragment
        for bob_start_index in range(len(bob) - len(alice_diffs)):
            error = 0
            bob_index = bob_start_index
            bob_start_time = bob[bob_index]

            # we iterate alice buffer from 1 (we assume that alice[0] is alligned to bob[bob_index])
            for alice_index in range(1, len(alice_diffs)):
                #compute difference, between alice_index data and bob_index
                diff = (bob[bob_index] - bob_start_time) - alice_diffs[alice_index]

                diff_old = diff
                #if diff >= 0 bobs time stamp is greater then alices, so we can not increment bob index,
                #if diff < 0 alices time stamp is greater than bobs, so we will incremet bob indexes, until we "jump" over alice
                while diff < 0:
                    diff_old = diff
                    bob_index += 1
                    if bob_index >= len(bob):
                        bob_index = len(bob) - 1
                        break
                    diff = (bob[bob_index] - bob_start_time) - alice_diffs[alice_index]

                # we chceck if which Bobs timestamp (before and after "jumping" over Alice) is closer to Alice
                if abs(diff_old) < diff:
                    bob_index -= 1
                    error += abs(diff_old)
                else:
                    error += diff

            if error < global_min:
                global_min = error
                global_min_time = bob_start_time - alice_start_time
                global_min_index = bob_start_index

            errors.append(error)

        return global_min_time, global_min, errors, global_min_index
