import math
import time
import copy
import threading
import time
import requests

import serial

import neo

S0 = 3
S1 = 4
S2 = 5
S3 = 6
IO = neo.Gpio()
IO.pinMode(S0, IO.OUTPUT)
IO.pinMode(S1, IO.OUTPUT)
IO.pinMode(S2, IO.OUTPUT)
IO.pinMode(S3, IO.OUTPUT)
SCALE = float(open("/sys/bus/iio/devices/iio:device0/in_voltage_scale").read())
try:
    SER = serial.Serial('/dev/ttyACM0',115200,timeout=1)
    SER.flushOutput()
except Exception as e:
    pass
result = 25.0
past_result = 25.0

MUX = (
    (IO.LOW, IO.LOW, IO.LOW, IO.LOW),
    (IO.HIGH, IO.LOW, IO.LOW, IO.LOW),
    (IO.LOW, IO.HIGH, IO.LOW, IO.LOW),
    (IO.HIGH, IO.HIGH, IO.LOW, IO.LOW),
    (IO.LOW, IO.LOW, IO.HIGH, IO.LOW),
    (IO.HIGH, IO.LOW, IO.HIGH, IO.LOW),
    (IO.LOW, IO.HIGH, IO.HIGH, IO.LOW),
    (IO.HIGH, IO.HIGH, IO.HIGH, IO.LOW),
    (IO.LOW, IO.LOW, IO.LOW, IO.HIGH),
    (IO.HIGH, IO.LOW, IO.LOW, IO.HIGH),
    (IO.LOW, IO.HIGH, IO.LOW, IO.HIGH),
    (IO.HIGH, IO.HIGH, IO.LOW, IO.HIGH),
    (IO.LOW, IO.LOW, IO.HIGH, IO.HIGH),
    (IO.HIGH, IO.LOW, IO.HIGH, IO.HIGH),
    (IO.LOW, IO.HIGH, IO.HIGH, IO.HIGH),
    (IO.HIGH, IO.HIGH, IO.HIGH, IO.HIGH),
)

CALIBRATE = {
    "NO2": {0: 0.18, 10: 0.18, 20: 0.18, 30: 0.18, 40: 0.18, 50: 2.87},
    "O3": {0: 1.18, 10: 1.18, 20: 1.18, 30: 1.18, 40: 2.00, 50: 2.70},
    "CO": {0: 0.62, 10: 0.30, 20: 0.03, 30: -0.25, 40: -0.48, 50: -0.80},
    "SO2": {0: 0.85, 10: 0.85, 20: 1.15, 30: 1.45, 40: 1.75, 50: 1.95}
}


def read_a0():
    return int(open("/sys/bus/iio/devices/iio:device0/in_voltage0_raw").read()) * SCALE


def set_mux(output_pin):
    IO.digitalWrite(S0, MUX[output_pin][0])
    IO.digitalWrite(S1, MUX[output_pin][1])
    IO.digitalWrite(S2, MUX[output_pin][2])
    IO.digitalWrite(S3, MUX[output_pin][3])


def get_output(output_pin):
    set_mux(output_pin)
    time.sleep(0.05)
    result = read_a0()
    return result


def test_output():
    for i in range(10):
        print i, get_output(i)
    print ""
    time.sleep(1)


def get_temp():
    global result
    global past_result

    try:
        result = float(SER.readline())
        if math.isnan(result):
            raise Exception
        past_result = result
    except Exception as e:
        result = past_result

    return result


def get_no2():
    we = get_output(0)
    ae = get_output(1)
    we = we - 220
    ae = ae - 260
    temp = get_temp()
    if temp > 50:
        temp = 50
    ae = ae * CALIBRATE["NO2"][int(round(temp / 10) * 10)]
    we = we - ae
    if we < 0:
        we = 0
    we = we / 0.207
    return we


def get_o3():
    we = get_output(2)
    ae = get_output(3)
    we = we - 414
    ae = ae - 400
    temp = get_temp()
    if temp > 50:
        temp = 50
    ae = ae * CALIBRATE["O3"][int(round(temp / 10) * 10)]
    we = we - ae
    if we < 0:
        we = 0
    we = (we / 0.256) / 1000
    return we


def get_co():
    we = get_output(4)
    ae = get_output(5)
    we = we - 346
    ae = ae - 274
    temp = get_temp()
    if temp > 50:
        temp = 50
    ae = ae * CALIBRATE["CO"][int(round(temp / 10) * 10)]
    we = we - ae
    if we < 0:
        we = 0
    we = (we / 0.276) / 1000
    return we


def get_so2():
    we = get_output(6)
    ae = get_output(7)
    we = we - 300
    ae = ae - 294
    temp = get_temp()
    if temp > 50:
        temp = 50
    ae = ae * CALIBRATE["SO2"][int(round(temp / 10) * 10)]
    we = we - ae
    if we < 0:
        we = 0
    we = we / 0.300
    return we


def get_pm25():
    mv = get_output(9)
    v = mv / 1000
    hppcf = 240.0 * math.pow(v, 6) \
            - 2491.3 * math.pow(v, 5) \
            + 9448.7 * math.pow(v, 4) \
            - 14840.0 * math.pow(v, 3) \
            + 10684.0 * math.pow(v, 2) \
            + 2211.8 * v \
            + 7.9623
    ugm3 = .518 + .00274 * hppcf
    return ugm3


if __name__ == '__main__':
    while True:
        start_time = time.time()
        print "Temp:", get_temp()
        print "NO2:", get_no2()
        print "O3:", get_o3()
        print "CO:", get_co()
        print "SO2:", get_so2()
        print "PM25:", get_pm25()
        print time.time() - start_time
        print ""
