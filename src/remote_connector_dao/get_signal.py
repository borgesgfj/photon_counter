import time
from remote_connector_dao.constants import SLEEP_TIME, INTEGRATION_TIME


def get_count_rates(timetagger_proxy, tagger_controller, channels):
    with timetagger_proxy.Countrate(tagger_controller, channels) as cr:
        cr.startFor(int(INTEGRATION_TIME), clear=True)

        while cr.isRunning():
            time.sleep(SLEEP_TIME)

        counts = cr.getData()

        return counts
