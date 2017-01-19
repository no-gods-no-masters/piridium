#!/usr/bin/env python

# Receive & Process MT Data
#
# Run on the RockBLOCK and sets up a listener to await incoming Mobile
# Terminated (MT) data and implements a callback function for processing the
# included messages. It needs to be running for messages from mt_send.py to
# be picked up.
#
# See README.md for documentation.

# Python imports
import sys
import signal
import threading

# Application imports
sys.path.append("../modules")
from modem import Modem

# Executed on the value returned by the RockBLOCK. Use it to process the data
# and act on the result.
def _callback(value):
    print("Response: %s" % value)

# Instantiate Modem class
App = Modem()

# Check to make sure the modem is connected
print(App.status())

# Monitor serial port.
# Allow ^C to exit gracefully.
try:
    initiate_stop = threading.Event()
    monitor_mode  = ["listen"]

    t = threading.Thread(
        target=App.monitor, args=(initiate_stop, monitor_mode, _callback)
    )

    t.daemon = True
    t.start()

    signal.pause()
except KeyboardInterrupt:
    initiate_stop.set()
    sys.exit(1)
