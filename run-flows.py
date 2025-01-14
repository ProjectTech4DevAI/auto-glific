import sys
import time
import math
import random
from dataclasses import dataclass
from configparser import ConfigParser

import requests
import pandas as pd

from mylib import Logger, SheetManager

#
#
#
@dataclass
class Status:
    items: int
    duration: float

#
#
#
class GlificFlowCaller:
    _attempts = 3
    _query = '''
mutation startContactFlow($flowId: ID!, $contactId: ID! $defaultResults: Json!) {
  startContactFlow(flowId: $flowId, contactId: $contactId, defaultResults: $defaultResults) {
    success
    errors {
        key
        message
    }
  }
}
'''

    def __init__(self, config):
        self.config = config
        self.token = None

        self.variables = {
            'defaultResults': '{}',
        }
        iterable = zip(('flowId', 'contactId'), ('flow_id', 'contact_id'))
        self.variables.update((x, self.config[y]) for (x, y) in iterable)

    def __call__(self):
        if self.token is None:
            self.token = self.auth()

        for _ in range(self._attempts):
            response = requests.post(
                'https://api.prod.glific.com/api',
                headers={
                    'Content-Type': 'application/json',
                    'authorization': self.token,
                },
                json={
                    'query': self._query,
                    'variables': self.variables,
                },
            )
            try:
                response.raise_for_status()
                break
            except requests.HTTPError:
                if response.status_code == 401:
                    self.token = self.auth()
        else:
            raise ConnectionError()

    def auth(self):
        user = { x: self.config[x] for x in ('phone', 'password') }

        response = requests.post(
            'https://api.prod.glific.com/api/v1/session',
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            json={
                'user': user,
            },
        )
        response.raise_for_status()

        return (response
                .json()
                .get('data')
                .get('access_token'))

class GoogleSheetsIterator:
    _min_poll_time = 1e-2

    @property
    def complete(self):
        return self.rows(self.config['sheet_tab_target'])

    def __init__(self, config):
        self.max_poll_time = config.getint('DEFAULT', 'max_poll_time')
        self.config = config['GOOGLE']

        args = map(self.config.get, ('sheet_id', 'api_key'))
        self.sheet = SheetManager(*args)
        self.target = self.rows(self.config['sheet_tab_source'])

    def rows(self, tab):
        df = pd.read_csv(self.sheet.get(tab))
        return len(df)

    def sleep(self):
        tm = random.uniform(self._min_poll_time, self.max_poll_time)
        time.sleep(tm)
        return tm

    def __iter__(self):
        stime = math.nan
        before = self.complete

        while before != self.target:
            after = self.complete
            if after > before or math.isnan(stime):
                yield Status(after, stime)
                before = after
                stime = 0
            elif after == before:
                stime += self.sleep()
            else:
                raise ValueError(f'Invalid increment: {before} -> {after}')

#
#
#
if __name__ == "__main__":
    config = ConfigParser()
    config.read_file(sys.stdin)

    glific = GlificFlowCaller(config['GLIFIC'])
    google = GoogleSheetsIterator(config)

    for g in google:
        Logger.info(g)
        glific()
