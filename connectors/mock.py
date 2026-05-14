# SPDX-License-Identifier: Apache-2.0
"""In-memory connector used by tests and demos."""

from __future__ import annotations

from typing import Any

from connectors.base import ConnectorCapabilities, require_write_enabled


class InMemoryConnector:
    def __init__(
        self,
        accounts: dict[str, dict[str, Any]] | None = None,
        *,
        name: str = "in-memory",
        write_enabled: bool = False,
    ) -> None:
        self.capabilities = ConnectorCapabilities(
            name=name,
            read_only=not write_enabled,
            can_write=write_enabled,
        )
        self.accounts = dict(accounts or {})
        self.records: dict[str, list[dict[str, Any]]] = {}

    def read_account(self, account_id: str) -> dict[str, Any]:
        if account_id not in self.accounts:
            return {}
        return dict(self.accounts[account_id])

    def upsert_record(self, schema_slot: str, record: dict[str, Any]) -> bool:
        require_write_enabled(self.capabilities)
        if not schema_slot:
            raise ValueError("schema_slot must be non-empty")
        self.records.setdefault(schema_slot, []).append(dict(record))
        return True
