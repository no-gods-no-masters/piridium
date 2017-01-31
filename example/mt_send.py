#!/usr/bin/env python

# Send MT Data
#
# This script allows data to be sent to a RockBLOCK via Short Burst Data (SBD)
# messages. It can be run from any web-connected computer.
#
# See README.md for documentation.

# Python imports
import re
import sys
import urllib
import urllib2
import getpass
from   optparse import OptionParser

# Application imports
sys.path.append("../modules")
from config import Config

# Option setup
opt_parser = OptionParser()
opt_parser.add_option(
    "-x", "--rockblock-select", dest="which_rb",
    help="Specify a RockBLOCK based on './config.ini'."
)

opt_parser.add_option(
    "-t", "--test", action="store_true", default=False, dest="test_mode",
    help="Test mode will not send message, and will set verbose true."
)

opt_parser.add_option(
    "-v", "--verbose", action="store_true", dest="verbose", default=False,
    help="Print informative messages to the command line."
)

(options, args) = opt_parser.parse_args()

# Helper Functions

def string_to_hex(string):
    output = ''
    for char in str(string):
        output += format(ord(char), 'x')
    return output

# Send data

# If test_mode option is on, switch to verbose error logging.
if options.test_mode:
    sys.stdout.write("Test mode.\n")
    options.verbose = True

# See send-example.ini for examples.
try:
    imei = Config.get("imei")[options.which_rb]
except:
    sys.stderr.write(
        "Use the -x flag to specify a RockBLOCK based on './config.ini'.\n"
    )
    sys.exit(1)

# If an argument is present it will be converted to hex and sent to the
# specified RockBLOCK.
if args:
    send_string = string_to_hex(args[0])
else:
    sys.stderr.write("Please add a message to send to the RockBLOCK.\n")
    sys.exit(1)

# Print debug information.
if options.verbose:
    sys.stdout.write("Output: %s\n" % args[0])
    sys.stdout.write('Hex output: %s\n' % send_string)
    sys.stdout.write('RockBLOCK name: %s\n' % options.which_rb)

# Collect the username and password from the user if not in config.
# Empty string is used for testing.
username = Config.get("post")["username"]

if not options.test_mode:
    pw = Config.get("post")["password"]
    if not pw:
        pw = getpass.getpass("Rock7 password: ")
else:
    pw = ""

# Set up user defined variables from config.ini
url  = Config.get("post")["url"]
data = urllib.urlencode({
    "imei"     : imei,
    "username" : username,
    "password" : pw,
    "data"     : send_string
})

# Prints the contents of the POST data to the command line when the verbose
# flag is selected.
if options.verbose:
    # Redacts the password from the displayed message.
    if pw:
        redacted_data = re.sub(urllib.pathname2url(pw), 'XXX', data)
    else:
        redacted_data = data
    sys.stdout.write("Data output: %s\n" % redacted_data)
    sys.stdout.write("Data bytes: %s\n" % (len(send_string)/2))

# Submits the POST to the URL.
if not options.test_mode:
    req = urllib2.Request(url, data)
    r   = urllib2.urlopen(req)
    sys.stdout.write("Return:\n%s\n" % r.read())
