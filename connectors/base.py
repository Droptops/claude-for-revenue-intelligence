# SPDX-License-Identifier: Apache-2.0
"""Connector protocols for the revenue-intelligence harness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ConnectorCapabilities:
    name: str
    read_only: bool = True
    can_write: bool = False


class ReadOnlyConnector(Protocol):
    capabilities: ConnectorCapabilities

    def read_account(self, account_id: str) -> dict[str, Any]:
        """Return one account-shaped payload from the upstream system."""


class WriteConnector(ReadOnlyConnector, Protocol):
    def upsert_record(self, schema_slot: str, record: dict[str, Any]) -> bool:
        """Write one schema-shaped record after explicit operator approval."""


def require_write_enabled(capabilities: ConnectorCapabilities) -> None:
    if capabilities.read_only or not capabilities.can_write:
        raise PermissionError(
            f"connector {capabilities.name!r} is read-only; enable writes explicitly"
        )
