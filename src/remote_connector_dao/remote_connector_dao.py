import base64
import io
import numpy as np
import Pyro5.api


def _load_numpy_array_from_buffer(class_name, data):
    assert class_name == "numpy.ndarray"
    buffer = io.BytesIO(base64.b64decode(data["data"].encode("ASCII")))
    return np.load(buffer, allow_pickle=False)


def _serialize_data_from_server():
    Pyro5.api.register_dict_to_class(
        classname="numpy.ndarray", converter=_load_numpy_array_from_buffer
    )


def _get_server_proxy(host_address):
    return Pyro5.api.Proxy(f"PYRO:TimeTagger@{host_address}")


def connect_to_server(server_address):
    _serialize_data_from_server()

    timetagger = _get_server_proxy(server_address)

    tagger = timetagger.createTimeTagger()

    print(f"Connected to Timetagger with serial: {tagger.getSerial()}")

    return (tagger, timetagger)
