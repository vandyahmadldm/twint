import re
import time

import requests
import logging as logme


class TokenExpiryException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class RefreshTokenException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


BEARER = (
    'AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs'
    '%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
)


class Token:
    def __init__(self, config):
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'
        })
        self.config = config
        self._retries = 5
        self._timeout = 10

    def _activate_guest_token(self):
        """Ambil guest token via POST ke endpoint resmi Twitter."""
        bearer = getattr(self.config, 'Bearer_token', None) or f'Bearer {BEARER}'
        headers = {
            'Authorization': bearer,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
        }
        for attempt in range(self._retries + 1):
            try:
                r = self._session.post(
                    'https://api.twitter.com/1.1/guest/activate.json',
                    headers=headers,
                    timeout=self._timeout,
                )
                r.raise_for_status()
                guest_token = r.json().get('guest_token')
                if guest_token:
                    logme.debug(f'Got guest token via activate endpoint: {guest_token}')
                    return guest_token
            except requests.exceptions.RequestException as exc:
                logme.warning(f'activate.json attempt {attempt + 1} failed: {exc!r}')
                if attempt < self._retries:
                    time.sleep(2.0 * 2 ** attempt)
        return None

    def refresh(self):
        logme.debug('Retrieving guest token via activate endpoint')
        guest_token = self._activate_guest_token()
        if guest_token:
            self.config.Guest_token = str(guest_token)
        else:
            self.config.Guest_token = None
            raise RefreshTokenException('Could not retrieve guest token from Twitter activate endpoint')
