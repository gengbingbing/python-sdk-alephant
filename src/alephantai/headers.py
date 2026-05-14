from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


def _bool_header(value: bool) -> str:
    return "true" if value else "false"


def _validate_text(name: str, value: Optional[str], max_length: int) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"{name} must be a non-empty string")
    if len(value) > max_length:
        raise ValueError(f"{name} must be at most {max_length} characters")
    if "\r" in value or "\n" in value:
        raise ValueError(f"{name} must not contain newlines")
    return value


def _validate_bool(name: str, value: Optional[bool]) -> Optional[bool]:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a bool")
    return value


def _validate_int(name: str, value: Optional[int]) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value


@dataclass(frozen=True)
class CacheHeaders:
    enabled: Optional[bool] = None
    read: Optional[bool] = None
    save: Optional[bool] = None
    bucket_max_size: Optional[int] = None
    seed: Optional[int] = None
    cache_control: Optional[str] = None

    def __post_init__(self) -> None:
        _validate_bool("enabled", self.enabled)
        _validate_bool("read", self.read)
        _validate_bool("save", self.save)
        _validate_int("bucket_max_size", self.bucket_max_size)
        _validate_int("seed", self.seed)
        if self.bucket_max_size is not None and not (1 <= self.bucket_max_size <= 20):
            raise ValueError("bucket_max_size must be between 1 and 20")
        _validate_text("cache_control", self.cache_control, 128)

    def to_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.enabled is not None:
            headers["Alephant-Cache-Enabled"] = _bool_header(self.enabled)
        if self.read is not None:
            headers["Alephant-Cache-Read"] = _bool_header(self.read)
        if self.save is not None:
            headers["Alephant-Cache-Save"] = _bool_header(self.save)
        if self.bucket_max_size is not None:
            headers["Alephant-Cache-Bucket-Max-Size"] = str(self.bucket_max_size)
        if self.seed is not None:
            headers["Alephant-Cache-Seed"] = str(self.seed)
        if self.cache_control is not None:
            headers["Alephant-Cache-Control"] = self.cache_control
        return headers


@dataclass(frozen=True)
class GatewayHeaders:
    forced_routing: Optional[str] = None
    prompt_id: Optional[str] = None
    omit_request: Optional[bool] = None
    omit_response: Optional[bool] = None
    webhook_enabled: Optional[bool] = None
    cache: Optional[CacheHeaders] = None

    def __post_init__(self) -> None:
        _validate_text("forced_routing", self.forced_routing, 64)
        _validate_text("prompt_id", self.prompt_id, 128)
        _validate_bool("omit_request", self.omit_request)
        _validate_bool("omit_response", self.omit_response)
        _validate_bool("webhook_enabled", self.webhook_enabled)
        if self.cache is not None and not isinstance(self.cache, CacheHeaders):
            raise ValueError("cache must be a CacheHeaders instance")

    def to_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.forced_routing is not None:
            headers["alephant-forced-routing"] = self.forced_routing
        if self.prompt_id is not None:
            headers["alephant-prompt-id"] = self.prompt_id
        if self.omit_request is True:
            headers["alephant-omit-request"] = "true"
        if self.omit_response is True:
            headers["alephant-omit-response"] = "true"
        if self.webhook_enabled is True:
            headers["x-alephant-webhook-enabled"] = "true"
        if self.cache is not None:
            headers.update(self.cache.to_headers())
        return headers
