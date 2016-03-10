#!/usr/bin/env python

import os
import sys
import json
import re

import tree_functions

# Functions
functions = tree_functions.TreeFunctions()


class Index(object):
    """docstring for Index"""
    def __init__(self, logger, constants):
        super(Index, self).__init__()

        self.c = constants
        self.logger = logger

        # Log
        logger.info('Indexing started at ' + unicode(self.c['now_timestamp']))
        logger.info('Source dir: ' +
                    functions.enc(os.path.abspath(self.c['src_dir'])))
        logger.info('Log file: ' +
                    functions.enc(os.path.abspath(self.c['log_file'])))

        # Indexing
        index = self.indexer()  # traverse
        self.write_json(data=index)  # dump index to disk

    def indexer(self):
        """ Index the directory

        Algorithm:
        - If no limits, will delete all files
        - If limit by --days ...
        - If limit by --regex ...
        - If limit by --days AND --regex ...

        This means that algo drivers are 'DAYS' and 'REGEX' variables.

        """
        if self.c['days'] == self.c['default_days'] and \
                self.c['regex'] == self.c['default_regex']:
            # no limits, will delete all files
            index = self.traverse(limit=[])
        elif self.c['days'] != self.c['default_days'] and \
                self.c['regex'] == self.c['default_regex']:
            # limit by days
            index = self.traverse(limit=['days'])
        elif self.c['days'] == self.c['default_days'] and \
                self.c['regex'] != self.c['default_regex']:
            # limit by regex
            index = self.traverse(limit=['regex'])
        elif self.c['days'] != self.c['default_days'] and \
                self.c['regex'] != self.c['default_regex']:
            # limit by BOTH days and regex
            index = self.traverse(limit=['days', 'regex'])

        return index

    def walklevel(self, dirpath, level=None):
        dirpath = dirpath.rstrip(os.path.sep)
        assert os.path.isdir(dirpath)
        num_sep = dirpath.count(os.path.sep)
        for root, dirs, files in os.walk(dirpath):
            yield root, dirs, files
            if not isinstance(level, type(None)):
                level = int(level)
                num_sep_this = root.count(os.path.sep)
                if num_sep + int(level) <= num_sep_this:
                    del dirs[:]

    def traverse(self, limit):
        """ Based on indexer method, directory will be traversed and files
        will get registered for specific action.
        """
        index = {}  # json dictionary
        src_dir = self.c['src_dir']
        max_walk_level = self.c['max_walk_level']
        silent = self.c['silent']
        for root, dirs, files in self.walklevel(dirpath=src_dir,
                                                level=max_walk_level):
            path = root.split('/')
            if not silent:
                # print (len(path) - 1) * '-', root
                node = (len(path) - 1) * '-' + ' ' + root + '\n'
                sys.stdout.write(node)

            # Use items rather than root+file,
            # in order to also parse directories
            items = sorted(files + dirs)
            for i in items:
                filepath = os.path.join(root, i)

                if not silent:
                    node = len(path)*'-' + ' ' + i

                index = self.reg_check(index=index,
                                       filepath=filepath,
                                       limit=limit)

                if not silent:
                    # node = len(path)*'-' + ' ' + i
                    # print len(path)*'-', i
                    sys.stdout.write(node)
                    if filepath in index:
                        sys.stdout.write(' ...')
                        size = functions.nice_number(b=index[filepath]['b'])
                        size = ' ' + size + '\n'
                        sys.stdout.write(size)
                    else:
                        sys.stdout.write('\n')

        return index

    def reg_check(self, index, filepath, limit):
        """ Check if the filepath matches the criteria or not
        """
        item_registered = False

        if 'days' not in limit and 'regex' not in limit:
            index[filepath] = {}
            item_registered = True

        elif 'days' in limit and 'regex' not in limit:
            timestamp = functions.modification_date(filepath=filepath)
            keep = functions.keep(
                    now_timestamp=self.c['now_timestamp'],
                    timestamp=timestamp,
                    days=self.c['days'])
            if not keep:
                # Add filepath to index
                if filepath not in index:
                    index[filepath] = {}
                index[filepath]['t'] = unicode(timestamp)
                item_registered = True

        elif 'days' not in limit and 'regex' in limit:
            match = re.search(r''+self.c['regex']+'', filepath)
            if match:
                if filepath not in index:
                    index[filepath] = {}
                index[filepath]['r'] = 'True'
                item_registered = True

        elif 'days' in limit and 'regex' in limit:
            timestamp = functions.modification_date(filepath=filepath)
            keep = functions.keep(
                    now_timestamp=self.c['now_timestamp'],
                    timestamp=timestamp,
                    days=self.c['days'])
            if not keep:
                match = re.search(r''+self.c['regex']+'', filepath)
                if match:
                    if filepath not in index:
                        index[filepath] = {}
                    index[filepath]['r'] = 'True'
                    item_registered = True

        if item_registered:
            index = self.add_sizedata(index=index, filepath=filepath)

        return index

    def add_sizedata(self, index, filepath):
        """ Add size (in bytes) to the filepath
        """
        if self.c['tool'] == 'tree_purger':
            b = self.file_size(filepath=filepath)
            index[filepath]['b'] = b
        elif self.c['tool'] == 'tree_leafsize':
            if os.path.isdir(filepath):
                b = self.folder_tree_size(filepath=filepath)
            else:
                b = self.file_size(filepath=filepath)
            index[filepath]['b'] = b

        return index

    def file_size(self, filepath):
        # File size in bytes
        try:
            b = os.stat(filepath).st_size
        except:
            self.logger.error('Could not get size for ' + filepath)
        return b

    def folder_tree_size(self, filepath):
        # Folder tree size in bytes
        b = self.file_size(filepath)
        for root, dirs, files in os.walk(filepath):
            items = dirs + files
            for i in items:
                fp = os.path.join(root, i)
                try:
                    b += os.stat(fp).st_size
                except:
                    self.logger.error('Could not get size for ' + fp)
        return b

    def write_json(self, data):
        with open(self.c['index_file'], 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4,
                      separators=(',', ': '))
