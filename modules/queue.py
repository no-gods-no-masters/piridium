#!/usr/bin/env python

# Pything imports
import os
import uuid
import time
import threading

# Application imports
from logger import log


# The Queue class uses a simple file handler to read and write messages from
# a disk-based queue for sending.
class Queue(object):
    def __init__(self, qdir):
        self.qdir = qdir

        log.debug("self.qdir: %s" % self.qdir)

        if not os.path.isdir(self.qdir):
            os.mkdir(self.qdir)

    # Add message into the queue by creating a file with a UUID
    def add(self, message):
        if len(message) > 270:
            log.info("Failed... SBD message must be less than 270 bytes.\n")

        # TO DO: Add error handling

        uid = uuid.uuid4()
        file_path = os.path.join(self.qdir, str(uid))
        with open(file_path, 'w') as f:
            f.write(message + "\n")

    # Return the number of files currently in queue.
    def count(self):
        num = len(os.listdir(self.qdir))
        return num

    # Get oldest file in queue.
    def get(self):
        dict = {}

        # Create a dict with mtime key value set to path.
        for f in os.listdir(self.qdir):
            p = os.path.join(self.qdir, f)
            dict[os.stat(p).st_mtime] = p

        time_list = dict.keys()
        time_list.sort()

        oldest_file = dict[time_list[0]]
        return oldest_file

    # If there are no changes to the directory (monitor_dir) being monitored
    # 'wait'.
    def update(self, monitor_dir, old_time):
        while os.stat(monitor_dir).st_mtime == old_time:
            time.sleep(1)
            pass
        return

    def nuke(self):
        for file in os.listdir(self.qdir):
            os.remove(os.path.join(self.qdir, file))
        return
    
