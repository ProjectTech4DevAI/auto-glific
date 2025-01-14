import sys
import logging
from dataclasses import dataclass
from argparse import ArgumentParser
from configparser import ConfigParser

import requests
import pandas as pd

from gutils import SheetManager

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
                .get('access_token'))

    def run(self, token):
        query = '''
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
    @property
    def complete(self):
        return self.rows(self.config['sheet_tab_target'])

    def __init__(self, config):
        super().__init__(config)

        self.wait = self.config.getint('DEFAULT', 'poll_time')
        self.config = self.config['GOOGLE']

        args = map(self.config.get, ('sheet_id', 'api_key'))
        self.sheet = SheetManager(*args)
        self.target = self.rows(self.config['sheet_tab_source'])

    def rows(self, tab):
        df = pd.read_csv(self.sheet.get(tab))
        return len(df)

    def __iter__(self):
        wait = 0
        before = self.complete

        while before != self.target:
            after = self.complete
            if after == before:
                time.sleep(self.wait)
                wait += self.wait
            elif after > before:
                yield Status(after, wait)
                before = after
                wait = 0
            else:
                raise ValueError(f'Inconsistent increment {before} {after}')

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
        token = glific.auth(glific)
    else:
        token = args.glific_token

    google = GoogleHelper(config['GOOGLE'])
    for i in google:
        logging.warning(i)
        glific.run(token)
