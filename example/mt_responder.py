#!/usr/bin/env python

# Core functions

# Python imports
import os
import sys
import signal
import threading

# Application imports

# Library imports
sys.path.append("../modules")
from modem  import Modem
from logger import log
from queue  import Queue
from parse  import Parse

# Global variables
QDIR = "moqueue"

# Instantiate objects
App    = Modem()
Parser = Parse()
Q      = Queue(QDIR)

# Check for the string "hi greg" in the SMD message
# if "hi greg" is found a reply is sent
# else it just logs the incoming message
# this could be usefull if you want signal the system to
# data only when instructed.

def _callback(data):
    print("Callback: %s" % data)
    if "hi greg" in data:

        Q.add("hi mike")

        old = os.stat(QDIR).st_mtime
        log.debug("Old time: %s" % repr(old))

        while Q.count() > 0:
            log.info("SBDIX mode set to 'send'.")
            monitor_mode[0] = "send"
            oldest_file = Q.get()

            with open(oldest_file) as f:
                data = f.read()

            t = threading.Thread(target=App.send_sbd_message, args=(data, oldest_file))
            t.start()
            Q.update(QDIR, old)
        log.debug("Queue empty.")
        log.info("Monitor mode set to 'listen'.")
        monitor_mode[0] = ["listen"]
    else:
        log.debug("message doesn't contain hi greg\nmessage: %s" % data)

# Check to make sure the modem is connected
print(App.status())

# Monitor serial port
try:
    initiate_stop = threading.Event()
    monitor_mode = ["listen"]
    t = threading.Thread(target=App.monitor, args=(initiate_stop, monitor_mode, _callback))
    t.daemon = True
    t.start()
    print "Thread count: ", threading.active_count()
    signal.pause()
except KeyboardInterrupt:
    initiate_stop.set()
    sys.exit(1)
