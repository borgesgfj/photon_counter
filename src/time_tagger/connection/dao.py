import TimeTagger as TT


class ConnectionDao:
    def __init__(self) -> None:
        pass

    def create_time_tagger_network_proxy(self, host_address: str, port: str):

        return TT.createTimeTaggerNetwork(f"{host_address}:{port}")

    def disconnect_device(self, time_tagger_proxy):
        TT.freeTimeTagger(time_tagger_proxy)
