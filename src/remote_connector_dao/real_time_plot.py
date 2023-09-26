from functools import partial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from remote_connector_dao.get_signal import get_count_rates

CHANNEL1_COUNTS, CHANNEL2_COUNTS, COINCIDENCES, ELAPSED_TIME = [0], [0], [0], [0]


def update_data(timetagger_proxy, timetagger_controller, channels_list):
    channel1, channel2, coincidences = get_count_rates(
        timetagger_proxy, timetagger_controller, channels_list
    )

    CHANNEL1_COUNTS.append(channel1)
    CHANNEL2_COUNTS.append(channel2)
    COINCIDENCES.append(coincidences)
    ELAPSED_TIME.append(ELAPSED_TIME[-1] + 1)

    if len(ELAPSED_TIME) > 100 or ELAPSED_TIME[0] == 0:
        CHANNEL1_COUNTS.pop(0)
        CHANNEL2_COUNTS.pop(0)
        COINCIDENCES.pop(0)
        ELAPSED_TIME.pop(0)

    return CHANNEL1_COUNTS, CHANNEL2_COUNTS, COINCIDENCES, ELAPSED_TIME


def animate(
    frames,
    timetagger_proxy,
    timetagger_controller,
    channels_list,
    graph1_object,
    graph2_object,
):
    channel1_data, channel2_data, coincidences_data, elapsed_time = update_data(
        timetagger_proxy, timetagger_controller, channels_list
    )

    graph1_object.cla()
    graph1_object.plot(elapsed_time, channel1_data, label="1", marker="o", color="r")
    graph1_object.plot(elapsed_time, channel2_data, label="2", marker="s", color="b")
    graph1_object.grid(axis="y", linewidth=1, alpha=0.6, linestyle='--')
    graph1_object.margins(x=0)
    graph1_object.legend(loc="upper right")

    graph2_object.cla()
    graph2_object.plot(
        elapsed_time, coincidences_data, label="CC", marker="^", color="k"
    )
    graph2_object.grid(axis="y", linewidth=1, alpha=0.6, linestyle='--')
    graph2_object.margins(x=0)
    graph2_object.legend(loc="upper right")
    plt.tight_layout()


def plot_real_time_graph(timetagger_proxy, timetagger_controller, channels_list):
    fig, (ax1, ax2) = plt.subplots(2, 1)

    ani = FuncAnimation(
        fig,
        partial(
            animate,
            timetagger_proxy=timetagger_proxy,
            timetagger_controller=timetagger_controller,
            channels_list=channels_list,
            graph1_object=ax1,
            graph2_object=ax2,
        ),
        interval=500,
    )
    plt.tight_layout()
    plt.show()
    timetagger_proxy.freeTimeTagger(timetagger_controller)
