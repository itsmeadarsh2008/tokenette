"""
Interaction Batching Engine

Combines multiple operations into a single optimized payload to
reduce token usage and premium request costs.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import Any, Literal

from tokenette.core.minifier import MinificationEngine
from tokenette.tools.file_ops import read_file_smart, search_code_semantic, write_file_diff
from tokenette.tools.workspace import extract_smart_context, get_workspace_summary


OperationType = Literal["read", "write", "search", "analyze"]


@dataclass
class BatchOperation:
    """A single batch operation."""

    type: OperationType
    path: str | None = None
    strategy: str | None = None
    start_line: int | None = None
    end_line: int | None = None
    diff: str | None = None
    content: str | None = None
    query: str | None = None
    directory: str | None = None
    file_pattern: str | None = None
    max_results: int | None = None
    focus: str | None = None


class InteractionBatcher:
    """Batch multiple operations with deduplication and minification."""

    MAX_BATCH_TOKENS = 60_000
    MAX_BATCH_OPS = 25

    def __init__(self):
        self.minifier = MinificationEngine()

    async def batch_file_operations(self, operations: list[dict[str, Any]]) -> dict[str, Any]:
        if len(operations) > self.MAX_BATCH_OPS:
            return {"error": f"Too many operations: {len(operations)} > {self.MAX_BATCH_OPS}"}

        reads: list[dict[str, Any]] = []
        writes: list[dict[str, Any]] = []
        searches: list[dict[str, Any]] = []
        analyses: list[dict[str, Any]] = []

        for op in operations:
            op_type = op.get("type")
            if op_type == "read":
                reads.append(op)
            elif op_type == "write":
                writes.append(op)
            elif op_type == "search":
                searches.append(op)
            elif op_type == "analyze":
                analyses.append(op)

        read_results = [await self._run_read(op) for op in reads]
        read_results, shared = self._deduplicate_reads(read_results)
        write_results = [await self._run_write(op) for op in writes]
        search_results = [await self._run_search(op) for op in searches]
        analysis_results = [await self._run_analyze(op) for op in analyses]

        payload = {
            "_batch": True,
            "_ops": len(operations),
            "reads": read_results,
            "writes": write_results,
            "searches": search_results,
            "analyses": analysis_results,
            "shared": shared,
        }

        # Minify payload for transmission (client can format)
        minified = self.minifier.minify(payload, content_type="json")
        return {
            "payload": minified.data,
            "format": minified.format,
            "tokens": {
                "original": minified.original_tokens,
                "minified": minified.result_tokens,
                "saved_pct": minified.savings_pct,
            },
            "client_instruction": minified.client_instruction,
        }

    async def _run_read(self, op: dict[str, Any]) -> dict[str, Any]:
        return await read_file_smart(
            op.get("path", ""),
            op.get("strategy", "auto"),
            op.get("start_line"),
            op.get("end_line"),
            None,
        )

    async def _run_write(self, op: dict[str, Any]) -> dict[str, Any]:
        path = op.get("path", "")
        diff = op.get("diff")
        content = op.get("content")

        if not diff and content is not None:
            diff = self._to_diff(path, content)

        if not diff:
            return {"error": "Write operation requires diff or content", "path": path}

        return await write_file_diff(path, diff, None)

    async def _run_search(self, op: dict[str, Any]) -> dict[str, Any]:
        return await search_code_semantic(
            op.get("query", ""),
            op.get("directory", "."),
            op.get("file_pattern"),
            op.get("max_results", 10),
            None,
        )

    async def _run_analyze(self, op: dict[str, Any]) -> dict[str, Any]:
        directory = op.get("directory", ".")
        focus = op.get("focus", "overview")
        summary = await get_workspace_summary(directory, max_depth=3)
        if focus and focus != "overview":
            context = await extract_smart_context(directory, focus, max_tokens=4000)
        else:
            context = {"summary": summary.summary_text, "key_files": summary.key_files}
        return {"summary": summary.summary_text, "context": context}

    def _deduplicate_reads(
        self, results: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], dict[str, str]]:
        shared_segments: dict[str, str] = {}
        all_imports: list[str] = []

        for r in results:
            content = r.get("content")
            if isinstance(content, str):
                imports = [
                    line
                    for line in content.split("\n")
                    if line.startswith("import ") or line.startswith("from ")
                ]
                all_imports.extend(imports)

        if all_imports:
            from collections import Counter

            import_counts = Counter(all_imports)
            shared = [imp for imp, count in import_counts.items() if count > 1]
            if shared:
                shared_segments["_shared_imports"] = "\n".join(shared)
                for r in results:
                    content = r.get("content")
                    if isinstance(content, str):
                        for imp in shared:
                            content = content.replace(imp, "# → _shared_imports")
                        r["content"] = content

        return results, shared_segments

    def _to_diff(self, path: str, new_content: str) -> str:
        """Generate unified diff from file on disk to new content."""
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                old_lines = f.read().splitlines()
        except FileNotFoundError:
            old_lines = []

        new_lines = new_content.splitlines()
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
            lineterm="",
        )
        return "\n".join(diff)
