#!/usr/bin/env python

import os
import datetime
import math
import json
import operator


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

    def nice_number_old(self, b):
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
            size = str(self.round(f=b)) + ' bytes'
        return size

    def nice_number(self, b, return_div=False):
        div = 0
        for unit in ['bytes', 'Kb', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
            if abs(b) < 1024.0:
                size = str(self.round(f=b)) + ' ' + unit
                if return_div:
                    return size, div
                else:
                    return size
            b /= 1024.0
            div += 1024.0

    def summary(self, index, constants):
        """ Create summary and return
        """
        summary = {}

        # Source dir
        src_dir = constants['src_dir']
        summary['src_dir'] = os.path.realpath(src_dir)

        # Number of items
        item_count = len(index)
        summary['item_count'] = str(item_count)

        if item_count != 0:
            # Collect sizes and store in variables
            b_sum = 0
            b_list = []
            for filepath, ddata in index.iteritems():
                b_sum += ddata['b']  # bytes summed
                b_list.append(ddata['b'])  # bytes in list
            b_list_ordered = sorted(b_list)  # bytes in ordered list

            # Total size
            summary['size_total'] = self.nice_number(b=b_sum)

            # Average size
            b_average = int(float(b_sum) / float(item_count))
            summary['size_average'] = self.nice_number(b=b_average)

            # Trimmed mean, remove 5% extremes
            p = int(len(b_list_ordered) * 0.05) + 1
            if not p >= (len(b_list_ordered)/2):
                b_list_ordered = b_list_ordered[p:-p]
            b_trimmed_mean = sum(b_list_ordered)/len(b_list_ordered)
            summary['size_trimmedmean'] = self.nice_number(b=b_trimmed_mean)

        else:
            summary['size_total'] = str(0)
            summary['size_average'] = str(0)
            summary['size_trimmedmean'] = str(0)

        return summary

    def read_json(self, filepath):
        with open(filepath, 'r') as infile:
            index = json.load(infile)
        return index

    def sort_index_by_size(self, index):
        sorted_index = sorted(index.items(),
                              key=operator.itemgetter(1),
                              reverse=True)
        return sorted_index

    def delete_empty_dir(self, dirpath, constants, logger):
        """ Deletes directory of file, if the directory is empty.
        """
        c = constants
        if os.path.exists(dirpath):
            files_in_dir = sorted(os.listdir(dirpath))
            if len(files_in_dir) == 0:
                if c['delete'] and c['delete_empty_dirs']:
                    try:
                        os.remove(dirpath)
                        logger.info('Deleted: ' + self.enc(dirpath))
                    except:
                        logger.error('Could not delete: ' +
                                     self.enc(dirpath))
        else:
            logger.error('Does not exist: ' + self.enc(dirpath))

    def delete_file(self, filepath, constants, logger):
        """ Delete the file given.
        """
        c = constants
        if os.path.exists(filepath):
            if not c['delete']:
                logger.info('Deleting (dry-run): ' + self.enc(filepath))
            else:
                try:
                    os.remove(filepath)
                    logger.info('Deleting: ' + self.enc(filepath))
                except:
                    logger.error('Coult not delete: ' +
                                 self.enc(filepath))
        else:
            logger.error('Does not exist: ' + self.enc(filepath))

        if c['delete_empty_dirs']:
            dirpath = os.path.dirname(filepath)
            self.delete_empty_dir(dirpath=dirpath)
