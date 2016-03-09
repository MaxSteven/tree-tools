#!/usr/bin/env python

from optparse import OptionParser
import sys
import os
import datetime

from shared import tree_functions
from shared import tree_logger
from shared import tree_indexer

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
    '--index-only', action='store_true', dest='indexonly', default=False,
    help='Only index directory tree and generate index.json.')
parser.add_option(
    '--skip-indexing', action='store_true', dest='skipindexing', default=False,
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
c = {}
c['tool'] = 'tree_purger'
c['default_days'] = DEFAULT_DAYS
c['default_regex'] = DEFAULT_REGEX
c['src_dir'] = options.sourcedir
c['regex'] = options.regex
c['index_file'] = options.index
c['log_file'] = options.logfile
c['days'] = options.days
c['index_only'] = options.indexonly
c['skip_indexing'] = options.skipindexing
c['delete'] = options.delete
c['delete_empty_dirs'] = options.deleteemptydirs
c['silent'] = options.silent
c['now_timestamp'] = datetime.datetime.now()

# Logger
logger = tree_logger.tree_logger(purge_log=c['log_file'])

# Shared functions
functions = tree_functions.TreeFunctions()


class Purge(object):
    """docstring for Purge"""
    def __init__(self):
        super(Purge, self).__init__()

        # Indexing
        if not c['skip_indexing']:
            tree_indexer.Index(logger=logger, constants=c)

        # Log
        logger.info('Purge started at ' + unicode(c['now_timestamp']))
        logger.info('Source dir: ' +
                    functions.enc(os.path.abspath(c['src_dir'])))
        logger.info('Log file: ' +
                    functions.enc(os.path.abspath(c['log_file'])))

        # Read json index
        index = functions.read_json(filepath=c['index_file'])  # load index

        # Delete files
        if not c['index_only']:
            for filepath, ddata in index.iteritems():
                self.delete_file(filepath=filepath)

        # Summary
        summary = functions.summary(index=index, constants=c)

        # Log
        logger.info('Files: ' + str(len(index)))
        logger.info('Total size: ' + summary['size'])
        logger.info('Purge completed: ' + unicode(datetime.datetime.now()))

    def delete_empty_dir(self, dirpath):
        """ Deletes directory of file, if the directory is empty.
        """
        if os.path.exists(dirpath):
            files_in_dir = os.listdir(dirpath)
            if len(files_in_dir) == 0:
                if c['delete'] and c['delete_empty_dirs']:
                    try:
                        os.remove(dirpath)
                        logger.info('Deleted: ' + functions.enc(dirpath))
                    except:
                        logger.error('Could not delete: ' +
                                     functions.enc(dirpath))
        else:
            logger.error('Does not exist: ' + functions.enc(dirpath))

    def delete_file(self, filepath):
        """ Delete the file given.
        """
        if os.path.exists(filepath):
            if not c['delete']:
                logger.info('Deleting (dry-run): ' + functions.enc(filepath))
            else:
                try:
                    os.remove(filepath)
                    logger.info('Deleting: ' + functions.enc(filepath))
                except:
                    logger.error('Coult not delete: ' +
                                 functions.enc(filepath))
        else:
            logger.error('Does not exist: ' + functions.enc(filepath))

        if c['delete_empty_dirs']:
            dirpath = os.path.dirname(filepath)
            self.delete_empty_dir(dirpath=dirpath)


if __name__ == '__main__':

    # Set contants
    if os.path.isdir(c['src_dir']):
        p = Purge()
    else:
        logger.error('The directory specified does not exist or \
                        is not accessible.')
        sys.exit(1)
