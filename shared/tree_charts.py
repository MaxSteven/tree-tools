import os

import pygal

import tree_functions

# Functions
functions = tree_functions.TreeFunctions()


class Charts(object):
    """docstring for Charts"""
    def __init__(self, logger, constants, index):
        super(Charts, self).__init__()

        self.c = constants
        unit, div = self.determine_unit(index=index)
        summary = functions.summary(index=index, constants=constants)

        if self.c['sort_by_size']:
            index = functions.sort_index_by_size(index=index)

        # Create charts
        self.bar_chart(index=index, unit=unit, div=div, summary=summary)
        self.pie_chart(index=index, unit=unit, div=div, summary=summary)

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

    def bar_chart(self, index, unit, div, summary):
        """ Create a simple bar chart
        """

        if div == 0:
            div = 1  # prevent division if zero

        chart = pygal.Bar(truncate_legend=35)
        chart.title = 'Total size: ' + summary['size']
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
        chart.render_to_file('tree_leafsize_bar_chart.svg')

    def pie_chart(self, index, unit, div, summary):
        """ Create a simple pie chart
        """
        if div == 0:
            div = 1  # prevent division if zero

        chart = pygal.Pie(truncate_legend=35)
        chart.title = 'Total size: ' + summary['size']

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
        chart.render_to_file('tree_leafsize_pie_chart.svg')
