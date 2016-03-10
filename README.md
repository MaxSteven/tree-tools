# tree-tools

## tree_purger
Python script to purge a directory tree of files based on different criteria.

```
Usage: tree_leafsize.py [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s SOURCEDIR, --source-dir=SOURCEDIR
                        Absolute path to dir to purge [default: .]
  -r REGEX, --regex=REGEX
                        Calculate size for leaf matching regex [default: .*]
  -i INDEX, --index=INDEX
                        Path to JSON file [default: tree_leafsize_index.json]
  -l LOGFILE, --log=LOGFILE
                        Path to log file [default: tree_leafsize.log]
  -p PIECHART, --pie-chart=PIECHART
                        Path to pie chart SVG file [default:
                        tree_leafsize_pie_chart.svg]
  -b BARCHART, --bar-chart=BARCHART
                        Path to bar chart SVG file [default:
                        tree_leafsize_bar_chart.svg]
  -d DAYS, --days=DAYS  Skip leaves which are DAYS days old [default: 0]
  -m MAXWALKLEVEL, --max-walk-level=MAXWALKLEVEL
                        Max directory levels to traverse [default: none]
  --index-only          Only index directory tree and generate index.json.
  --skip-indexing       Skip indexing phase.
  --sort-by-size        Sort by size.
  --silent              Do not output progress (faster).
  ```

## tree_leafsize
Python script to analyze a directory tree of files and create charts based on different criteria.

#### Prerequisites

Charts are made using [Pygal](http://www.pygal.org). Install with `pip install pygal`.

```
Usage: tree_leafsize.py [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s SOURCEDIR, --source-dir=SOURCEDIR
                        Absolute path to dir to purge [default: .]
  -r REGEX, --regex=REGEX
                        Calculate size for leaf matching regex [default: .*]
  -i INDEX, --index=INDEX
                        Path to JSON file [default: tree_leafsize_index.json]
  -l LOGFILE, --log=LOGFILE
                        Path to log file [default: tree_leafsize.log]
  -d DAYS, --days=DAYS  Skip leaves which are DAYS days old [default: 0]
  -m MAXWALKLEVEL, --max-walk-level=MAXWALKLEVEL
                        Max directory levels to traverse [default: none]
  --index-only          Only index directory tree and generate index.json.
  --skip-indexing       Skip indexing phase.
  --sort-by-size        Sort by size.
  --silent              Do not output progress (faster).
```
