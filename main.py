import asyncore
import json
import re
import subprocess
import threading
import time

from aqicalculator import AQIOfData
from bterror import BTError
from btserver import BTServer
from confthread import *
from dbthread import DBThread


def get_mac_address():
    result = ''
    out = subprocess.check_output(["hcitool", "dev"])
    p = re.compile(ur'(?:[0-9a-fA-F]:?){12}')
    mac = re.findall(p, out)[0]
    for i in mac.split(':'):
        result += i
    return result


if __name__ == '__main__':
    # Create a BT server
    uuid = "00001101-0000-1000-8000-00805F9B34FB"
    service_name = "TEAMC_UDOO"
    server = BTServer(uuid, service_name)

    no2 = AQIOfData(service_name, 'NO2', 3600)
    o3 = AQIOfData(service_name, 'O3', 28800)
    co = AQIOfData(service_name, 'CO', 28800)
    so2 = AQIOfData(service_name, 'SO2', 3600)
    pm25 = AQIOfData(service_name, 'PM25', 86400)

    # Create the server thread and run it
    server_thread = threading.Thread(target=asyncore.loop, name="TEAMC UDOO BT Server Thread")
    server_thread.daemon = True
    server_thread.start()

    db_thread = DBThread(service_name)
    db_thread.daemon = True
    db_thread.start()

    teamc_server = 'http://teamc-iot.calit2.net/jae/sensorConfig'
    bd_addr = get_mac_address()
    # print bd_addr
    # conf_thread = ConfThread(teamc_server, bd_addr)
    # conf_thread.daemon = True
    # conf_thread.start()

    while True:
        for client_handler in server.active_client_handlers.copy():
            # Use a copy() to get the copy of the set, avoiding 'set change size during iteration' error
            result = db_thread.get_result()
            epoch_time = result[0]
            temp = result[1]
            SN1 = result[2] / 1000
            SN2 = result[3]
            SN3 = result[4]
            SN4 = result[5] / 1000
            PM25 = result[6]

            no2_aqi = float(no2.get_aqi())
            o3_aqi = float(o3.get_aqi())
            co_aqi = float(co.get_aqi())
            so2_aqi = float(so2.get_aqi())
            pm25_aqi = float(pm25.get_aqi())

            msg = ""
            output = {'time': epoch_time,
                      'temp': temp,
                      'NO2': SN1,
                      'O3': SN2,
                      'CO': SN3,
                      'SO2': SN4,
                      'PM25': PM25,
                      'NO2_aqi': no2_aqi,
                      'O3_aqi': o3_aqi,
                      'CO_aqi': co_aqi,
                      'SO2_aqi': so2_aqi,
                      'PM25_aqi': pm25_aqi
                      }
            print output
            msg = json.dumps(output)
            try:
                client_handler.send(msg + '\n')
            except Exception as e:
                print (client_handler)
                BTError.print_error(handler=client_handler, error=BTError.ERR_WRITE, error_message=repr(e))
        time.sleep(float(get_delay_time(teamc_server, bd_addr)))