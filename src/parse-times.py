import sys
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import dataclass, asdict

import pandas as pd

from mylib import SheetManager

def duration(start, end):
    def calculate(x):
        return (x[end]
                .sub(x[start])
                .apply(lambda y: y.total_seconds()))

    return calculate

if __name__ == "__main__":
    arguments = ArgumentParser()
    arguments.add_argument('--sheet-id')
    arguments.add_argument('--result-tab')
    arguments.add_argument('--google-api-key')
    arguments.add_argument('--data-file', type=Path)
    args = arguments.parse_args()

    if args.data_file:
        data = args.data_file
    else:
        sheet = SheetManager(args.sheet_id, args.google_api_key)
        data = sheet.get(args.result_tab)

    (start, middle, end) = ('start', 'middle', 'end')
    columns = {
        'Question Time': start,
        'Answer Shared Time': middle,
        'Summarized Answer Shared Time': end,
    }

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
