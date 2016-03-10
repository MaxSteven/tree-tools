#!/usr/bin/env python

from optparse import OptionParser
import sys
import os
import datetime

from shared import tree_functions
from shared import tree_logger
from shared import tree_indexer
from shared import tree_charts


def main():
    # Option parser and constants
    TREE_LEAFSIZE = 'v1.0.0'
    DEFAULT_JSON = 'tree_leafsize_index.json'
    DEFAULT_LOG = 'tree_leafsize.log'
    DEFAULT_REGEX = '.*'
    DEFAULT_DAYS = '0'
    DEFAULT_MAX_WALK = None
    DEFAULT_PIE_CHART = 'tree_leafsize_pie_chart.svg'
    DEFAULT_BAR_CHART = 'tree_leafsize_bar_chart.svg'
    parser = OptionParser(version='%prog ' + TREE_LEAFSIZE)
    parser.add_option(
        '-s', '--source-dir', dest='sourcedir',
        default='.',
        help='Absolute path to dir to purge [default: %default]')
    parser.add_option(
        '-r', '--regex', dest='regex', default=DEFAULT_REGEX,
        help='Calculate size for leaf matching regex [default: %default]')
    parser.add_option(
        '-i', '--index', dest='index',
        default=DEFAULT_JSON,
        help='Path to JSON file [default: %default]')
    parser.add_option(
        '-l', '--log', dest='logfile',
        default=DEFAULT_LOG,
        help='Path to log file [default: %default]')
    parser.add_option(
        '-p', '--pie-chart', dest='piechart',
        default=DEFAULT_PIE_CHART,
        help='Path to pie chart SVG file [default: %default]')
    parser.add_option(
        '-b', '--bar-chart', dest='barchart',
        default=DEFAULT_BAR_CHART,
        help='Path to bar chart SVG file [default: %default]')
    parser.add_option(
        '-d', '--days', dest='days', default=DEFAULT_DAYS,
        help='Skip leaves which are DAYS days old [default: %default]')
    parser.add_option(
        '-m', '--max-walk-level', dest='maxwalklevel', default=DEFAULT_MAX_WALK,
        help='Max directory levels to traverse [default: %default]')
    parser.add_option(
        '--index-only', action='store_true', dest='indexonly', default=False,
        help='Only index directory tree and generate index.json.')
    parser.add_option(
        '--skip-indexing', action='store_true', dest='skipindexing', default=False,
        help='Skip indexing phase.')
    parser.add_option(
        '--sort-by-size', action='store_true', dest='sortbysize', default=False,
        help='Sort by size.')
    parser.add_option(
        '--silent', action='store_true', dest='silent', default=False,
        help='Do not output progress (faster).')
    (options, args) = parser.parse_args()

    # Constants
    c = {}
    c['tool'] = 'tree_leafsize'
    c['default_days'] = DEFAULT_DAYS
    c['default_regex'] = DEFAULT_REGEX
    c['src_dir'] = options.sourcedir
    c['regex'] = options.regex
    c['index_file'] = options.index
    c['log_file'] = options.logfile
    c['pie_chart_file'] = options.piechart
    c['bar_chart_file'] = options.barchart
    c['days'] = options.days
    c['max_walk_level'] = options.maxwalklevel
    c['index_only'] = options.indexonly
    c['skip_indexing'] = options.skipindexing
    c['sort_by_size'] = options.sortbysize
    c['silent'] = options.silent
    c['now_timestamp'] = datetime.datetime.now()

    # Run
    if os.path.isdir(c['src_dir']):
        LeafSize(constants=c)
    else:
        print 'The directory specified does not exist or \
                        is not accessible.'
        sys.exit(1)


class LeafSize(object):
    """docstring for Purge"""
    def __init__(self, constants):
        super(LeafSize, self).__init__()

        # Use shorter variable name
        c = constants

        # Logger
        logger = tree_logger.tree_logger(log_filepath=c['log_file'])

        # Shared functions
        functions = tree_functions.TreeFunctions()

        # Indexing
        if not c['skip_indexing']:
            tree_indexer.Index(logger=logger, constants=c)

        # Log
        logger.info('Leaf size started at ' + unicode(c['now_timestamp']))
        logger.info('Source dir: ' +
                    functions.enc(os.path.abspath(c['src_dir'])))
        logger.info('Log file: ' +
                    functions.enc(os.path.abspath(c['log_file'])))

        # Read json index
        index = functions.read_json(filepath=c['index_file'])  # load index

        # Summary
        for key, value in index.iteritems():
            size = functions.nice_number(b=value['b'])
            logger.info('Leaf: ' + functions.enc(key) + ' (' + size + ')')
        summary = functions.summary(index=index, constants=c)

        # Log
        logger.info('Leaves: ' + str(len(index)))
        logger.info('Total size: ' + summary['size_total'])
        logger.info('Average/mean item size: ' + summary['size_average'])
        logger.info('Trimmed mean item size: ' + summary['size_trimmedmean'])

        # Create charts here
        if not c['index_only']:
            tree_charts.Charts(logger=logger,
                               constants=c,
                               index=index)

        logger.info('Leaf size completed: ' + unicode(datetime.datetime.now()))

if __name__ == '__main__':
    main()
