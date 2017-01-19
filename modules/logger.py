#!/usr/bin/env python

# Custom logging setup

# Python imports
import logging

# Application imports
from config import Config

# Configure logging
log = logging.getLogger(Config.get("log")["log_name"])
log.setLevel(logging.DEBUG)

# Define handlers
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)

fh = logging.FileHandler(Config.get("log")["log_filename"])
fh.setLevel(logging.INFO)

# Apply formatting to log output
fh.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s : %(message)s"
    )
)

# Apply handlers
log.addHandler(fh)
log.addHandler(sh)
