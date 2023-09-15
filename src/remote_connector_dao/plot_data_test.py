import time
from remote_connector_dao.remote_connector_dao import connect_to_server
import numpy as np
import matplotlib.pyplot as plt


tagger, TimeTagger = connect_to_server("192.168.1.162:23000")

tagger.setTriggerLevel(1, 0.09)
tagger.setTriggerLevel(2, 0.09)

hist = TimeTagger.Histogram(
    tagger, start_channel=2, click_channel=1, binwidth=100, n_bins=1000
)

hist.startFor(int(10e12), clear=True)

while hist.isRunning():
    time.sleep(0.3)

data = np.array(hist.getData())
print(np.max(data))
# trigger_counts = corr.getCounts()
plt.figure(figsize=(3, 2))
plt.plot(data)
plt.show()

# Cleanup
TimeTagger.freeTimeTagger(tagger)
del hist
del tagger
del TimeTagger
