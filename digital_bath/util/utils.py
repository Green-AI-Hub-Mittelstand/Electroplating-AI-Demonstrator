import numpy as np


def generate_sensor_data(range):
    data = np.random.uniform(range[0], range[1])
    return data

def generate_json(temp_range, ph_range, ntu_range):
    temp = generate_sensor_data(temp_range)
    ph = generate_sensor_data(ph_range)
    ntu = generate_sensor_data(ntu_range)

    return {
        "pH": ph,
        "NTU": ntu,
        "Temperature": temp
    }