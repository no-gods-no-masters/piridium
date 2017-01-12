#!/usr/bin/env python

import os
import uuid
import time
from logger import log


class Queue(object):
    def __init__(self, qdir):
        self.QDIR = qdir
        print "qdir", self.QDIR

        if not os.path.isdir(self.QDIR):
            os.mkdir(self.QDIR)

    # Add message into the queue by creating a file with a UUID
    def add(self, message):
        if len(message) > 270:
            log.info("Failure... sbd message must be less than 270 bytes\n")
            # need error handling 
        uid = uuid.uuid4()
        file_path = os.path.join(self.QDIR, str(uid))
        with open(file_path, 'w') as f:
            f.write(message + "\n")

    # return the number of files currently in queue
    def count(self):
        num = len(os.listdir(self.QDIR))
        return num

    # get oldest file in queue
    def get(self):
        dict = {}
    
        #make a dict of with mtime keys value set to path
        for f in os.listdir(self.QDIR):
            p = os.path.join(self.QDIR, f)
            dict[os.stat(p).st_mtime] = p

        time_list = dict.keys()
        time_list.sort()

        oldest_file = dict[time_list[0]]
        return oldest_file

                
