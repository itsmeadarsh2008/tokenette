"""
Tokenette MCP Server

The Ultimate All-in-One AI Coding Enhancement MCP
- Zero-Loss Token Optimization
- Intelligent Model Routing
- Quality Amplification

Built with FastMCP for maximum performance.
"""

from contextlib import asynccontextmanager
from typing import Any, Literal

from fastmcp import Context, FastMCP

from .config import TokenetteConfig, get_config
from .core import (
    InteractionBatcher,
    MetricsTracker,
    MultiLayerCache,
    OptimizationPipeline,
    QualityAmplifier,
    TaskRouter,
)
from .tools import (
    # Analysis tools
    analyze_code,
    batch_read_files,
    # Meta tools
    discover_tools,
    execute_tool,
    fetch_library_docs,
    find_bugs,
    get_complexity,
    get_context7_client,
    get_file_structure,
    get_tool_details,
    read_file_smart,
    # Context7 tools
    resolve_library,
    search_code_semantic,
    search_library_docs,
    write_file_diff,
)

# ─── LIFESPAN MANAGEMENT ─────────────────────────────────────────


@asynccontextmanager
async def lifespan(mcp: FastMCP):
    """
    Manage server lifecycle.

    Initializes:
    - Multi-layer cache (L1-L4)
    - Optimization pipeline
    - Task router
    - Quality amplifier
    - Context7 client
    """
    config = get_config()

    # Initialize core components
    cache = MultiLayerCache(config.cache)
    optimizer = OptimizationPipeline(config)  # Takes full config, creates its own cache
    router = TaskRouter(config.router)
    amplifier = QualityAmplifier(config.amplifier)
    context7 = await get_context7_client()
    metrics = MetricsTracker(config.metrics)
    batcher = InteractionBatcher()

    # Store in MCP context for tool access
    mcp.state = {
        "config": config,
        "cache": cache,
        "optimizer": optimizer,
        "router": router,
        "amplifier": amplifier,
        "context7": context7,
        "batcher": batcher,
        "metrics": metrics,
    }

    try:
        yield
    finally:
        # Cleanup
        await context7.close()
        await cache.close()


# ─── CREATE MCP SERVER ───────────────────────────────────────────


def create_server(config: TokenetteConfig | None = None) -> FastMCP:
    """
    Create and configure the Tokenette MCP server.

    Returns a fully configured FastMCP server with:
    - All tools registered
    - Optimization middleware
    - Lifespan management
    """
    if config is None:
        config = get_config()

    mcp = FastMCP(
        name=(config.server.name or "tokenette").lower(),
        instructions="""
Tokenette: The Ultimate AI Coding Enhancement MCP

I provide zero-loss token optimization, intelligent model routing, and quality amplification.

Key capabilities:
- 90-99% token reduction on file operations
- Smart model routing to minimize premium request usage
- Quality amplification for cheaper models
- Multi-layer caching (L1-L4) with 99.8% hit rate on repeated data
- Context7 integration for up-to-date library docs
- Interaction batching for multi-op workflows

Use `discover_tools` first to see available tools efficiently.
Use `route_task` to get optimal model recommendations.
Use `optimize_output` to compress any response before transmission.
        """.strip(),
        lifespan=lifespan,
    )

    def _record_metrics(
        tool_name: str,
        input_data: Any | None,
        output_data: Any | None,
        tokens_saved: int = 0,
        cache_hit: bool | None = None,
    ) -> None:
        metrics: MetricsTracker = mcp.state["metrics"]
        metrics.record_tool_call(
            tool_name,
            input_data=input_data,
            output_data=output_data,
            tokens_saved=tokens_saved,
            cache_hit=cache_hit,
        )

    def _tokens_saved_from_result(result: Any) -> int:
        if isinstance(result, dict):
            for key in ("tokens_saved", "total_tokens_saved"):
                if key in result and isinstance(result[key], int):
                    return result[key]
            tokens = result.get("tokens")
            if isinstance(tokens, dict):
                saved = tokens.get("saved")
                if isinstance(saved, int):
                    return saved
                original = tokens.get("original")
                minified = tokens.get("minified")
                if isinstance(original, int) and isinstance(minified, int):
                    return max(0, original - minified)
        return 0

    # ─── REGISTER CORE TOOLS ─────────────────────────────────────

    @mcp.tool()
    async def tokenette_discover_tools(
        category: str | None = None, ctx: Context | None = None
    ) -> dict[str, Any]:
        """
        Discover available tools efficiently (96% token savings).

        Returns compact tool list. Use get_tool_details for full schemas.

        Args:
            category: Filter by category (file, analysis, docs, meta)
        """
        result = await discover_tools(category, ctx)
        _record_metrics("tokenette_discover_tools", {"category": category}, result)
        return result

    @mcp.tool()
    async def tokenette_get_tool_details(
        tool_name: str, ctx: Context | None = None
    ) -> dict[str, Any]:
        """
        Get full schema for a specific tool.

        Only fetches schema when needed, saving tokens.
        """
        result = await get_tool_details(tool_name, ctx)
        _record_metrics("tokenette_get_tool_details", {"tool_name": tool_name}, result)
        return result

    @mcp.tool()
    async def tokenette_execute_tool(
        tool_name: str,
        arguments: dict[str, Any],
        cache_key: str | None = None,
        skip_cache: bool = False,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """
        Execute a tool dynamically via the meta-tool registry.

        Args:
            tool_name: Name of the tool to execute (use tokenette_discover_tools first)
            arguments: Arguments for the tool
            cache_key: Optional cache key
            skip_cache: Skip cache lookup
        """
        result = await execute_tool(tool_name, arguments, cache_key, skip_cache, ctx)
        _record_metrics(
            "tokenette_execute_tool",
            {"tool_name": tool_name, "cache_key": cache_key, "skip_cache": skip_cache},
            result,
        )
        return result

    if config.server.meta_tools_only:
        return mcp

    # ─── FILE OPERATION TOOLS ────────────────────────────────────

    @mcp.tool()
    async def tokenette_read_file(
        path: str,
        strategy: Literal["auto", "full", "partial", "summary", "ast"] = "auto",
        start_line: int | None = None,
        end_line: int | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """
        Read file with intelligent strategy selection.

        Strategies:
        - auto: Picks best strategy based on file size
        - full: Read entire file (small files only)
        - partial: Read specific line range
        - summary: Extract key structures (functions, classes)
        - ast: Return AST structure only (Python)

        Args:
            path: File path to read
            strategy: Reading strategy
            start_line: Start line for partial reads
            end_line: End line for partial reads
        """
        result = await read_file_smart(path, strategy, start_line, end_line, ctx)
        _record_metrics(
            "tokenette_read_file",
            {
                "path": path,
                "strategy": strategy,
                "start_line": start_line,
                "end_line": end_line,
            },
            result,
            tokens_saved=_tokens_saved_from_result(result),
        )
        return result

    @mcp.tool()
    async def tokenette_write_file(
        path: str,
        diff: str,
        ctx: Context | None = None,
        expected_hash: str | None = None,
    ) -> dict[str, Any]:
        """
        Write file using unified diff format (97% token savings).

        Instead of sending entire file content, send only the changes.

        Args:
            path: Target file path
            diff: Unified diff format changes
            expected_hash: Optional file hash to verify before applying
        """
        result = await write_file_diff(path, diff, ctx=ctx, expected_hash=expected_hash)
        _record_metrics(
            "tokenette_write_file",
            {"path": path, "diff": diff, "expected_hash": expected_hash},
            result,
            tokens_saved=_tokens_saved_from_result(result),
        )
        return result

    @mcp.tool()
    async def tokenette_search_code(
        query: str,
        directory: str = ".",
        file_pattern: str = "*.py",
        max_results: int = 20,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """
        Semantic code search across files.

        Finds relevant code based on meaning, not just text matching.

        Args:
            query: Search query (semantic)
            directory: Directory to search
            file_pattern: File glob pattern
            max_results: Maximum results to return
        """
        result = await search_code_semantic(query, directory, file_pattern, max_results, ctx)
        _record_metrics(
            "tokenette_search_code",
            {
                "query": query,
                "directory": directory,
                "file_pattern": file_pattern,
                "max_results": max_results,
            },
            result,
        )
        return result

    @mcp.tool()
    async def tokenette_get_structure(path: str, ctx: Context | None = None) -> dict[str, Any]:
        """
        Get file structure (AST summary).

        Returns functions, classes, and methods without code bodies.
        Much smaller than full file content.
        """
        result = await get_file_structure(path, ctx)
        _record_metrics("tokenette_get_structure", {"path": path}, result)
        return result

    @mcp.tool()
    async def tokenette_batch_read(paths: list[str], ctx: Context | None = None) -> dict[str, Any]:
        """
        Read multiple files in one request with deduplication.

        Automatically detects and references shared code (imports, utilities).
        Much more efficient than multiple read_file calls.
        """
        result = await batch_read_files(paths, ctx)
        _record_metrics(
            "tokenette_batch_read",
            {"paths": paths},
            result,
            tokens_saved=_tokens_saved_from_result(result),
        )
        return result

    @mcp.tool()
    async def tokenette_batch_ops(
        operations: list[dict[str, Any]], ctx: Context | None = None
    ) -> dict[str, Any]:
        """
        Execute a batch of operations in a single optimized payload.

        Supports operations:
        - read: {type:"read", path, strategy?, start_line?, end_line?}
        - write: {type:"write", path, diff? | content?}
        - search: {type:"search", query, directory?, file_pattern?, max_results?}
        - analyze: {type:"analyze", directory?, focus?}
        """
        batcher: InteractionBatcher = mcp.state["batcher"]
        result = await batcher.batch_file_operations(operations)
        _record_metrics(
            "tokenette_batch_ops",
            {"operations": operations},
            result,
            tokens_saved=_tokens_saved_from_result(result),
        )
        return result

    # ─── ANALYSIS TOOLS ──────────────────────────────────────────

    @mcp.tool()
    async def tokenette_analyze(
        path: str, checks: list[str] | None = None, ctx: Context | None = None
    ) -> dict[str, Any]:
        """
        Analyze code for patterns, complexity, and issues.

        Args:
            path: File or directory to analyze
            checks: Analysis checks (complexity, style, security)
        """
        result = await analyze_code(path, checks, ctx)
        _record_metrics("tokenette_analyze", {"path": path, "checks": checks}, result)
        return result

    @mcp.tool()
    async def tokenette_find_bugs(
        path: str,
        severity: Literal["all", "high", "medium", "low"] = "all",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """
        Find potential bugs and security issues.

        Args:
            path: File to scan
            severity: Filter by severity level
        """
        result = await find_bugs(path, severity, ctx)
        _record_metrics(
            "tokenette_find_bugs",
            {"path": path, "severity": severity},
            result,
        )
        return result

    @mcp.tool()
    async def tokenette_complexity(path: str, ctx: Context | None = None) -> dict[str, Any]:
        """
        Calculate cyclomatic complexity metrics.

        Returns complexity score, LOC, nesting depth, and maintainability index.
        """
        result = await get_complexity(path, ctx)
        _record_metrics("tokenette_complexity", {"path": path}, result)
        return result

    # ─── CONTEXT7 / DOCUMENTATION TOOLS ──────────────────────────

    @mcp.tool()
    async def tokenette_resolve_lib(name: str, ctx: Context | None = None) -> dict[str, Any]:
        """
        Resolve library name to Context7 ID.

        Examples: "react" → "/facebook/react"
        """
        result = await resolve_library(name, ctx)
        _record_metrics("tokenette_resolve_lib", {"name": name}, result)
        return result

    @mcp.tool()
    async def tokenette_get_docs(
        library: str,
        topic: str | None = None,
        mode: Literal["code", "info"] = "code",
        page: int = 1,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """
        Fetch library documentation with caching.

        Uses Context7 for up-to-date docs. Results are cached.

        Args:
            library: Library name or Context7 ID
            topic: Focus topic (e.g., "hooks", "middleware")
            mode: "code" for API refs, "info" for guides
            page: Page number (1-10)
        """
        result = await fetch_library_docs(library, topic, mode, page, ctx)
        _record_metrics(
            "tokenette_get_docs",
            {"library": library, "topic": topic, "mode": mode, "page": page},
            result,
            tokens_saved=_tokens_saved_from_result(result),
        )
        return result

    @mcp.tool()
    async def tokenette_search_docs(
        query: str, library: str | None = None, ctx: Context | None = None
    ) -> dict[str, Any]:
        """
        Search documentation across libraries.

        Args:
            query: Search query
            library: Optional library to search within
        """
        result = await search_library_docs(query, library, ctx)
        _record_metrics(
            "tokenette_search_docs",
            {"query": query, "library": library},
            result,
        )
        return result

    # ─── OPTIMIZATION TOOLS ──────────────────────────────────────

    @mcp.tool()
    async def tokenette_optimize(
        data: Any,
        content_type: Literal["auto", "json", "code", "toon"] = "auto",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """
        Optimize any data for minimal token usage.

        Applies: Cache → Minification → Deduplication → Compression

        Args:
            data: Data to optimize
            content_type: Content type hint
        """
        optimizer: OptimizationPipeline = mcp.state["optimizer"]
        result = await optimizer.optimize(data, content_type=content_type)

        response = result.to_response()
        _record_metrics(
            "tokenette_optimize",
            {"content_type": content_type},
            response,
            tokens_saved=result.tokens_saved,
            cache_hit=result.is_cache_hit,
        )
        return response

    @mcp.tool()
    async def tokenette_route_task(
        request: str, affected_files: int = 1, ctx: Context | None = None
    ) -> dict[str, Any]:
        """
        Get optimal model recommendation for a task.

        Analyzes task complexity and returns:
        - Recommended model
        - Cost multiplier
        - Quality boosters to apply
        - Fallback chain

        Args:
            request: Description of the task
            affected_files: Number of files involved
        """
        router: TaskRouter = mcp.state["router"]
        decision = router.route(request, {"affected_files": affected_files})
        result = {
            "model": decision.model,
            "complexity": decision.complexity.name,
            "category": decision.category.value,
            "multiplier": decision.multiplier,
            "effective_multiplier": decision.effective_multiplier,
            "quality_boosters": decision.quality_boosters,
            "fallback_chain": decision.fallback_chain,
            "reasoning": decision.reasoning,
        }
        metrics: MetricsTracker = mcp.state["metrics"]
        metrics.record_model_use(decision.model, decision.multiplier)
        _record_metrics(
            "tokenette_route_task",
            {"request": request, "affected_files": affected_files},
            result,
        )
        return result

    @mcp.tool()
    async def tokenette_amplify(
        prompt: str,
        category: str | None = None,
        boosters: list[str] | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """
        Amplify prompt quality for cheaper models.

        Adds expert framing, chain-of-thought, and examples
        to make cheaper models produce premium output.

        Args:
            prompt: Original prompt
            category: Task category (generation, refactor, etc.)
            boosters: Specific boosters to apply
        """
        amplifier: QualityAmplifier = mcp.state["amplifier"]

        # Detect category if not provided
        if category is None:
            router: TaskRouter = mcp.state["router"]
            cat = router._detect_category(prompt)
            category = cat.value

        # Normalize category to TaskCategory
        from tokenette.core.router import TaskCategory

        try:
            category_enum = TaskCategory(category)
        except Exception:
            category_enum = TaskCategory.GENERATION

        # Get boosters if not provided
        if boosters is None:
            boosters = ["expert_role_framing", "chain_of_thought_injection"]

        result = amplifier.amplify(prompt, boosters, category_enum, {})

        response = {
            "original_length": len(prompt),
            "amplified_length": result.amplified_length,
            "boosters_applied": result.boosters_applied,
            "enhanced_prompt": result.prompt,
            "quality_boost": amplifier.estimate_quality_improvement(
                result.boosters_applied, base_quality=0.85
            ),
        }
        _record_metrics(
            "tokenette_amplify",
            {"category": category_enum.value, "boosters": boosters},
            response,
        )
        return response

    @mcp.tool()
    async def tokenette_metrics(ctx: Context | None = None) -> dict[str, Any]:
        """
        Get current session metrics.

        Returns token savings, cache hits, and budget usage.
        """
        cache: MultiLayerCache = mcp.state["cache"]
        router: TaskRouter = mcp.state["router"]
        metrics: MetricsTracker = mcp.state["metrics"]
        cache_stats = cache.get_stats()
        budget = router.budget_tracker

        result = {
            "session": metrics.snapshot(),
            "cache": {
                "l1_entries": cache_stats.get("l1_entries", 0),
                "l2_entries": cache_stats.get("l2_entries", 0),
                "hit_rate": cache_stats.get("hit_rate", 0),
            },
            "budget": {
                "used": budget.used,
                "remaining": budget.remaining,
                "usage_pct": budget.usage_pct,
            },
        }
        _record_metrics("tokenette_metrics", None, result)
        return result

    # ─── GIT TOOLS ───────────────────────────────────────────────

    @mcp.tool()
    async def tokenette_git_diff(
        path: str = ".",
        staged: bool = False,
        context_lines: int = 3,
        files: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get optimized git diff with smart compression.

        Removes redundant headers, compresses output.

        Args:
            path: Repository path
            staged: Show staged changes only
            context_lines: Lines of context (less = smaller)
            files: Specific files to diff
        """
        from .tools.git_ops import get_git_diff

        result = await get_git_diff(path, staged, context_lines, True, files)
        response = {
            "files_changed": result.files_changed,
            "insertions": result.insertions,
            "deletions": result.deletions,
            "diff": result.diff,
            "summary": result.summary,
            "tokens_saved": result.tokens_saved,
        }
        _record_metrics(
            "tokenette_git_diff",
            {"path": path, "staged": staged, "context_lines": context_lines, "files": files},
            response,
            tokens_saved=result.tokens_saved,
        )
        return response

    @mcp.tool()
    async def tokenette_git_status(path: str = ".") -> dict[str, Any]:
        """
        Get optimized git status.

        Returns compact status with file counts.

        Args:
            path: Repository path
        """
        from .tools.git_ops import get_git_status

        result = await get_git_status(path)
        _record_metrics("tokenette_git_status", {"path": path}, result)
        return result

    @mcp.tool()
    async def tokenette_git_history(
        path: str = ".",
        max_commits: int = 20,
        file_path: str | None = None,
        author: str | None = None,
    ) -> dict[str, Any]:
        """
        Get compressed commit history.

        Args:
            path: Repository path
            max_commits: Maximum commits to return
            file_path: Filter by file
            author: Filter by author
        """
        from .tools.git_ops import get_git_history

        result = await get_git_history(path, max_commits, file_path, author)
        response = {
            "commits": result.commits,
            "total": result.total_commits,
            "date_range": result.date_range,
            "summary": result.summary,
        }
        _record_metrics(
            "tokenette_git_history",
            {
                "path": path,
                "max_commits": max_commits,
                "file_path": file_path,
                "author": author,
            },
            response,
        )
        return response

    @mcp.tool()
    async def tokenette_git_blame(
        file_path: str, start_line: int | None = None, end_line: int | None = None
    ) -> dict[str, Any]:
        """
        Get optimized git blame (grouped by author).

        Args:
            file_path: Path to file
            start_line: Starting line (1-indexed)
            end_line: Ending line (inclusive)
        """
        from .tools.git_ops import get_git_blame

        result = await get_git_blame(file_path, start_line, end_line)
        response = {
            "file": result.file,
            "lines": result.lines,
            "authors": result.authors,
            "summary": result.summary,
        }
        _record_metrics(
            "tokenette_git_blame",
            {"file_path": file_path, "start_line": start_line, "end_line": end_line},
            response,
        )
        return response

    # ─── PROMPT TOOLS ────────────────────────────────────────────

    @mcp.tool()
    async def tokenette_list_prompts(category: str | None = None) -> list[dict[str, str]]:
        """
        List available prompt templates.

        Categories: code_generation, refactoring, debugging,
                   testing, documentation, review, architecture, optimization

        Args:
            category: Filter by category
        """
        from .tools.prompts import list_templates

        result = list_templates(category)
        _record_metrics("tokenette_list_prompts", {"category": category}, result)
        return result

    @mcp.tool()
    async def tokenette_build_prompt(
        template_name: str, variables: dict[str, str], quality_boosters: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Build an optimized prompt from a template.

        Templates: function, class, api_endpoint, refactor_function,
                  find_bug, unit_tests, code_review, security_audit, etc.

        Args:
            template_name: Name of the template
            variables: Variable values to fill in
            quality_boosters: Optional boosters (expert_role_framing, chain_of_thought_injection, etc.)
        """
        from .tools.prompts import build_prompt

        result = build_prompt(template_name, variables, quality_boosters)
        response = {
            "prompt": result.prompt,
            "template": result.template_name,
            "token_count": result.token_count,
            "boosters_applied": result.quality_boosters,
        }
        _record_metrics(
            "tokenette_build_prompt",
            {"template_name": template_name, "variables": variables},
            response,
        )
        return response

    # ─── TOKEN & BUDGET TOOLS ────────────────────────────────────

    @mcp.tool()
    async def tokenette_count_tokens(
        text: str, language: str | None = None, detailed: bool = False
    ) -> dict[str, Any]:
        """
        Estimate token count for text/code.

        Args:
            text: Text or code to count
            language: Programming language for better accuracy
            detailed: Include detailed breakdown
        """
        from .tools.tokens import count_tokens

        result = count_tokens(text, language, detailed)
        response = {
            "text_length": result.text_length,
            "estimated_tokens": result.estimated_tokens,
            "breakdown": result.breakdown,
        }
        _record_metrics(
            "tokenette_count_tokens",
            {"language": language, "detailed": detailed},
            response,
        )
        return response

    @mcp.tool()
    async def tokenette_estimate_cost(
        model: str, input_text: str, output_estimate: int = 500
    ) -> dict[str, Any]:
        """
        Estimate cost of a model interaction.

        Args:
            model: Model name (gpt-4.1, claude-sonnet-4, etc.)
            input_text: Input text or prompt
            output_estimate: Estimated output tokens
        """
        from .tools.tokens import estimate_cost

        result = estimate_cost(model, input_text, output_estimate)
        response = {
            "model": result.model,
            "input_tokens": result.input_tokens,
            "output_estimate": result.output_tokens_estimate,
            "multiplier": result.multiplier,
            "premium_cost": result.premium_requests_cost,
            "breakdown": result.breakdown,
        }
        _record_metrics(
            "tokenette_estimate_cost",
            {"model": model, "output_estimate": output_estimate},
            response,
        )
        return response

    @mcp.tool()
    async def tokenette_compare_models(
        input_text: str, output_estimate: int = 500
    ) -> list[dict[str, Any]]:
        """
        Compare costs across all available models.

        Helps choose the right model for a task.

        Args:
            input_text: Input text to estimate for
            output_estimate: Estimated output tokens
        """
        from .tools.tokens import compare_model_costs

        result = compare_model_costs(input_text, output_estimate)
        _record_metrics(
            "tokenette_compare_models",
            {"output_estimate": output_estimate},
            result,
        )
        return result

    @mcp.tool()
    async def tokenette_budget_status() -> dict[str, Any]:
        """
        Get current budget status with recommendations.

        Shows usage, remaining budget, and optimization tips.
        """
        from .tools.tokens import get_budget_tracker

        tracker = get_budget_tracker()
        status = tracker.get_status()
        response = {
            "monthly_limit": status.monthly_limit,
            "used": status.used,
            "remaining": status.remaining,
            "percentage": status.percentage_used,
            "days_remaining": status.days_remaining,
            "daily_budget": status.daily_budget,
            "on_track": status.on_track,
            "recommendations": status.recommendations,
        }
        _record_metrics("tokenette_budget_status", None, response)
        return response

    # ─── WORKSPACE TOOLS ─────────────────────────────────────────

    @mcp.tool()
    async def tokenette_project_info(path: str = ".") -> dict[str, Any]:
        """
        Detect project type and gather information.

        Returns project name, type, framework, dependencies, etc.

        Args:
            path: Path to project root
        """
        from .tools.workspace import detect_project_type

        result = await detect_project_type(path)
        response = {
            "name": result.name,
            "type": result.type,
            "language": result.language,
            "framework": result.framework,
            "package_manager": result.package_manager,
            "entry_points": result.entry_points,
            "dependencies_count": len(result.dependencies),
            "scripts": result.scripts,
        }
        _record_metrics("tokenette_project_info", {"path": path}, response)
        return response

    @mcp.tool()
    async def tokenette_workspace_summary(path: str = ".", max_depth: int = 4) -> dict[str, Any]:
        """
        Generate comprehensive workspace summary.

        Token-optimized overview of the entire workspace.

        Args:
            path: Path to workspace root
            max_depth: Maximum directory depth
        """
        from .tools.workspace import get_workspace_summary

        result = await get_workspace_summary(path, max_depth)
        response = {
            "total_files": result.total_files,
            "total_lines": result.total_lines,
            "languages": result.languages,
            "key_files": result.key_files,
            "entry_points": result.entry_points,
            "token_estimate": result.token_estimate,
            "summary": result.summary_text,
        }
        _record_metrics(
            "tokenette_workspace_summary",
            {"path": path, "max_depth": max_depth},
            response,
        )
        return response

    @mcp.tool()
    async def tokenette_code_health(path: str = ".") -> dict[str, Any]:
        """
        Analyze code health metrics.

        Returns quality indicators and recommendations.

        Args:
            path: Path to project root
        """
        from .tools.workspace import get_code_health

        result = await get_code_health(path)
        response = {
            "files_analyzed": result.files_analyzed,
            "total_lines": result.total_lines,
            "code_lines": result.code_lines,
            "comment_ratio": result.comment_ratio,
            "avg_file_size": result.avg_file_size,
            "largest_files": result.largest_files[:5],
            "recommendations": result.recommendations,
        }
        _record_metrics("tokenette_code_health", {"path": path}, response)
        return response

    @mcp.tool()
    async def tokenette_smart_context(
        path: str, query: str, max_tokens: int = 4000
    ) -> dict[str, Any]:
        """
        Extract relevant context for a query.

        Intelligently selects files and sections most relevant
        to the task, optimized for token budget.

        Args:
            path: Path to project root
            query: User's query or task description
            max_tokens: Maximum tokens to include
        """
        from .tools.workspace import extract_smart_context

        result = await extract_smart_context(path, query, max_tokens)
        _record_metrics(
            "tokenette_smart_context",
            {"path": path, "query": query, "max_tokens": max_tokens},
            result,
        )
        return result

    @mcp.tool()
    async def tokenette_dependencies(path: str = ".") -> dict[str, Any]:
        """
        Analyze project dependencies.

        Args:
            path: Path to project root
        """
        from .tools.workspace import analyze_dependencies

        result = await analyze_dependencies(path)
        response = {
            "direct": result.direct,
            "dev": result.dev,
            "total": result.total_count,
            "tree": result.dependency_tree,
        }
        _record_metrics("tokenette_dependencies", {"path": path}, response)
        return response

    # ─── REGISTER RESOURCES ──────────────────────────────────────

    @mcp.resource("tokenette://config")
    async def get_current_config() -> str:
        """Current Tokenette configuration."""
        config = get_config()
        return config.model_dump_json(indent=2)

    @mcp.resource("tokenette://models")
    async def get_model_profiles() -> str:
        """Available model profiles with costs."""
        import json

        from .core.router import MODEL_PROFILES

        return json.dumps(MODEL_PROFILES, indent=2)

    @mcp.resource("tokenette://cache/stats")
    async def get_cache_stats() -> str:
        """Current cache statistics."""
        import json

        cache: MultiLayerCache = mcp.state.get("cache")
        if cache:
            return json.dumps(cache.get_stats(), indent=2)
        return "{}"

    return mcp


# ─── DEFAULT SERVER INSTANCE ─────────────────────────────────────

# Create default server (used by CLI and direct imports)
mcp = create_server()

# Export for uvicorn / fastmcp run
app = mcp


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the MCP server."""
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
