import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from remote_connector_dao.get_signal import get_count_rates
from remote_connector_dao.constants import GRAPH_ANIMATION_INTERVAL
from remote_connector_dao.SignalCounter import SignalCounter

plt.style.use("src/remote_connector_dao/styles/graphsStyle.mplstyle")


def update_data(
    timetagger_proxy,
    timetagger_controller,
    channels_list,
    signal_counter: SignalCounter,
):
    channel1_counts, channel2_counts, coincidences_counts = get_count_rates(
        timetagger_proxy, timetagger_controller, channels_list
    )

    signal_counter.record_measurement(
        channel1_counts, channel2_counts, coincidences_counts
    )


def plot(
    graph1_object,
    graph2_object,
    signal_counter: SignalCounter,
):
    elapsed_time = signal_counter.elapsed_time

    graph1_object.cla()
    graph1_object.plot(elapsed_time, signal_counter.channel1, label="1")
    graph1_object.plot(elapsed_time, signal_counter.channel2, label="2")
    graph1_object.legend(loc="upper right")
    graph1_object.autoscale_view()

    graph2_object.cla()
    graph2_object.plot(elapsed_time, signal_counter.coincidences, label="CC")
    graph2_object.legend(loc="upper right")
    plt.tight_layout()


def plot_real_time_graph(
    timetagger_proxy,
    timetagger_controller,
    channels_list,
):
    fig, (ax1, ax2) = plt.subplots(2, 1)

    signal_counter = SignalCounter()

    def animate(frame):
        update_data(
            timetagger_proxy, timetagger_controller, channels_list, signal_counter
        )
        plot(ax1, ax2, signal_counter)

    ani = FuncAnimation(
        fig,
        animate,
        interval=GRAPH_ANIMATION_INTERVAL,
    )
    plt.tight_layout()
    plt.show()
    timetagger_proxy.freeTimeTagger(timetagger_controller)
