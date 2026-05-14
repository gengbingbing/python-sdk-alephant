from __future__ import annotations

from collections.abc import Mapping
import re
import secrets
import string
from typing import Dict, Optional

from .headers import GatewayHeaders

_ID_ALPHABET = string.ascii_letters + string.digits + "_-"
_PROPERTY_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_SENSITIVE_PROPERTY_KEY_PARTS = ("token", "secret", "password", "apikey")
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")
_PROPERTY_VALUE_TYPES = (str, int, float, bool)


def _new_session_id() -> str:
    return "sess_" + "".join(secrets.choice(_ID_ALPHABET) for _ in range(24))


def _validate_header_value(name: str, value: str, max_length: int) -> str:
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"{name} must be a non-empty string")
    if len(value) > max_length:
        raise ValueError(f"{name} must be at most {max_length} characters")
    if _CONTROL_CHAR_RE.search(value):
        raise ValueError(f"{name} must not contain control characters")
    return value


def _normalize_path(path: Optional[str]) -> Optional[str]:
    if path is None:
        return None
    value = _validate_header_value("session_path", path, 256)
    normalized = value if value.startswith("/") else f"/{value}"
    return _validate_header_value("session_path", normalized, 256)


def _property_header_name(key: str) -> str:
    if not isinstance(key, str) or not _PROPERTY_KEY_RE.fullmatch(key):
        raise ValueError("property key must match ^[a-z0-9][a-z0-9_-]{0,63}$")
    normalized_key = key.replace("-", "").replace("_", "")
    if any(part in normalized_key for part in _SENSITIVE_PROPERTY_KEY_PARTS):
        raise ValueError("property key must not look like a secret")
    return f"alephant-property-{key}"


def _normalize_properties(properties: Optional[Mapping[str, object]]) -> Dict[str, str]:
    if properties is not None and not isinstance(properties, Mapping):
        raise ValueError("properties must be a mapping")
    result: Dict[str, str] = {}
    for key, raw_value in (properties or {}).items():
        _property_header_name(key)
        if not isinstance(raw_value, _PROPERTY_VALUE_TYPES):
            raise ValueError(f"property {key} must be a string, number, or bool")
        result[key] = _validate_header_value(f"property {key}", str(raw_value), 512)
    return result


def _validate_gateway_headers(headers: Optional[GatewayHeaders]) -> Optional[GatewayHeaders]:
    if headers is not None and not isinstance(headers, GatewayHeaders):
        raise ValueError("headers must be a GatewayHeaders instance")
    return headers


class AlephantGatewayContext:
    def __init__(
        self,
        *,
        session_id: Optional[str] = None,
        session_name: Optional[str] = None,
        session_path: Optional[str] = None,
        headers: Optional[GatewayHeaders] = None,
        properties: Optional[Mapping[str, object]] = None,
    ) -> None:
        self.session_id = (
            _validate_header_value("session_id", session_id, 128)
            if session_id is not None
            else _new_session_id()
        )
        self.session_name = (
            _validate_header_value("session_name", session_name, 128)
            if session_name is not None
            else None
        )
        self.session_path = _normalize_path(session_path)
        self.gateway_headers = _validate_gateway_headers(headers)
        self.properties = _normalize_properties(properties)

    def headers(self) -> Dict[str, str]:
        result: Dict[str, str] = {"Alephant-Session-Id": self.session_id}
        if self.session_name is not None:
            result["Alephant-Session-Name"] = self.session_name
        if self.session_path is not None:
            result["Alephant-Session-Path"] = self.session_path
        if self.gateway_headers is not None:
            result.update(self.gateway_headers.to_headers())
        for key, raw_value in self.properties.items():
            value = _validate_header_value(f"property {key}", str(raw_value), 512)
            result[_property_header_name(key)] = value
        return result
