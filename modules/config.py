#!/usr/bin/env python

# Simple config wrapper to normalize and simplify app config.

# Python imports
import logging
import ConfigParser as cfgp

# Set up config
config = cfgp.ConfigParser()
config.read("./config.ini")


class Config(object):

    @staticmethod
    def get(section):
        dict1 = {}
        options = config.options(section)
        for option in options:
            try:
                dict1[option] = config.get(section, option)
                if dict1[option] == -1:
                    log.debug("Skip: %s" % option)
            except ValueError as e:
                print("Exception on %s!" % option)
                log.debug(e)

                dict1[option] = None
        return dict1
