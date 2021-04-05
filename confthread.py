import copy
import threading
import time

import requests


class ConfThread(threading.Thread):
    def __init__(self, server_url, mac_address):
        threading.Thread.__init__(self)
        self.server_url = server_url
        self.mac_address = mac_address
        self.delay_time = 5
        self.lock = threading.RLock()

    def run(self):
        time_stamp = time.time()
        while True:

            if (time.time() - time_stamp) > 5.0:
                print "aaaa"
                time_stamp = time.time()
                self.lock.acquire()
                print "acquired"
                response = requests.post(self.server_url, data={"macAdd": self.mac_address}, )
                self.delay_time = response.text
                self.lock.release()
                print "released"

    def get_delay_time(self):
        self.lock.acquire()
        print "before"
        result = copy.deepcopy(self.delay_time)
        print "after"
        self.lock.release()

        return result


def get_delay_time(server_url, mac_address):
    try:
        response = requests.post(server_url, data={"macAdd": mac_address}, )
    except Exception as e:
        return 5
    return response.text


if __name__ == '__main__':
    conf_thread = ConfThread("http://teamc-iot.calit2.net/jae/sensorConfig", '5C313E27CF63')
    conf_thread.daemon = True
    conf_thread.start()

    while True:
        print conf_thread.get_delay_time()
        time.sleep(1)
