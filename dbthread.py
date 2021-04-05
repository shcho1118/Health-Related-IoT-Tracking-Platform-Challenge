import copy
import sqlite3
import threading
from time import time

import sensor


class DBThread(threading.Thread):
    def __init__(self, db_name):
        threading.Thread.__init__(self)
        self.db_name = db_name
        self.lock = threading.RLock()
        self.result = ()

    def run(self):
        with sqlite3.connect('%s.db' % self.db_name) as con:
            cursor = con.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS %s %s'
                           % (self.db_name, '(time int, temp real, NO2 real, O3 real, CO real, SO2 real, PM25 real)'))
            while True:
                self.lock.acquire()
                self.result = (int(time()) - 28800,
                               sensor.get_temp(),
                               sensor.get_no2(),
                               sensor.get_o3(),
                               sensor.get_co(),
                               sensor.get_so2(),
                               sensor.get_pm25())
                cursor.execute('INSERT INTO %s %s VALUES %s'
                               % (self.db_name, '(time, temp, NO2, O3, CO, SO2, PM25)', str(self.result)))
                con.commit()
                self.lock.release()

    def get_result(self):
        self.lock.acquire()
        result = copy.deepcopy(self.result)
        self.lock.release()
        return result
