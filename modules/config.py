#!/usr/bin/env python

# Simple config wrapper to normalize and simplify app config.

# Python imports
import ConfigParser

class Config(object):
    def __init__(self):
        # Set up config
        self.cfpg = ConfigParser.ConfigParser()
        self.cfpg.read("./config.ini")

    def get(self, section):
        dict1 = {}
        options = self.cfpg.options(section)
        for option in options:
            try:
                dict1[option] = self.cfpg.get(section, option)
                if dict1[option] == -1:
                    DebugPrint("Skip: %s" % option)
            except:
                print("Exception on %s!" % option)
                dict1[option] = None
        return dict1
