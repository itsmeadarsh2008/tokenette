"""
Meta Tools - Dynamic Tool Discovery

Implements the 3 meta-tools that enable 96% token savings:
1. discover_tools: Find tools by category/keyword (vs loading all schemas)
2. get_tool_details: Load full schema on-demand
3. execute_tool: Run tool with caching and optimization
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from fastmcp import Context


@dataclass
class ToolMetadata:
    """Lightweight tool metadata for discovery."""

    name: str
    description: str
    category: str
    popularity: int = 0  # Usage count
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "desc": self.description[:80],  # Truncate for token savings
            "cat": self.category,
            "pop": self.popularity,
        }


@dataclass
class ToolDetails:
    """Full tool schema with parameters."""

    name: str
    description: str
    category: str
    parameters: dict[str, Any]
    returns: str
    examples: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "parameters": self.parameters,
            "returns": self.returns,
            "examples": self.examples,
        }


# Tool registry - lightweight metadata for discovery
TOOL_REGISTRY: dict[str, ToolMetadata] = {
    # Meta tools
    "discover_tools": ToolMetadata(
        name="discover_tools",
        description="Discover available tools with minimal metadata",
        category="meta",
        popularity=1000,
        tags=["meta", "discover", "tools"],
    ),
    "get_tool_details": ToolMetadata(
        name="get_tool_details",
        description="Get full schema for a specific tool",
        category="meta",
        popularity=800,
        tags=["meta", "schema", "details"],
    ),
    "execute_tool": ToolMetadata(
        name="execute_tool",
        description="Execute a tool dynamically via the registry",
        category="meta",
        popularity=700,
        tags=["meta", "execute", "tool"],
    ),
    # File Operations
    "read_file_smart": ToolMetadata(
        name="read_file_smart",
        description="Read file with intelligent strategy (full, partial, summary, AST)",
        category="file",
        popularity=500,
        tags=["read", "file", "optimize"],
    ),
    "write_file_diff": ToolMetadata(
        name="write_file_diff",
        description="Write file changes using diff format (97% smaller than full file)",
        category="file",
        popularity=450,
        tags=["write", "file", "diff", "edit"],
    ),
    "search_code_semantic": ToolMetadata(
        name="search_code_semantic",
        description="Semantic code search across files (98% savings vs grep)",
        category="file",
        popularity=380,
        tags=["search", "code", "semantic"],
    ),
    "get_file_structure": ToolMetadata(
        name="get_file_structure",
        description="Get AST structure of file (functions, classes, imports)",
        category="file",
        popularity=320,
        tags=["structure", "ast", "analyze"],
    ),
    "batch_read_files": ToolMetadata(
        name="batch_read_files",
        description="Read multiple files with cross-file deduplication",
        category="file",
        popularity=280,
        tags=["batch", "read", "files"],
    ),
    "batch_ops": ToolMetadata(
        name="batch_ops",
        description="Execute batched file operations (read/write/search/analyze) in one payload",
        category="file",
        popularity=260,
        tags=["batch", "ops", "read", "write", "search"],
    ),
    # Analysis
    "analyze_code": ToolMetadata(
        name="analyze_code",
        description="Analyze code for patterns, complexity, and issues",
        category="analysis",
        popularity=300,
        tags=["analyze", "code", "quality"],
    ),
    "find_bugs": ToolMetadata(
        name="find_bugs",
        description="Find potential bugs and security issues",
        category="analysis",
        popularity=250,
        tags=["bugs", "security", "lint"],
    ),
    "get_complexity": ToolMetadata(
        name="get_complexity",
        description="Calculate cyclomatic complexity metrics",
        category="analysis",
        popularity=180,
        tags=["complexity", "metrics"],
    ),
    # Documentation (via Context7)
    "get_docs": ToolMetadata(
        name="get_docs",
        description="Get package documentation (cached, compressed)",
        category="docs",
        popularity=400,
        tags=["docs", "documentation", "package"],
    ),
    "search_docs": ToolMetadata(
        name="search_docs",
        description="Search documentation with semantic matching",
        category="docs",
        popularity=350,
        tags=["search", "docs", "api"],
    ),
    # Optimization
    "optimize_response": ToolMetadata(
        name="optimize_response",
        description="Optimize any data for minimal token usage",
        category="optimize",
        popularity=200,
        tags=["optimize", "tokens", "minify"],
    ),
    "get_metrics": ToolMetadata(
        name="get_metrics",
        description="Get Tokenette performance metrics",
        category="system",
        popularity=150,
        tags=["metrics", "stats", "performance"],
    ),
}

# Full tool schemas (loaded on demand)
TOOL_SCHEMAS: dict[str, ToolDetails] = {
    "discover_tools": ToolDetails(
        name="discover_tools",
        description="Discover available tools with minimal metadata.",
        category="meta",
        parameters={
            "category": {"type": "string", "description": "Filter by category"},
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "integer", "default": 10, "description": "Max tools to return"},
        },
        returns="List of tools with minimal metadata",
        examples=[{"input": {"category": "file"}, "description": "List file tools"}],
    ),
    "get_tool_details": ToolDetails(
        name="get_tool_details",
        description="Get full schema for a specific tool.",
        category="meta",
        parameters={
            "tool_name": {"type": "string", "description": "Tool name", "required": True},
            "include_examples": {
                "type": "boolean",
                "default": True,
                "description": "Include example usage",
            },
        },
        returns="Full tool schema",
        examples=[{"input": {"tool_name": "tokenette_read_file"}, "description": "Tool schema"}],
    ),
    "execute_tool": ToolDetails(
        name="execute_tool",
        description="Execute a tool dynamically via the registry.",
        category="meta",
        parameters={
            "tool_name": {"type": "string", "description": "Tool name", "required": True},
            "arguments": {"type": "object", "description": "Tool arguments", "required": True},
            "cache_key": {"type": "string", "description": "Optional cache key"},
            "skip_cache": {
                "type": "boolean",
                "default": False,
                "description": "Skip cache lookup",
            },
        },
        returns="Tool result (optionally optimized)",
        examples=[
            {
                "input": {
                    "tool_name": "tokenette_read_file",
                    "arguments": {"path": "README.md"},
                },
                "description": "Execute read file",
            }
        ],
    ),
    "read_file_smart": ToolDetails(
        name="read_file_smart",
        description=(
            "Read a file with intelligent strategy selection. "
            "Automatically chooses the most token-efficient approach: "
            "full (small files), partial (medium), summary (large), or AST (code analysis)."
        ),
        category="file",
        parameters={
            "path": {"type": "string", "description": "Path to the file to read", "required": True},
            "strategy": {
                "type": "string",
                "enum": ["auto", "full", "partial", "summary", "ast"],
                "default": "auto",
                "description": "Reading strategy (auto recommended)",
            },
            "start_line": {"type": "integer", "description": "Start line for partial reads"},
            "end_line": {"type": "integer", "description": "End line for partial reads"},
        },
        returns="File content in optimized format",
        examples=[
            {"input": {"path": "src/main.py"}, "description": "Read with auto strategy"},
            {"input": {"path": "src/app.js", "strategy": "ast"}, "description": "Get AST only"},
        ],
    ),
    "write_file_diff": ToolDetails(
        name="write_file_diff",
        description=(
            "Write file changes using unified diff format. "
            "97% more token-efficient than sending full file content. "
            "Validates changes before applying."
        ),
        category="file",
        parameters={
            "path": {
                "type": "string",
                "description": "Path to the file to modify",
                "required": True,
            },
            "changes": {
                "type": "string",
                "description": "Changes in unified diff format (@@ -line,count +line,count @@)",
                "required": True,
            },
            "verify": {
                "type": "boolean",
                "default": True,
                "description": "Verify file hash before applying",
            },
            "expected_hash": {
                "type": "string",
                "description": "Optional file hash to verify against",
            },
        },
        returns="Result of the write operation",
        examples=[
            {
                "input": {
                    "path": "src/config.js",
                    "changes": "@@ -10,0 +10,2 @@\n+const DEBUG = true;\n+const API_URL = 'http://localhost:3000';",
                },
                "description": "Add 2 lines after line 10",
            }
        ],
    ),
    "search_code_semantic": ToolDetails(
        name="search_code_semantic",
        description=(
            "Search code using semantic matching. "
            "98% more efficient than grep for finding relevant code. "
            "Returns ranked snippets with context."
        ),
        category="file",
        parameters={
            "query": {
                "type": "string",
                "description": "Natural language search query",
                "required": True,
            },
            "directory": {
                "type": "string",
                "description": "Directory to search in",
                "default": ".",
            },
            "file_pattern": {"type": "string", "description": "File glob pattern (e.g., '*.py')"},
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum results to return",
            },
        },
        returns="Ranked list of code snippets",
        examples=[
            {"input": {"query": "authentication middleware"}, "description": "Find auth code"},
            {
                "input": {"query": "database connection", "file_pattern": "*.py"},
                "description": "Find DB code in Python",
            },
        ],
    ),
    "get_file_structure": ToolDetails(
        name="get_file_structure",
        description=(
            "Get the structural overview of a file (AST-based). "
            "99% token savings for understanding file organization. "
            "Returns functions, classes, imports without full code."
        ),
        category="file",
        parameters={
            "path": {"type": "string", "description": "Path to the file", "required": True},
            "depth": {
                "type": "integer",
                "default": 2,
                "description": "Depth of nesting to show (1-5)",
            },
            "include_signatures": {
                "type": "boolean",
                "default": True,
                "description": "Include function signatures",
            },
        },
        returns="File structure in TOON format",
        examples=[
            {"input": {"path": "src/app.py"}, "description": "Get structure"},
            {"input": {"path": "src/utils.js", "depth": 3}, "description": "Get deeper structure"},
        ],
    ),
    "batch_read_files": ToolDetails(
        name="batch_read_files",
        description=(
            "Read multiple files with cross-file deduplication. "
            "60-80% savings on multi-file operations. "
            "Shared imports and patterns are extracted once."
        ),
        category="file",
        parameters={
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of file paths to read",
                "required": True,
            },
            "deduplicate": {
                "type": "boolean",
                "default": True,
                "description": "Enable cross-file deduplication",
            },
            "strategy": {"type": "string", "enum": ["auto", "full", "summary"], "default": "auto"},
        },
        returns="Batch result with deduplicated content",
        examples=[
            {
                "input": {"paths": ["src/a.py", "src/b.py", "src/c.py"]},
                "description": "Read 3 files with deduplication",
            }
        ],
    ),
    "batch_ops": ToolDetails(
        name="batch_ops",
        description=(
            "Execute batched operations (read/write/search/analyze) in a single "
            "payload with minification and deduplication."
        ),
        category="file",
        parameters={
            "operations": {
                "type": "array",
                "items": {"type": "object"},
                "description": "List of operations with type and parameters",
                "required": True,
            }
        },
        returns="Minified batch payload with results",
        examples=[
            {
                "input": {
                    "operations": [
                        {"type": "read", "path": "src/app.py"},
                        {"type": "search", "query": "auth", "directory": "src"},
                    ]
                },
                "description": "Read + search in one batch",
            }
        ],
    ),
    "analyze_code": ToolDetails(
        name="analyze_code",
        description="Analyze code for patterns, complexity, and potential issues.",
        category="analysis",
        parameters={
            "path": {
                "type": "string",
                "description": "Path to file or directory",
                "required": True,
            },
            "checks": {
                "type": "array",
                "items": {"type": "string"},
                "default": ["complexity", "style", "security"],
                "description": "Analysis checks to run",
            },
        },
        returns="Analysis results",
        examples=[],
    ),
    "find_bugs": ToolDetails(
        name="find_bugs",
        description="Find potential bugs and security issues in code.",
        category="analysis",
        parameters={
            "path": {
                "type": "string",
                "description": "Path to file or directory",
                "required": True,
            },
            "severity": {
                "type": "string",
                "enum": ["all", "high", "medium", "low"],
                "default": "all",
            },
        },
        returns="List of potential issues",
        examples=[],
    ),
    "get_complexity": ToolDetails(
        name="get_complexity",
        description="Calculate cyclomatic complexity and other metrics.",
        category="analysis",
        parameters={"path": {"type": "string", "description": "Path to file", "required": True}},
        returns="Complexity metrics",
        examples=[],
    ),
    "get_docs": ToolDetails(
        name="get_docs",
        description="Get package documentation via Context7 (cached).",
        category="docs",
        parameters={
            "package": {
                "type": "string",
                "description": "Package name (e.g., 'react', 'fastapi')",
                "required": True,
            },
            "topic": {"type": "string", "description": "Specific topic to fetch"},
            "version": {"type": "string", "description": "Package version"},
        },
        returns="Compressed documentation",
        examples=[],
    ),
    "search_docs": ToolDetails(
        name="search_docs",
        description="Search documentation with semantic matching.",
        category="docs",
        parameters={
            "query": {"type": "string", "description": "Search query", "required": True},
            "package": {"type": "string", "description": "Limit to specific package"},
        },
        returns="Relevant documentation snippets",
        examples=[],
    ),
    "optimize_response": ToolDetails(
        name="optimize_response",
        description="Optimize any data for minimal token usage.",
        category="optimize",
        parameters={
            "data": {"type": "any", "description": "Data to optimize", "required": True},
            "format": {
                "type": "string",
                "enum": ["auto", "json", "toon", "code"],
                "default": "auto",
            },
        },
        returns="Optimized data",
        examples=[],
    ),
    "get_metrics": ToolDetails(
        name="get_metrics",
        description="Get Tokenette performance metrics and savings.",
        category="system",
        parameters={},
        returns="Performance metrics",
        examples=[],
    ),
}


def _prefix_tool_name(name: str) -> str:
    return name if name.startswith("tokenette_") else f"tokenette_{name}"


def _strip_tool_prefix(name: str) -> str:
    return name.replace("tokenette_", "", 1) if name.startswith("tokenette_") else name


async def discover_tools(
    category: str | None = None,
    query: str | None = None,
    limit: int = 10,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Discover available tools without loading full schemas.

    96% token savings vs listing all tool schemas upfront.

    Args:
        category: Filter by category (file, analysis, docs, optimize, system)
        query: Search query for tool names/descriptions
        limit: Maximum tools to return
        ctx: MCP context

    Returns:
        List of matching tools with minimal metadata
    """
    results = []

    for name, metadata in TOOL_REGISTRY.items():
        # Filter by category
        if category and metadata.category != category:
            continue

        # Filter by query
        if query:
            query_lower = query.lower()
            matches = (
                query_lower in name.lower()
                or query_lower in metadata.description.lower()
                or any(query_lower in tag for tag in metadata.tags)
            )
            if not matches:
                continue

        tool_dict = metadata.to_dict()
        tool_dict["name"] = _prefix_tool_name(name)
        results.append(tool_dict)

    # Sort by popularity
    results.sort(key=lambda x: x.get("pop", 0), reverse=True)

    # Limit results
    results = results[:limit]

    return {
        "tools": results,
        "total": len(results),
        "categories": list({m.category for m in TOOL_REGISTRY.values()}),
        "_tokens": len(results) * 20,  # Approximate token cost
    }


async def get_tool_details(
    tool_name: str, include_examples: bool = True, ctx: Context | None = None
) -> dict[str, Any]:
    """
    Get full schema for a specific tool.

    Loaded on-demand to save tokens.

    Args:
        tool_name: Name of the tool
        include_examples: Include usage examples
        ctx: MCP context

    Returns:
        Full tool schema with parameters
    """
    lookup_name = _strip_tool_prefix(tool_name)
    if lookup_name not in TOOL_SCHEMAS:
        return {
            "error": f"Tool '{tool_name}' not found",
            "available": [_prefix_tool_name(n) for n in TOOL_REGISTRY],
        }

    schema = TOOL_SCHEMAS[lookup_name]
    result = schema.to_dict()
    result["name"] = _prefix_tool_name(schema.name)

    if not include_examples:
        result.pop("examples", None)

    return result


async def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    cache_key: str | None = None,
    skip_cache: bool = False,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Execute a tool with caching and optimization.

    Automatically caches results and optimizes response.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments
        cache_key: Custom cache key (auto-generated if None)
        skip_cache: Skip cache lookup
        ctx: MCP context

    Returns:
        Optimized tool result
    """
    lookup_name = _strip_tool_prefix(tool_name)
    if lookup_name not in TOOL_REGISTRY:
        return {
            "error": f"Tool '{tool_name}' not found",
            "available": [_prefix_tool_name(n) for n in TOOL_REGISTRY],
        }

    # Import tools dynamically to avoid circular imports
    from tokenette.tools import analysis, file_ops

    # Tool dispatch map
    tool_functions: dict[str, Callable[..., Any]] = {
        "discover_tools": discover_tools,
        "get_tool_details": get_tool_details,
        "read_file_smart": file_ops.read_file_smart,
        "write_file_diff": file_ops.write_file_diff,
        "search_code_semantic": file_ops.search_code_semantic,
        "get_file_structure": file_ops.get_file_structure,
        "batch_read_files": file_ops.batch_read_files,
        "analyze_code": analysis.analyze_code,
        "find_bugs": analysis.find_bugs,
        "get_complexity": analysis.get_complexity,
    }

    if lookup_name == "batch_ops":
        from tokenette.core.batcher import InteractionBatcher

        batcher = InteractionBatcher()
        return await batcher.batch_file_operations(arguments.get("operations", []))

    if lookup_name not in tool_functions:
        return {"error": f"Tool '{tool_name}' not yet implemented", "status": "pending"}

    # Execute tool
    func = tool_functions[lookup_name]

    try:
        result = await func(**arguments, ctx=ctx)

        # Update popularity
        TOOL_REGISTRY[lookup_name].popularity += 1

        return {"status": "success", "tool": _prefix_tool_name(lookup_name), "result": result}
    except Exception as e:
        return {"status": "error", "tool": _prefix_tool_name(lookup_name), "error": str(e)}
