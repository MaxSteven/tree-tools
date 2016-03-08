#!/usr/bin/env python

import os
import datetime
import math


class TreeFunctions(object):
    """docstring for TreeFunctions"""
    def __init__(self):
        super(TreeFunctions, self).__init__()

    def enc(self, text):
        """ Encodes unicode text
        """
        return unicode(text).encode('utf-8').strip()

    def modification_date(self, filepath):
        """ Return last modification date for file, in datetime format
        """
        s = os.path.getmtime(filepath)  # last time of modification in seconds
        timestamp = datetime.datetime.fromtimestamp(s)  # timestamp format
        return timestamp

    def keep(self, now_timestamp, timestamp, days):
        """ If file is older than n days, return False. If file is not
        older than n days, return True.
        """
        # now_timestamp = datetime.datetime.now()
        timedelta = now_timestamp - timestamp
        if int(timedelta.days) > int(days):
            return False
        else:
            return True

    def round(self, f):
        """ Round number to two decimals
        """
        return math.ceil(f*100)/100

    def nice_number(self, b):
        """ Convert bytes into something nicer
        """
        kb = b / 1024.0
        mb = kb / 1024.0
        gb = mb / 1024.0
        tb = gb / 1024.0
        if tb > 1.0:
            size = str(self.round(f=tb)) + ' TB'
        elif gb > 1.0:
            size = str(self.round(f=gb)) + ' GB'
        elif mb > 1.0:
            size = str(self.round(f=mb)) + ' MB'
        elif kb > 1.0:
            size = str(self.round(f=kb)) + ' kb'
        else:
            size = str(self.round(f=b)) + 'bytes'

        return size
