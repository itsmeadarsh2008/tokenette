"""
Metrics Tracking

Lightweight metrics and observability for Tokenette:
- Tool usage counts
- Token in/out/saved estimates
- Cache hit/miss tracking
- Model usage and cost multipliers
- Optional persistence to JSON
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tokenette.config import MetricsConfig


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class ToolMetrics:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    tokens_saved: int = 0
    cache_hits: int = 0
    cache_misses: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "calls": self.calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "tokens_saved": self.tokens_saved,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
        }


@dataclass
class ModelMetrics:
    calls: int = 0
    multiplier_total: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {"calls": self.calls, "multiplier_total": round(self.multiplier_total, 2)}


class MetricsTracker:
    """Tracks Tokenette usage and token savings."""

    def __init__(self, config: MetricsConfig | None = None):
        self.config = config or MetricsConfig()
        self.started_at = _utc_now()
        self.last_updated = self.started_at

        self.total_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.tokens_saved = 0
        self.cache_hits = 0
        self.cache_misses = 0

        self.tools: dict[str, ToolMetrics] = {}
        self.models: dict[str, ModelMetrics] = {}

        self._lock = threading.Lock()
        if self.config.persist_metrics:
            self._load()

    def record_tool_call(
        self,
        tool_name: str,
        input_data: Any | None = None,
        output_data: Any | None = None,
        tokens_saved: int = 0,
        cache_hit: bool | None = None,
    ) -> None:
        input_tokens = self._estimate_tokens(input_data)
        output_tokens = self._estimate_tokens(output_data)

        with self._lock:
            tool = self.tools.setdefault(tool_name, ToolMetrics())
            tool.calls += 1
            tool.input_tokens += input_tokens
            tool.output_tokens += output_tokens
            tool.tokens_saved += max(0, tokens_saved)

            if cache_hit is True:
                tool.cache_hits += 1
                self.cache_hits += 1
            elif cache_hit is False:
                tool.cache_misses += 1
                self.cache_misses += 1

            self.total_calls += 1
            self.input_tokens += input_tokens
            self.output_tokens += output_tokens
            self.tokens_saved += max(0, tokens_saved)
            self.last_updated = _utc_now()

        self._persist()

    def record_cache(self, hit: bool, tokens_saved: int = 0) -> None:
        with self._lock:
            if hit:
                self.cache_hits += 1
            else:
                self.cache_misses += 1
            self.tokens_saved += max(0, tokens_saved)
            self.last_updated = _utc_now()
        self._persist()

    def record_model_use(self, model: str, multiplier: float = 0.0) -> None:
        with self._lock:
            metrics = self.models.setdefault(model, ModelMetrics())
            metrics.calls += 1
            metrics.multiplier_total += float(multiplier)
            self.last_updated = _utc_now()
        self._persist()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "started_at": self.started_at,
                "last_updated": self.last_updated,
                "totals": {
                    "calls": self.total_calls,
                    "input_tokens": self.input_tokens,
                    "output_tokens": self.output_tokens,
                    "tokens_saved": self.tokens_saved,
                    "cache_hits": self.cache_hits,
                    "cache_misses": self.cache_misses,
                },
                "tools": {name: tm.to_dict() for name, tm in self.tools.items()},
                "models": {name: mm.to_dict() for name, mm in self.models.items()},
            }

    def reset(self) -> None:
        with self._lock:
            self.started_at = _utc_now()
            self.last_updated = self.started_at
            self.total_calls = 0
            self.input_tokens = 0
            self.output_tokens = 0
            self.tokens_saved = 0
            self.cache_hits = 0
            self.cache_misses = 0
            self.tools.clear()
            self.models.clear()
        self._persist()

    def _estimate_tokens(self, data: Any | None) -> int:
        if data is None:
            return 0
        if isinstance(data, str):
            return max(1, len(data) // 4)
        try:
            serialized = json.dumps(data, default=str)
            return max(1, len(serialized) // 4)
        except (TypeError, ValueError):
            return max(1, len(str(data)) // 4)

    def _load(self) -> None:
        path = Path(self.config.metrics_file)
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text())
        except Exception:
            return

        self.started_at = data.get("started_at", self.started_at)
        self.last_updated = data.get("last_updated", self.last_updated)

        totals = data.get("totals", {})
        self.total_calls = totals.get("calls", self.total_calls)
        self.input_tokens = totals.get("input_tokens", self.input_tokens)
        self.output_tokens = totals.get("output_tokens", self.output_tokens)
        self.tokens_saved = totals.get("tokens_saved", self.tokens_saved)
        self.cache_hits = totals.get("cache_hits", self.cache_hits)
        self.cache_misses = totals.get("cache_misses", self.cache_misses)

        tools = data.get("tools", {})
        for name, tm in tools.items():
            self.tools[name] = ToolMetrics(**tm)

        models = data.get("models", {})
        for name, mm in models.items():
            self.models[name] = ModelMetrics(**mm)

    def _persist(self) -> None:
        if not self.config.persist_metrics:
            return
        path = Path(self.config.metrics_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = self.snapshot()
        tmp_path = path.with_suffix(".tmp")
        try:
            tmp_path.write_text(json.dumps(payload, indent=2))
            tmp_path.replace(path)
        except Exception:
            # Best-effort persistence; ignore failures
            return
