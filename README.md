# tree-purger
Python script to purge a directory tree of files based on different criteria

```
Usage: tree_purger.py [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s SOURCEDIR, --source-dir=SOURCEDIR
                        Absolute path to dir to purge [default: .]
  -r REGEX, --regex=REGEX
                        Delete files matching regex [default: .*]
  -i INDEXFILE, --indexfile=INDEXFILE
                        Path to JSON file [default: tree_purger_index.json]
  -l LOGFILE, --log=LOGFILE
                        Path to log file [default: tree_purge.log]
  -d DAYS, --days=DAYS  Keep files which are DAYS days old [default: 0]
  --indexonly           Only index directory tree and generate index.json.
  --skipindexing        Skip indexing phase.
  --delete              Actually delete files. If not specified, script will
                        always run in "dry-run" mode.
  --delete-empty-dirs   Deletes empty directories. Requires --delete.
  --silent              Do not output progress (faster).
  ```
