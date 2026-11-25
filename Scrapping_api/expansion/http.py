"""Requisições HTTP com espera em 429 (Retry-After) e novas tentativas em erro 5xx."""

import time
from typing import Callable, Optional

import requests

USER_AGENT = "TCC-Recommendation-App/0.2 ( https://github.com/PauloOyama/Undergraduate-Final-Project )"


class HttpClient:
    def __init__(self, log: Optional[Callable[[str], None]] = None, max_retries: int = 5):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.session.headers["Accept"] = "application/json"
        self.max_retries = max_retries
        self.log = log or (lambda msg: None)
        self.calls = 0
        self.waited_seconds = 0.0

    def get(self, url: str, params=None, headers=None, timeout: int = 30) -> requests.Response:
        """GET que respeita o Retry-After do 429 e tenta de novo em 5xx e erros de rede."""
        for attempt in range(self.max_retries + 1):
            try:
                self.calls += 1
                resp = self.session.get(url, params=params, headers=headers, timeout=timeout)
            except requests.RequestException as err:
                wait = min(2 ** attempt, 30)
                self.log(f"erro de rede ({err.__class__.__name__}); nova tentativa em {wait}s")
                self._sleep(wait)
                continue
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", "5") or 5) + 1
                self.log(f"limite de requisições (429); esperando {wait}s como pede o Retry-After")
                self._sleep(wait)
                continue
            if resp.status_code >= 500 and attempt < self.max_retries:
                wait = min(2 ** attempt, 30)
                self.log(f"erro {resp.status_code} do servidor; nova tentativa em {wait}s")
                self._sleep(wait)
                continue
            return resp
        return resp

    def _sleep(self, seconds: float):
        self.waited_seconds += seconds
        time.sleep(seconds)
