import os
import time
import warnings
import itertools as it
import functools as ft
from pathlib import Path
from urllib.parse import ParseResult, urlunparse

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

#
#
#
class SheetLocation:
    @ft.cached_property
    def target(self):
        kwargs = { x: None for x in ParseResult._fields }
        p_result = ParseResult(**kwargs)

        return p_result._replace(
            scheme='https',
            netloc='docs.google.com',
        )

    def __init__(self, sheet_id):
        self.sheet_id = sheet_id
        self.path = Path(
            '/',
            'spreadsheets',
            'd',
            self.sheet_id,
            'export',
        )

    @ft.singledispatchmethod
    def __call__(self, doc_id):
        raise TypeError(type(doc_id))

    @__call__.register
    def _(self, doc_id: str):
        q_parts = {
            'format': 'csv',
            'gid': doc_id,
        }
        query = '&'.join(map('='.join, q_parts.items()))
        target = self.target._replace(path=str(self.path), query=query)

        return urlunparse(target)

    @__call__.register
    def _(self, doc_id: int):
        return self(str(doc_id))

#
#
#
class SheetManager:
    _backoff = 2

    def __init__(self, sheet_id, token=None):
        self.sheet_id = sheet_id

        if token is None:
            token = os.environ.get('GOOGLE_API_KEY')
        service = build(
            'sheets',
            'v4',
            developerKey=token,
            cache_discovery=False,
        )
        self.service = service.spreadsheets()
        self.locator = SheetLocation(self.sheet_id)

    def __iter__(self):
        gsheet = self()
        assert self.sheet_id == gsheet['spreadsheetId']
        yield from (x.get('properties') for x in gsheet.get('sheets'))

    def __call__(self):
        backoff = self._backoff
        for i in it.count():
            try:
                return self.service.get(spreadsheetId=self.sheet_id).execute()
            except HttpError as err:
                warnings.warn(f'[{i}]: {err} ({backoff})')
            time.sleep(backoff)
            backoff **= 2

    def get(self, sheet_tab):
        for s in self:
            if s['title'] == sheet_tab:
                return self.locator(s['sheetId'])

        raise LookupError(sheet_tab)
