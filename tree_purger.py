#!/usr/bin/env python

from optparse import OptionParser
import logging
import sys
import os
import datetime
import json
import re
import math

# Option parser and constants
TREE_PURGER = 'v1.0.0'
DEFAULT_JSON = 'tree_purger_index.json'
DEFAULT_LOG = 'tree_purger.log'
DEFAULT_REGEX = '.*'
DEFAULT_DAYS = '0'
parser = OptionParser(version='%prog ' + TREE_PURGER)
parser.add_option(
    '-s', '--source-dir', dest='sourcedir',
    default='.',
    help='Absolute path to dir to purge [default: %default]')
parser.add_option(
    '-r', '--regex', dest='regex', default=DEFAULT_REGEX,
    help='Delete files matching regex [default: %default]')
parser.add_option(
    '-i', '--index', dest='index',
    default=DEFAULT_JSON,
    help='Path to JSON file [default: %default]')
parser.add_option(
    '-l', '--log', dest='logfile',
    default=DEFAULT_LOG,
    help='Path to log file [default: %default]')
parser.add_option(
    '-d', '--days', dest='days', default=DEFAULT_DAYS,
    help='Keep files which are DAYS days old [default: %default]')
parser.add_option(
    '--indexonly', action='store_true', dest='indexonly', default=False,
    help='Only index directory tree and generate index.json.')
parser.add_option(
    '--skipindexing', action='store_true', dest='skipindexing', default=False,
    help='Skip indexing phase.')
parser.add_option(
    '--delete', action='store_true', dest='delete', default=False,
    help='Actually delete files. If not specified, \
script will always run in "dry-run" mode.')
parser.add_option(
    '--delete-empty-dirs', action='store_true', dest='deleteemptydirs',
    default=False, help='Deletes empty directories. Requires --delete.')
parser.add_option(
    '--silent', action='store_true', dest='silent', default=False,
    help='Do not output progress (faster).')
(options, args) = parser.parse_args()

# Constants
SOURCE_DIR = options.sourcedir
REGEX = options.regex
INDEX_FILE = options.index
PURGE_LOG = options.logfile
DAYS = options.days
INDEX_ONLY = options.indexonly
SKIP_INDEXING = options.skipindexing
DELETE = options.delete
DELETE_EMPTY_DIRS = options.deleteemptydirs
SILENT = options.silent
NOW_TIMESTAMP = datetime.datetime.now()

# Logging
logger = logging.getLogger('TreePurgerLogger')
hdlr = logging.FileHandler(PURGE_LOG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

# Logging to stdout
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


class Purge(object):
    """docstring for Purge"""
    def __init__(self):
        super(Purge, self).__init__()

        # Log
        logger.info('Purge started at ' + unicode(NOW_TIMESTAMP))
        logger.info('Source dir: ' + self.enc(os.path.abspath(SOURCE_DIR)))
        logger.info('Log file: ' + self.enc(os.path.abspath(PURGE_LOG)))

        # Indexing
        if not SKIP_INDEXING:
            index = self.indexer()  # traverse
            self.write_json(data=index)  # dump index to disk

        # Delete files
        if not INDEX_ONLY:
            index = self.read_json(filepath=INDEX_FILE)  # load index
            for filepath, ddata in index.iteritems():
                self.delete_file(filepath=filepath)

        # Summary
        summary = self.summary(index=index)

        # Log
        logger.info('Files: ' + str(len(index)))
        logger.info('Total size: ' + summary['size'])
        logger.info('Purge completed: ' + unicode(datetime.datetime.now()))

    def round(self, f):
        """ Round number to two decimals
        """
        return math.ceil(f*100)/100

    def enc(self, text):
        """ Encodes unicode text
        """
        return unicode(text).encode('utf-8').strip()

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

    def summary(self, index):
        """ Create summary and return
        """
        summary = {}

        b = 0
        for filepath, ddata in index.iteritems():
            b += ddata['b']  # bytes
        size = self.nice_number(b=b)

        summary['size'] = size

        return summary

    def delete_empty_dir(self, dirpath):
        """ Deletes directory of file, if the directory is empty.
        """
        if os.path.exists(dirpath):
            files_in_dir = os.listdir(dirpath)
            if len(files_in_dir) == 0:
                if DELETE and DELETE_EMPTY_DIRS:
                    try:
                        os.remove(dirpath)
                        logger.info('Deleted: ' + self.enc(dirpath))
                    except:
                        logger.error('Could not delete: ' + self.enc(dirpath))
        else:
            logger.error('Does not exist: ' + self.enc(dirpath))

    def delete_file(self, filepath):
        """ Delete the file given.
        """
        if os.path.exists(filepath):
            if not DELETE:
                logger.info('Deleting (dry-run): ' + self.enc(filepath))
            else:
                try:
                    os.remove(filepath)
                    logger.info('Deleting: ' + self.enc(filepath))
                except:
                    logger.error('Coult not delete: ' + self.enc(filepath))
        else:
            logger.error('Does not exist: ' + self.enc(filepath))

        if DELETE_EMPTY_DIRS:
            dirpath = os.path.dirname(filepath)
            self.delete_empty_dir(dirpath=dirpath)

    def write_json(self, data):
        with open(INDEX_FILE, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4,
                      separators=(',', ': '))

    def read_json(self, filepath):
        with open(INDEX_FILE, 'r') as infile:
            index = json.load(infile)
        return index

    def traverse(self, limit):
        """ Based on indexer method, directory will be traversed and files
        will get registered to get deleted.
        """
        index = {}  # json dictionary
        for root, dirs, files in os.walk(unicode(SOURCE_DIR)):
            path = root.split('/')
            if not SILENT:
                print (len(path) - 1) * '-', os.path.basename(root)
            for file in files:
                file_registered = False
                filepath = os.path.join(root, file)

                if 'days' not in limit and 'regex' not in limit:
                    index[filepath] = {}
                    file_registered = True

                elif 'days' in limit and 'regex' not in limit:
                    timestamp = self.modification_date(filepath=filepath)
                    keep = self.keep(timestamp=timestamp)
                    if not keep:
                        # Add filepath to index
                        if filepath not in index:
                            index[filepath] = {}
                        index[filepath]['t'] = unicode(timestamp)
                        file_registered = True

                elif 'days' not in limit and 'regex' in limit:
                    match = re.search(r''+REGEX+'', filepath)
                    if match:
                        if filepath not in index:
                            index[filepath] = {}
                        index[filepath]['r'] = 'True'
                        file_registered = True

                elif 'days' in limit and 'regex' in limit:
                    timestamp = self.modification_date(filepath=filepath)
                    keep = self.keep(timestamp=timestamp)
                    if not keep:
                        match = re.search(r''+REGEX+'', filepath)
                        if match:
                            if filepath not in index:
                                index[filepath] = {}
                            index[filepath]['r'] = 'True'
                            file_registered = True

                if file_registered:
                    # File size in bytes
                    b = os.stat(filepath).st_size
                    index[filepath]['b'] = b
                    size = self.nice_number(b=b)

                    if not SILENT:
                        print len(path)*'-', file, '('+size+')'

        return index

    def indexer(self):
        """ Index the directory

        Algorithm:
        - If no limits, will delete all files
        - If limit by --days ...
        - If limit by --regex ...
        - If limit by --days AND --regex ...

        This means that algo drivers are 'DAYS' and 'REGEX' variables.

        """
        if DAYS == DEFAULT_DAYS and REGEX == DEFAULT_REGEX:
            # no limits, will delete all files
            index = self.traverse(limit=[])
        elif DAYS != DEFAULT_DAYS and REGEX == DEFAULT_REGEX:
            # limit by days
            index = self.traverse(limit=['days'])
        elif DAYS == DEFAULT_DAYS and REGEX != DEFAULT_REGEX:
            # limit by regex
            index = self.traverse(limit=['regex'])
        elif DAYS != DEFAULT_DAYS and REGEX != DEFAULT_REGEX:
            # limit by BOTH days and regex
            index = self.traverse(limit=['days', 'regex'])

        return index

    def modification_date(self, filepath):
        """ Return last modification date for file, in datetime format
        """
        s = os.path.getmtime(filepath)  # last time of modification in seconds
        timestamp = datetime.datetime.fromtimestamp(s)  # timestamp format
        return timestamp

    def keep(self, timestamp):
        """ If file is older than n days, return False. If file is not
        older than n days, return True.
        """
        # now_timestamp = datetime.datetime.now()
        timedelta = NOW_TIMESTAMP - timestamp
        if int(timedelta.days) > int(DAYS):
            return False
        else:
            return True


if __name__ == '__main__':

    # Set contants
    if os.path.isdir(SOURCE_DIR):
        p = Purge()
    else:
        logger.error('The directory specified does not exist or \
                        is not accessible.')
        sys.exit(1)
