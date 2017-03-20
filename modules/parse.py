#!/usr/bin/env python

# The parser module handles everything related to incoming data, and generates
# valid responses or stores the message contents.

# Python module imports
import re
import sys
import time
import threading

# Application imports
from logger import log
from config import Config
import modem


class Parse(object):
    def __init__(self):
        self.mtqueue = 0
        self.holding_mt = 0

        self.retry = int(Config.get("modem")["retry"])

    # Public methods
    def read_mtqueue_count(self):
        return self.mtqueue

    def read_holding_mt(self):
        return self.holding_mt

    # Parse an incoming request
    def request(self, data, delay, mode):
        # print "PARSING\n---v\n%s\n^---" % data
        if "SBDRING" in data:
            log.info("SBDRING detected. Sending AT+SBDIX.")
            return "AT+SBDIX"
        elif "SBDIX:" in data:
            out = self._sbdix(data, mode)
            return out
        elif "CSQF:" in data:
            out = self._csqf(data)
            return out
        elif "SBDRT" in data:
            out = self._sbdrt(data)
            return out
        elif "SBDD" in data:
            out = self._sbdd(data)
            return out
        elif "SBDWT" in data:
            return "AT+SBDS"
        elif "SBDS:" in data:
            out = self._sbds(data)
            return out
        elif "AT+SBDAREG=1;+SBDMTA=1" in data:
            return "AT+SBDAREG=1;+SBDMTA=1"
        elif "MSSTM" in data:
            out = self._msstm(data)
            return out
        else:
            return data

    # Private methods

    # Request handler: CSQF
    @staticmethod
    def _csqf(data):
        log.info("Received: %s" % data.split("CSQF:")[1][0])
        return "AT+CSQF"

    # Request handler: SBDD
    @staticmethod
    def _sbdd(data):
        return "AT+SBDD"

    # Wait 20 seconds and try again
    def _try_again(self):
        time.sleep(self.retry)
        return

    # Request handler: SBDIX
    def _sbdix(self, data, mode):
        d = re.search(".+SBDIX\: (.+)", data)
        if d:
            log.debug("SBDIX values - %s" % d.group(1))

            if len(d.group(1).split(",")) > 1:
                status = {}
                status["mostatus"] = int(d.group(1).split(",")[0])
                status["momsn"] = int(d.group(1).split(",")[1])
                status["mtstatus"] = int(d.group(1).split(",")[2])
                status["mtmsn"] = int(d.group(1).split(",")[3])
                status["mtlength"] = int(d.group(1).split(",")[4])
                status["mtqueued"] = int(d.group(1).split(",")[5])

                # for key in status.keys():
                #     log.debug("%s - %s" % (key, status[key]))

                if mode[0] == "listen":
                    log.debug("***** Listen mode.")
                    if status["mtstatus"] == 1:
                        self.mtqueue = status["mtqueued"]
                        return "AT+SBDRT"
                    elif status["mtstatus"] == 2:
                        log.info(
                            "Message failure, retrying in %s seconds...\n\
sbdix: %s" % (self.retry, status)
                        )
                        self._try_again()
                        return "AT+SBDIX"
                    else:
                        log.warn(
                            "No message available on server"
                        )
                        return "AT\nOK"

                elif mode[0] == "send":
                    log.debug("***** Send mode.")
                    if status["mostatus"] < 4:
                        log.debug("MO message sent.")
                        self.mtqueue = status["mtqueued"]
                        if status["mtstatus"] == 1:
                            self.holding_mt = True
                        else:
                            self.holding_mt = False
                        return "CLEAR"
                    else:
                        log.info(
                            "Message failed to send retrying in %s seconds..."
                            % self.retry
                        )
                        self._try_again()
                        return "AT+SBDIX"
                else:
                    log.debug("wtf mode")
            else:
                log.warn("Failed to split incoming message.")
                # return False

    # Request handler: SBDRT
    @staticmethod
    def _sbdrt(data):
        # Split to separate the message data from the cruft that comes with it
        message_parsed = data.split("SBDRT:")[1][2:-6]

        log.debug("Raw message: %s" % data)
        log.debug("Parsed message: %s" % message_parsed)
        return message_parsed

    # Request handler: SBDS
    @staticmethod
    def _sbds(data):
        d = re.search(".+SBDS\: (.+)", data)
        if d:
            log.debug("SBDS values - %s" % d.group(1))
            status = {}
            status["mostatus"] = int(d.group(1).split(",")[0])
            status["momsn"] = int(d.group(1).split(",")[1])
            status["mtstatus"] = int(d.group(1).split(",")[2])
            status["mtmsn"] = int(d.group(1).split(",")[3])

            for key in status.keys():
                log.debug("%s - %s" % (key, status[key]))

        if status["mostatus"] > 0:
            return "AT+SBDIX"
        return

    @staticmethod
    def _msstm(data):
        d = re.search("(MSSTM\: .+)", data)
        if d:
            return d.group(1)

    #Request handler: SBDWT
