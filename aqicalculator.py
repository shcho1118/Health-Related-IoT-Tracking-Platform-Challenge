import sqlite3
from time import time

import aqi


class AQIOfData(object):
    def __init__(self, db_name, data_type, interval):
        self.db_name = db_name
        self.data_type = data_type
        self.interval = interval

    def get_avg(self):
        with sqlite3.connect('%s.db' % self.db_name) as con:
            cursor = con.cursor()
            cursor.execute('SELECT AVG(%s) FROM %s WHERE time > %d'
                           % (self.data_type, self.db_name, int(time()) - self.interval - 28800))
            avg = cursor.fetchone()[0]
        return avg

    def get_aqi(self):
        if self.data_type == 'NO2':
            constant = aqi.POLLUTANT_NO2_1H
        elif self.data_type == 'O3':
            constant = aqi.POLLUTANT_O3_8H
        elif self.data_type == 'CO':
            constant = aqi.POLLUTANT_CO_8H
        elif self.data_type == 'SO2':
            constant = aqi.POLLUTANT_SO2_1H
        elif self.data_type == 'PM25':
            constant = aqi.POLLUTANT_PM25
        else:
            return 0

        try:
            my_aqi = aqi.to_iaqi(constant, str(self.get_avg()), algo=aqi.ALGO_EPA)
        except Exception as e:
            print 'out of range'
            return 0
        return my_aqi


if __name__ == '__main__':
    no2 = AQIOfData('TEAMC_UDOO', 'NO2', 3600)
    o3 = AQIOfData('TEAMC_UDOO', 'O3', 28800)
    co = AQIOfData('TEAMC_UDOO', 'CO', 28800)
    so2 = AQIOfData('TEAMC_UDOO', 'SO2', 3600)
    pm25 = AQIOfData('TEAMC_UDOO', 'PM25', 86400)

    print no2.get_aqi()
    print o3.get_aqi()
    print co.get_aqi()
    print so2.get_aqi()
    print pm25.get_aqi()
