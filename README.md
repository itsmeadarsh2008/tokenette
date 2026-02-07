# Tokenette

**The Ultimate All-in-One AI Coding Enhancement MCP**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Zero-Loss Token Optimization · Intelligent Model Routing · Quality Amplification

Tokenette is a FastMCP server and Python toolkit that reduces token usage and premium request cost while preserving output quality. It combines multi-layer caching, minification, semantic compression, dynamic tool discovery, and smart file operations. It also routes tasks to the most cost-effective model and amplifies prompts for cheaper models.

Compatible with GitHub Copilot Pro/Business, Claude Code, Gemini CLI, Cursor, OpenCode, and any MCP client that supports stdio, SSE, or HTTP transports.

Version: 2.0.1 (Beta)

## Core Pillars

- Route Right: Detect task complexity and select the cheapest model that meets quality thresholds, with auto-mode discounts and budget tracking.
- Amplify Low: Boost prompt quality with expert framing, structured outputs, and reasoning templates so cheaper models perform better.
- Shrink Everything: Minify, deduplicate, compress, and cache outputs to reduce tokens without losing meaning.

## Highlights

- Multi-layer cache (L1-L4) with disk tiers and optional semantic index for repeated operations.
- Minification engine with JSON, code, and TOON formats for 20-61% transmission savings.
- Semantic compression with quality guardrails and automatic fallback.
- Smart file operations with auto strategies, AST summaries, diff-based writes, and streaming for large files.
- Dynamic tool discovery that loads schemas on demand to reduce overhead.
- Context7 documentation integration with caching and pagination.
- Git and workspace intelligence tools for diffs, history, project info, and dependency insights.
- Metrics, token estimation, and budget status built into tools and CLI.

## Architecture

```
Client (MCP)
    |
    v
Tokenette MCP Server
    |-- Request intelligence + model routing
    |-- Multi-layer cache (L1 hot, L2 warm, L3 cold, L4 semantic)
    |-- Minification engine (JSON, code, TOON)
    |-- Semantic compression + quality validation
    |-- Tool registry + dynamic discovery
    |-- Metrics + budget tracking
```

## Quick Start

Prerequisites: Python 3.11+

Install locally from source:

```bash
pip install -e .
# or
uv pip install -e .
```

Run the MCP server:

```bash
tokenette run
# SSE transport
tokenette run --transport sse --port 8000
# HTTP transport (Uvicorn)
tokenette run --transport http --port 8000 --reload
```

MCP client configuration example (`mcp.json`):

```json
{
  "mcpServers": {
    "tokenette": {
      "command": "tokenette",
      "args": ["run"]
    }
  }
}
```

## CLI

| Command | Purpose |
| --- | --- |
| `tokenette run` | Start the MCP server (stdio, SSE, or HTTP) |
| `tokenette metrics` | View cache, token savings, and budget usage |
| `tokenette config` | Show or initialize `.tokenette.json` |
| `tokenette cache` | Inspect or clear cache layers |
| `tokenette analyze` | Analyze code for complexity, security, and style |
| `tokenette route` | Get model routing recommendations |
| `tokenette version` | Print installed version |

## MCP Tool Catalog

All tools are exposed with a `tokenette_` prefix. Use `tokenette_discover_tools` to fetch a compact list and `tokenette_get_tool_details` for full schemas.

| Category | Tools |
| --- | --- |
| Meta | `tokenette_discover_tools`, `tokenette_get_tool_details`, `tokenette_execute_tool` |
| File | `tokenette_read_file`, `tokenette_write_file`, `tokenette_search_code`, `tokenette_get_structure`, `tokenette_batch_read`, `tokenette_batch_ops` |
| Analysis | `tokenette_analyze`, `tokenette_find_bugs`, `tokenette_complexity` |
| Docs | `tokenette_resolve_lib`, `tokenette_get_docs`, `tokenette_search_docs` |
| Optimization | `tokenette_optimize`, `tokenette_route_task`, `tokenette_amplify`, `tokenette_metrics` |
| Git | `tokenette_git_diff`, `tokenette_git_status`, `tokenette_git_history`, `tokenette_git_blame` |
| Prompts | `tokenette_list_prompts`, `tokenette_build_prompt` |
| Tokens and Cost | `tokenette_count_tokens`, `tokenette_estimate_cost`, `tokenette_compare_models`, `tokenette_budget_status` |
| Workspace | `tokenette_project_info`, `tokenette_workspace_summary`, `tokenette_code_health`, `tokenette_smart_context`, `tokenette_dependencies` |

## Default Model Multipliers

Tokenette ships with a model cost table tailored for GitHub Copilot-style multiplier billing. These defaults reflect the configuration in this repository (updated February 2026) and are fully configurable.

| Model | Multiplier | Tier |
| --- | --- | --- |
| GPT-4.1 | 0 | Free |
| GPT-4o | 0 | Free |
| GPT-4.1 Mini | 0 | Free |
| Gemini 2.0 Flash | 0.25 | Cheap |
| o4-mini | 0.33 | Cheap |
| o3-mini | 0.33 | Cheap |
| Claude Sonnet 4 | 1.0 | Moderate |
| Gemini 2.5 Pro | 1.0 | Moderate |
| Claude Opus 4.5 | 3.0 | Expensive |
| Claude Opus 4 | 10.0 | Expensive |
| GPT-4.5 | 50.0 | Avoid |

## Token Optimization Pipeline

Typical savings depend on content size and repetition, but the pipeline is designed for aggressive reduction while preserving quality.

| Stage | Purpose | Typical Savings |
| --- | --- | --- |
| Cache | Reuse prior outputs across repeated requests | Up to 99.8% on repeats |
| Minification | Remove whitespace and redundant syntax | 20-61% |
| Deduplication | Remove repeated structures | 40-60% |
| Reference extraction | Replace large repeated objects with refs | 20-40% |
| Semantic compression | Summarize large text with quality checks | 30-50% |

## Smart File Strategies

| Strategy | Use Case | Notes |
| --- | --- | --- |
| `full` | Small files | Full content |
| `partial` | Targeted edits | Range-based reads |
| `summary` | Medium-large code | AST summary + key sections |
| `ast` | Very large code | Structure only |
| `stream` | Huge files | Chunked streaming when enabled |

## Configuration

Tokenette looks for `.tokenette.json` in the current directory, then home directory, and finally falls back to environment variables and defaults.

Example `.tokenette.json`:

```json
{
  "cache": {
    "l1_max_size_mb": 100,
    "l1_ttl_seconds": 1800,
    "l2_enabled": true,
    "l2_max_size_mb": 2048,
    "l3_enabled": true,
    "l3_max_size_mb": 51200,
    "l4_enabled": false
  },
  "compression": {
    "min_quality_score": 0.95,
    "use_toon_format": true,
    "toon_min_items": 10,
    "large_text_threshold": 4000
  },
  "router": {
    "monthly_premium_limit": 300,
    "use_auto_mode_discount": true,
    "auto_mode_discount_rate": 0.1
  },
  "context7": {
    "enabled": true,
    "cache_docs": true,
    "max_doc_tokens": 8000
  },
  "server": {
    "transport": "stdio",
    "host": "127.0.0.1",
    "port": 8000
  }
}
```

Environment variable examples:

```bash
export TOKENETTE_CACHE__L1_MAX_SIZE_MB=200
export TOKENETTE_CONTEXT7__ENABLED=false
```

## Optional Extras

Enable semantic search and the L4 vector cache:

```bash
pip install "tokenette[vector]"
```

## Python API

```python
import asyncio
from tokenette import TaskRouter, TaskCategory, QualityAmplifier, OptimizationPipeline, mcp

router = TaskRouter()
decision = router.route("refactor authentication module", {"affected_files": 5})
print(decision.model, decision.multiplier)

amplifier = QualityAmplifier()
amplified = amplifier.amplify(
    prompt="Refactor the auth module",
    boosters=["expert_role_framing", "chain_of_thought_injection"],
    category=TaskCategory.REFACTOR,
    context={},
)
print(amplified.prompt)

async def main():
    pipeline = OptimizationPipeline()
    result = await pipeline.optimize({"hello": "world"})
    print(result.to_response())

asyncio.run(main())

# MCP server
# mcp.run()
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src/tokenette
mypy src/tokenette
```

## Contributing

Contributions are welcome. See `CONTRIBUTING.md` for guidelines.

## License

MIT License. See `LICENSE` for details.
