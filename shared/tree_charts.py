import os

import pygal

import tree_functions

# Functions
functions = tree_functions.TreeFunctions()


class Charts(object):
    """docstring for Charts"""
    def __init__(self, logger, constants, index):
        super(Charts, self).__init__()

        c = constants
        unit, div = self.determine_unit(index=index)
        summary = functions.summary(index=index, constants=constants)

        if summary['item_count'] != 0:
            if c['sort_by_size']:
                index = functions.sort_index_by_size(index=index)
            # Create charts
            self.bar_chart(constants=c,
                           index=index,
                           unit=unit,
                           div=div,
                           summary=summary)
            logger.info('Created bar chart: ' +
                        functions.enc(
                            os.path.abspath(
                                c['bar_chart_file'])))
            self.pie_chart(constants=c,
                           index=index,
                           unit=unit,
                           div=div,
                           summary=summary)
            logger.info('Created pie chart: ' +
                        functions.enc(
                            os.path.abspath(
                                c['pie_chart_file'])))

    def determine_unit(self, index):
        """ Determine proper unit for bytes
        """
        biggest_bite = 0
        for key, value in index.iteritems():
            b = value['b']
            if b > biggest_bite:
                biggest_bite = b
        size, div = functions.nice_number(biggest_bite, return_div=True)
        unit = size.split(' ')[1]
        return unit, div

    def bar_chart(self, constants, index, unit, div, summary):
        """ Create a simple bar chart
        """

        if div == 0:
            div = 1  # prevent division if zero

        c = constants
        chart_filepath = c['pie_chart_file']

        chart = pygal.Bar(truncate_legend=35)
        chart.title = self.set_title(summary=summary)

        if isinstance(index, list):
            # Index has been sorted
            for item in index:
                key = item[0]  # filepath
                value = item[1]
                name = os.path.basename(key)
                values = [value['b'] / div]
                nice_size = functions.nice_number(b=value['b'])
                chart.add(nice_size + ' ' + name, values)
        elif isinstance(index, dict):
            # Index is unsorted
            for key, value in index.iteritems():
                name = os.path.basename(key)
                values = [value['b'] / div]
                nice_size = functions.nice_number(b=value['b'])
                chart.add(nice_size + ' ' + name, values)
        chart.render_to_file(chart_filepath)

    def pie_chart(self, constants, index, unit, div, summary):
        """ Create a simple pie chart
        """
        if div == 0:
            div = 1  # prevent division if zero

        c = constants
        chart_filepath = c['pie_chart_file']

        chart = pygal.Pie(truncate_legend=35)
        chart.title = self.set_title(summary=summary)

        if isinstance(index, list):
            # Index has been sorted
            for item in index:
                key = item[0]  # filepath
                value = item[1]
                name = os.path.basename(key)
                values = [value['b'] / div]
                nice_size = functions.nice_number(b=value['b'])
                chart.add(nice_size + ' ' + name, values)
        elif isinstance(index, dict):
            # Index is unsorted
            for key, value in index.iteritems():
                name = os.path.basename(key)
                values = [value['b'] / div]
                nice_size = functions.nice_number(b=value['b'])
                chart.add(nice_size + ' ' + name, values)
        chart.render_to_file(chart_filepath)

    def set_title(self, summary):
        title = ''
        title += summary['src_dir'] + '\n'
        title += 'Total size: ' + summary['size_total'] + '\n'
        title += 'Average/mean item size: ' + summary['size_average'] + '\n'
        title += 'Trimmed mean item size: ' \
                 + summary['size_trimmedmean'] + '\n'
        title += 'Item count: ' + summary['item_count'] + '\n'

        return title
