#!/usr/bin/env python

import os
import time
import datetime
from datetime import timedelta


class Set_time(object):
    def __init__(self):
        self.era2 = datetime.datetime(2014, 05, 11, 14, 23, 55)
        self.ninety_miliseconds_ina_second = (1/0.09)

    def calculate_time(self, hextime):
        mssstm_in_dec = int(hextime, 16)
        seconds_since_iridium_epoch =\
            (mssstm_in_dec/self.ninety_miliseconds_ina_second)
        time_from_iridium = self.era2 +\
            timedelta(seconds=seconds_since_iridium_epoch)
        return time_from_iridium

    def set_system_time(self, updated_time):
        try:
            os.system("date %s" % updated_time.strftime("%m%d%H%M%Y.%S"))
        except Exception:
            print 'system set time failure!'
