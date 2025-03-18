import sys
import functools as ft
import collections as cl
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import dataclass

import pandas as pd

from mylib import SheetManager

#
#
#
class DataReader:
    _experiment = 'experiment'

    def __init__(self, tabs, columns):
        self.tabs = tabs
        self.columns = columns

    def __call__(self):
        for t in self.tabs:
            yield (pd
                   .read_csv(self.gather(t),
                             usecols=self.columns,
                             parse_dates=self.columns)
                   .assign(**{self._experiment: t}))

    def gather(self, tab):
        raise NotImplementedError()

class LocalDataReader(DataReader):
    def __init__(self, tabs, columns, path):
        super().__init__(tabs, columns)
        self.path = path

    def	gather(self, tab):
        return self.path

class RemoteDataReader(DataReader):
    def	__init__(self, tabs, columns, sheet, key=None):
        super().__init__(tabs, columns)
        self.sheet = SheetManager(sheet, key)

    def gather(self, tab):
        return self.sheet.get(tab)

#
#
#
@dataclass
class DurationCalculator:
    start: str
    end: str

    def __call__(self, x):
        return (x[self.end]
                .sub(x[self.start])
                .apply(lambda y: y.total_seconds()))

#
#
#
if __name__ == "__main__":
    arguments = ArgumentParser()
    arguments.add_argument('--sheet-id')
    arguments.add_argument('--result-tab', action='append')
    arguments.add_argument('--google-api-key')
    arguments.add_argument('--data-file', type=Path)
    args = arguments.parse_args()

    # setup

    tabs = []

    (start, middle, end) = ('start', 'middle', 'end')
    columns = {
        'Question Time': start,
        'Answer Shared Time': middle,
        'Summarized Answer Shared Time': end,
    }

    (full, summary) = ('full', 'summary')
    timings = cl.OrderedDict([
        (full, DurationCalculator(start, middle)),
        (summary, DurationCalculator(middle, end)),
        ('total', lambda x: x[full].add(x[summary])),
    ])

    # read
    if args.data_file:
        MyReader = ft.partial(LocalDataReader, path=args.data_file)
    else:
        MyReader = ft.partial(RemoteDataReader,
                              sheet=args.sheet_id,
                              key=args.google_api_key)
    if args.result_tab is None:
        tabs.append(pd.NA)
    else:
        tabs.extend(args.result_tab)
    reader = MyReader(tabs=tabs, columns=list(columns))

    # process
    df = (pd
          .concat(reader())
          .rename(columns=columns)
          .assign(**timings)
          .melt(id_vars=reader._experiment,
                value_vars=list(timings),
                var_name='response',
                value_name='seconds'))
    df.to_csv(sys.stdout, index=False)
