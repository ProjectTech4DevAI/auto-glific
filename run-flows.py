import sys
import time
import random
from argparse import ArgumentParser
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
class Helper:
    def __init__(self, config):
        self.config = config

class GlificHelper(Helper):
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

    def run(self, token):
        response = requests.post(
            'https://api.prod.glific.com/api',
            headers={
                'Content-Type': 'application/json',
                'authorization': token,
            },
            json={
                'query': query,
                'variables': {
                    'flowId': self.config['flow_id'],
                    'contactId': self.config['contact_id'],
                    'defaultResults': '{}',
                },
            }
        )
        response.raise_for_status()

class GoogleHelper(Helper):
    _min_poll_time = 1e-2

    @property
    def complete(self):
        return self.rows(self.config['sheet_tab_target'])

    def __init__(self, config):
        super().__init__(config)

        self.max_poll_time = self.config.getint('DEFAULT', 'max_poll_time')
        self.config = self.config['GOOGLE']

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
        stime = 0
        before = self.complete

        while before != self.target:
            after = self.complete
            if after == before:
                stime += self.sleep()
            elif after > before:
                yield Status(after, stime)
                before = after
                stime = 0
            else:
                raise ValueError(f'Invalid increment: {before} -> {after}')

#
#
#
if __name__ == "__main__":
    arguments = ArgumentParser()
    arguments.add_argument('--glific-token')
    args = arguments.parse_args()

    config = ConfigParser()
    config.read_file(sys.stdin)

    glific = GlificHelper(config['GLIFIC'])
    if args.glific_token is None:
        token = glific.auth()
    else:
        token = args.glific_token

    google = GoogleHelper(config)
    for i in google:
        Logger.info(i)
        glific.run(token)
