import sys
from dataclasses import dataclass, asdict
from configparser import ConfigParser

import pandas as pd

from mylib import SheetManager

def duration(start, end):
    def calculate(x):
        return (x[end]
                .sub(x[start])
                .apply(lambda y: y.total_seconds()))

    return calculate

if __name__ == "__main__":
    config = ConfigParser()
    config.read_file(sys.stdin)

    google = config['GOOGLE']
    args = map(google.get, ('sheet_id', 'api_key'))
    sheet = SheetManager(*args)

    (start, middle, end) = ('start', 'middle', 'end')
    columns = {
        'Question Time': start,
        'Answer Shared Time': middle,
        'Summarized Answer Shared Time': end,
    }

    data = sheet.get(google['sheet_tab_target'])
    df = (pd
          .read_csv(
              data,
              usecols=columns,
              parse_dates=list(columns),
          )
          .rename(columns=columns)
          .assign(
              full=duration(start, middle),
              summary=duration(middle, end),
              total=lambda x: x['full'].add(x['summary']),
          )
          .drop(columns=[start, middle, end])
          .melt(var_name='response', value_name='seconds'))
    df.to_csv(sys.stdout, index=False)
