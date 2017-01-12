#!/usr/bin/env python

# Send a command to the modem via CLI.
#
# Usage:
# send_command [COMMAND]
#
# If no [COMMAND] is specified, "AT" will be sent.

# Python imports
import ConfigParser as cfgp
import serial
import sys

# Config setup
config = cfgp.ConfigParser()
config.read("./config.ini")

if len(sys.argv) > 1:
    command = (sys.argv[1])
else:
    command = "AT"

s = serial.Serial(
    config.get("modem", "port"),
    config.get("modem", "baud")
)

print("Sending %s..." % command)
s.write("%s\r" % command)
print("Sent.")

s.close
