#!/usr/bin/env python

# Check for a string as defined in config.ini in an SBD message. If the string
# matches, a reply (also defined in config.ini) is sent, else it just logs the
# incoming message.

# Python imports
import os
import sys
import signal
import threading

# Application imports
sys.path.append("../modules")
from config import Config
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

# Callback is fired when an SBD message comes in.
def _callback(data):
    print("Callback: %s" % data)

    message_response = Config.get("respond")["response"]
    string_to_match  = Config.get("respond")["match"]

    if string_to_match in data:
        Q.add(message_response)

        old = os.stat(QDIR).st_mtime
        log.debug("Old time: %s" % repr(old))

        while Q.count() > 0:
            log.info("SBDIX mode set to 'send'.")

            monitor_mode[0] = "send"
            oldest_file     = Q.get()

            with open(oldest_file) as f:
                data = f.read()

            t = threading.Thread(
                target=App.send_sbd_message, args=(data, oldest_file)
            )

            t.start()
            Q.update(QDIR, old)
        log.debug("Queue empty.")
        log.info("Monitor mode set to 'listen'.")
        monitor_mode[0] = ["listen"]
    else:
        log.debug("Message doesn't match config.ini string: %s" % data)

# Check to make sure the modem is connected.
print(App.status())

# Monitor serial port.
try:
    initiate_stop = threading.Event()
    monitor_mode  = ["listen"]

    t = threading.Thread(
        target=App.monitor, args=(initiate_stop, monitor_mode, _callback)
    )

    t.daemon = True
    t.start()

    print "Thread count: ", threading.active_count()
    signal.pause()
except KeyboardInterrupt:
    initiate_stop.set()
    sys.exit(1)
