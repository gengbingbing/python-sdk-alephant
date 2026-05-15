from __future__ import annotations

import re
from typing import Any, Dict, Optional

import httpx

DEFAULT_API_BASE_URL = "https://alephant.io/api/v1"
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")


def _validate_api_key(api_key: str) -> str:
    if not isinstance(api_key, str) or api_key.strip() == "":
        raise ValueError("api_key must be a non-empty string")
    if _CONTROL_CHAR_RE.search(api_key):
        raise ValueError("api_key must not contain control characters")
    return api_key


class AlephantAnalyticsClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_API_BASE_URL,
        http_client: Optional[httpx.Client] = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = _validate_api_key(api_key)
        self.base_url = base_url.rstrip("/")
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(timeout=timeout)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "AlephantAnalyticsClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def _get_raw(self, path: str, **params: object) -> Dict[str, Any]:
        clean_params = {key: value for key, value in params.items() if value is not None}
        response = self._client.get(
            f"{self.base_url}{path}",
            params=clean_params,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Alephant analytics response must be a JSON object")
        return data

    def _get_data(self, path: str, **params: object) -> Any:
        envelope = self._get_raw(path, **params)
        if "data" not in envelope:
            raise ValueError("Alephant analytics data response must contain a data field")
        return envelope["data"]

    def _get_data_or_raw(self, path: str, **params: object) -> Any:
        envelope = self._get_raw(path, **params)
        return envelope["data"] if "data" in envelope else envelope

    def usage_summary(self, period: str = "billing_cycle") -> Any:
        return self._get_data("/cockpit/usage-summary", period=period)

    def budget_status(self, period: Optional[str] = None) -> Any:
        return self._get_data("/cockpit/budget-status", period=period)

    def cost_by_model(self, period: str = "billing_cycle") -> Any:
        return self._get_data("/cockpit/cost-by-model", period=period)

    def daily_costs(self, period: str = "billing_cycle") -> Any:
        return self._get_data("/cockpit/daily-costs", period=period)

    def scope(self) -> Any:
        return self._get_data_or_raw("/cockpit/scope")

    def recent_requests(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return self._get_raw("/cockpit/recent-requests", limit=limit, offset=offset)

    def health(self) -> Dict[str, Any]:
        response = self._client.get(f"{self.base_url}/cockpit/health")
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Alephant analytics response must be a JSON object")
        return data
