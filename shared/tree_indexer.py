#!/usr/bin/env python

import os
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

    def traverse(self, limit):
        """ Based on indexer method, directory will be traversed and files
        will get registered for specific action.
        """
        index = {}  # json dictionary
        tool = self.c['tool']
        silent = self.c['silent']
        roots_to_skip = []

        for root, dirs, files in os.walk(unicode(self.c['src_dir'])):
            skip_root = False
            for r in roots_to_skip:
                if root.startswith(r):
                    skip_root = True

            if not skip_root:
                path = root.split('/')
                if not silent:
                    print (len(path) - 1) * '-', root

                # Use items rather than root+file,
                # in order to also parse directories
                items = sorted(files + dirs)
                for i in items:
                    filepath = os.path.join(root, i)

                    index = self.reg_check(index=index,
                                           filepath=filepath,
                                           limit=limit)

                    if filepath in index:
                        size = functions.nice_number(b=index[filepath]['b'])
                        size = '(' + size + ')'
                        if tool == 'tree_leafsize':
                            roots_to_skip.append(filepath)  # skip sub-folders
                        if not silent:
                            print len(path)*'-', i, size
                    else:
                        if not silent:
                            print len(path)*'-', i

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
