#!/usr/bin/env python

# Modem-related classes

# Python imports
import os
import sys
import time
import serial
import threading

# Application imports
from config import Config
from parse import Parse
from logger import log


# The Modem class represents the Iridium 9602 modem within the RockBLOCK,
# and contains all functions related to the modem. It should be instantiated
# once for each RockBLOCK.
class Modem(object):

    # Initialize with simple defaults
    def __init__(self, baud=None, port=None, delay=None):
        if baud is None:
            baud = Config.get("modem")["baud"]

        if port is None:
            port = Config.get("modem")["port"]

        self.baud = baud
        self.port = port

        self.serialPort = serial.Serial(baudrate=baud, port=port)

        self.data = ""
        self.delay = delay

        self.sbdring_time = 0
        self.sbdix_time = 0
        self.retry_count = 0

        # Send two commands simultaneously
        self.send_command("AT+SBDAREG=1;+SBDMTA=1;+SBDD2")
        self.ready = False

        self.Parser = Parse()

    # String return of port status (for debugging)
    def status(self):
        baud = "baud: %r \n" % self.baud
        isOpen = "isOpen: %r \n" % self.serialPort.isOpen()
        port = "port: %r \n" % self.port
        return (baud + isOpen + port)

    # Send a command directly to the modem
    def send_command(self, message):
        command = "%s\r" % message
        self.serialPort.write(bytes(command))
        log.debug("Sent command: %s" % command)
        if command == "AT+SBDIX":
            self.retry_increment()
            log.debug("************************************")
            log.debug("************************************")
            log.debug("************************************")
    # Send an SBD message
    def send_sbd_message(self, message, filename=''):
        self.filename = filename
        if len(message) > 270:
            return False
        else:
            log.info(
                "Sending message.\nChars: %s\nMessage: %s" %
                (len(message), message)
            )
            self.send_command("AT+SBDWT=%s" % message)
            return

    # When we process the buffer the program either sends a command to the
    # modem or parses the buffer as a response from Iridium.
    def process_response(self, mode, callback):
        if self.response in {"AT+SBDIX", "AT+SBDRT", "AT+SBDS"}:
            self.send_command(self.response)

        elif self.response == "CLEAR":
            log.info("Clearing output buffer...")
            self.send_command("AT+SBDD0")
            if self.filename:
                log.info("Deleting file: %s" % self.filename)
                os.remove(self.filename)

        elif self.response in {"AT+CSQF", "AT+SBDMTA=1", "AT+SBDAREG=1",
                               "AT+SBDAREG=1;+SBDMTA=1", "AT+SBDD", "AT+SBDS",
                               "AT\nOK"}:
            log.info(self.response)
            self.ready = True


        elif self.response:
            if callable(callback):
                c = threading.Thread(target=callback, args=(self.response,))
                c.start()

        elif self.response is False:
            log.info(self.response)

        else:
            print "ELSE"
            log.info(self.response)

    # The monitor function sets up a listener on the serial port to await
    # commands.

    def retry_reset(self):
        self.retry_count = 0
        self.sbdring_time = time.time()

    def retry_increment(self):
        self.retry_count += 1

    def monitor(self, stop_event,  mode, status, callback):
        log.debug("Monitoring serial port '" + self.port + "'")
        log.debug("Monitor mode: %s" % mode)

        lines = ""
        targetWordList = ["OK", "SBDRING"]

        while True:
            line = self.serialPort.readline()
            lines += line

            for word in targetWordList:
                if word in line:
                    self.data = lines
                    lines = ""

                    if "SBDRING" in self.data:
                        #  self.retry_reset() this could be causeing problems
                        status[0] = 'busy'

                    self.response = self.Parser.request(
                        self.data, self.delay, mode
                    )

                    # if "SBDIX" in self.response:
                    #     self.retry_increment()

                    self.process_response(self.response, callback)
