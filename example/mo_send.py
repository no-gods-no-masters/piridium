#!/usr/bin/env python

# Send MO Data
#
# Allows MO (Mobile Originated) SBD (Short Burst Data) messages to be sent from
# a RockBLOCK to the RockBLOCK portal and then forwarded as necessary.
# mo_send.py uses a queuing system based on writing outgoing messages disk, and
# then sending from oldest to newest. If a message fails to send, it will be
# re-sent after a 45 second delay. This method avoids the need for a database,
# and allows for message persistence in the event of power loss.
#
# See README.md for documentation.

# Python imports
import os
import sys
import time
import uuid
import signal
import threading

# Application imports
sys.path.append("../modules")

from modem    import Modem
from optparse import OptionParser
from queue    import Queue
from logger   import log

# Globals
QDIR = "moqueue"

# Configure option parser
opt_parser = OptionParser()

opt_parser.add_option(
    "-v", "--verbose", action="store_true", dest="verbose", default=False,
    help="Print informative messages to the command line."
)

(options, args) = opt_parser.parse_args()

# Do something with the returned message!
def _callback(value):
    print(value)

# Instantiate classes
Q   = Queue(QDIR)
App = Modem()

# If there is an argument add it to the queue and start a monitoring thread
if len(args) < 1:
    sys.stderr.write(
        "Please add a message to send.\nUsage: ./reply.py <message>\n"
    )
    sys.exit(1)

else:
    Q.add(args[0])

# Monitor the queue dir if there are files send them oldest to newest.
def check_queue_dir(dir):
    while True:
        while Q.count() > 0:
            old = os.stat(dir).st_mtime
            log.info("Getting oldest file from queue...")
            oldest_file = Q.get()
            log.info("Oldest file: %s" % oldest_file)

            with open(oldest_file) as f:
                data = f.read()

            t = threading.Thread(
                target=App.send_sbd_message, args=(data, oldest_file)
            )

            t.start()
            print 'Waiting...'
            Q.update(dir, old)
        else:
            old = os.stat(dir).st_mtime
            Q.update(dir, old)

# Run the queue sending function.
# Allow ^C to exit gracefully.
try:
    initiate_stop = threading.Event()

    t = threading.Thread(
        target=App.monitor, args=(initiate_stop, ["send"], _callback)
    )

    t.daemon = True
    t.start()

    while not App.ready:
        pass

    check_queue_dir(QDIR)
    signal.pause()
except KeyboardInterrupt:
    initiate_stop.set()
    sys.exit(1)
