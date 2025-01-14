import sys
from dataclasses import dataclass, asdict
from configparser import ConfigParser

import pandas as pd

from mylib import SheetManager

#
#
#
@dataclass
class Experiment:
    sequence: int
    duration: float

#
#
#
def gather(config):
    args = map(config.get, ('sheet_id', 'api_key'))
    sheet = SheetManager(*args)
    data = sheet.get(config['sheet_tab_target'])

    columns = {
        'Question Asked Time ': 'start',
 	'Answer Shared Time': 'end',
    }

    df = (pd
          .read_csv(
              data,
              usecols=columns,
              parse_dates=list(columns),
              date_format='%I:%M:%S %p',
          )
          .rename(columns=columns))
    a_day = pd.Timedelta(1, 'day')
    for i in df.itertuples():
        end = i.end
        if end < i.start:
            end += a_day
        diff = end - i.start
        duration = diff.total_seconds()

        yield Experiment(i.Index + 1, duration)

#
#
#
if __name__ == "__main__":
    config = ConfigParser()
    config.read_file(sys.stdin)

    records = map(asdict, gather(config['GOOGLE']))
    df = pd.DataFrame.from_records(records)
    df.to_csv(sys.stdout, index=False)
