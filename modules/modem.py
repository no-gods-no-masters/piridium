#!/usr/bin/env python

# Modem-related classes

# Python imports
import os
import time
import serial
import ConfigParser as cfgp

# Set up config
config = cfgp.ConfigParser()
config.read("./config.ini")

# Application imports
from parse import Parse
from logger import log

# The Modem class represents the Iridium 9602 modem within the RockBLOCK,
# and contains all functions related to the modem. It should be instantiated
# once for each RockBLOCK.

class Modem(object):

    # Initialize with simple defaults
    def __init__(self, baud=None, port=None, delay=None):
        if baud is None:
            baud = config.get("modem", "baud")

        if port is None:
            port = config.get("modem", "port")

        self.baud = baud
        self.port = port

        self.serialPort = serial.Serial(baudrate=baud, port=port)

        self.data  = ""
        self.delay = delay

        self.send_command("AT+SBDMTA=1")
        time.sleep(.25)
        self.send_command("AT+SBDAREG=1")
        time.sleep(.25)
        
    # String return of port status (for debugging)
    def status(self):
        baud   = "baud: %r \n" % self.baud
        isOpen = "isOpen: %r \n" % self.serialPort.isOpen()
        port   = "port: %r \n" % self.port
        return (baud + isOpen + port)

    # Send a command directly to the modem
    def send_command(self, message):
        command = "%s\r" % message
        self.serialPort.write(bytes(command))

    #temporary I will move this someplace good
    def string_to_hex(self, string):
        output = ''
        for char in str(string):
            output += format(ord(char), 'x')
        return output

    # Send an SBD message
    def send_sbd_message(self, message, filename):
        print "DEBUG %s" % filename
        self.filename = filename
        print "DEBUG SELF", self.filename
        if len(message) > 270:
            return False
        else:
            log.info("sending message.\nchars: %s\nmessage: %s" % (len(message), message))
            self.send_command("AT+SBDWT=%s" % message)
            time.sleep(1)
            self.send_command("AT+SBDS")

    # When we process the buffer the program either sends a command to the
    # modem or parses the buffer as a response from Iridium.
    def process_buffer(self, mode, callback):
        Parser = Parse()
        log.debug("Processing modem input buffer...")
        if "SBDRING" in self.data:
            # need a timer for second SBDRING
            log.info("SBDRING detected. Sending AT+SBDIX.")
            self.send_command("AT+SBDIX")
        else:
            log.debug("Parsing request...")
            response = Parser.request(self.data, self.delay, mode)
            if response == "AT+SBDRT":
                log.info("Response parsed. Sending command.")
                self.send_command(response)
            elif response == "AT+SBDWT":
                log.info("Message ready to send...\n")
                self.send_command("AT+SBDIX")
            elif response == "AT+SBDD0":
                log.info("Clearing output buffer")
                self.send_command(response)
                log.info("Deleting file: %s" % self.filename)
                os.remove(self.filename)
            elif response == "AT+CSQF" or response == "AT+SBDMTA=1" or response == "AT+SBDAREG=1" or response == True:
                pass
            elif response:
                if callable(callback):
                    callback(response)
                return response
            elif response == False:
                log.debug("Not an SBD exchange message.")
            else:
                print("ELSE")
                print(response)

    # The monitor function sets up a listener on the serial port to await
    # commands.
    def monitor(self, stop_event,  mode, callback):
        print 'stop', stop_event.is_set()
        log.debug("Monitoring serial port '" + self.port + "'")
        log.debug("Monitor mode: %s" % mode)
        lines = ""
        targetWordList = ["OK", "SBDRING"]
        while not stop_event.wait(0):
            line =  self.serialPort.readline()
            lines += line
            for word in targetWordList:
                if word in line:
                    self.data = lines
                    lines = ""
                    self.process_buffer(mode, callback)
