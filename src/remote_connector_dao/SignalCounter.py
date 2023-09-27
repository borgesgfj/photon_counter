class SignalCounter:
    def __init__(self) -> None:
        self.elapsed_time = []
        self.coincidences = []
        self.channel1 = []
        self.channel2 = []

    def record_measurement(
        self,
        channel1_instant_signal,
        channel2_instant_signal,
        coincidences_instant_signal,
    ):
        previous_elapsed_time = self.elapsed_time[-1] if self.elapsed_time else 0
        self.channel1.append(channel1_instant_signal)
        self.channel2.append(channel2_instant_signal)
        self.coincidences.append(coincidences_instant_signal)
        self.elapsed_time.append(previous_elapsed_time + 1)

        if len(self.elapsed_time) > 100:
            self.channel1.pop(0)
            self.channel2.pop(0)
            self.coincidences.pop(0)
            self.elapsed_time.pop(0)
