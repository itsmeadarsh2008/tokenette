# Changelog

All notable changes to Tokenette will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2026-02-07

### Added
- **Interaction batching engine** with `tokenette_batch_ops` for multi-op payloads
- **Metrics tracker** with optional persistence and CLI visibility
- **Streaming reads** for huge files
- **Optional vector similarity** for semantic cache/search (when `vector` extras installed)

### Fixed
- Cache stats/close methods and router budget alias mismatches
- Server optimization result formatting and tool metrics updates
- Meta tool discovery output now aligns with `tokenette_` tool names

## [2.0.0] - 2026-02-01

### Added

#### Core Features
- **Intelligent Task Router** - Routes tasks to optimal models based on complexity, quality thresholds, and budget
- **Quality Amplifier** - Makes cheaper models produce premium-quality output with expert framing and chain-of-thought
- **Multi-Layer Cache** (L1-L4) - 99.8% hit rate on repeated data with semantic similarity matching
- **Optimization Pipeline** - Full token optimization with minification, deduplication, and compression

#### Model Selection (Feb 2026 Rankings)
- **Quality-first selection** for COMPLEX/EXPERT tasks
- **Cost-first selection** for TRIVIAL/SIMPLE tasks
- **Balanced value scoring** for MODERATE tasks
- Support for 11 models across 5 tiers (FREE → AVOID)

#### MCP Tools (33 total)

**Meta Tools**
- `tokenette_discover_tools` - Discover available tools (96% token savings)
- `tokenette_get_tool_details` - Get full tool schema
- `tokenette_execute_tool` - Execute any tool dynamically

**File Tools**
- `tokenette_read_file` - Smart file reading with caching
- `tokenette_batch_read` - Batch multiple file reads
- `tokenette_write_file` - Write files with diff output
- `tokenette_search_code` - Semantic code search
- `tokenette_file_structure` - Get directory structure

**Analysis Tools**
- `tokenette_analyze_code` - Comprehensive code analysis
- `tokenette_find_bugs` - Bug detection with explanations
- `tokenette_get_complexity` - Complexity metrics

**Routing Tools**
- `tokenette_route_task` - Get optimal model recommendation
- `tokenette_amplify_prompt` - Enhance prompts for quality
- `tokenette_optimize_output` - Compress output for transmission

**Documentation Tools**
- `tokenette_resolve_library` - Resolve library IDs via Context7
- `tokenette_fetch_docs` - Fetch library documentation
- `tokenette_search_docs` - Search documentation

**Git Tools**
- `tokenette_git_diff` - Optimized git diff with compression
- `tokenette_git_status` - Compact git status
- `tokenette_git_history` - Compressed commit history
- `tokenette_git_blame` - Optimized blame grouped by author

**Prompt Tools**
- `tokenette_list_prompts` - List 16 prompt templates
- `tokenette_build_prompt` - Build optimized prompts

**Token & Budget Tools**
- `tokenette_count_tokens` - Estimate token counts
- `tokenette_estimate_cost` - Estimate model costs
- `tokenette_compare_models` - Compare all model costs
- `tokenette_budget_status` - Budget status with recommendations

**Workspace Tools**
- `tokenette_project_info` - Detect project type/framework
- `tokenette_workspace_summary` - Token-optimized workspace overview
- `tokenette_code_health` - Code quality metrics
- `tokenette_smart_context` - Extract relevant context for queries
- `tokenette_dependencies` - Analyze project dependencies

#### Prompt Templates (16 templates)
- Code generation: `function`, `class`, `api_endpoint`
- Refactoring: `refactor_function`, `extract_method`
- Debugging: `find_bug`, `trace_execution`
- Testing: `unit_tests`, `test_cases`
- Documentation: `docstring`, `readme_section`
- Review: `code_review`, `security_audit`
- Architecture: `design_pattern`, `system_design`
- Optimization: `optimize_performance`, `reduce_complexity`

### Technical
- Built with FastMCP 2.14.4
- Python 3.13+ support
- Pydantic 2.x for configuration
- Async-first architecture
- Comprehensive test suite (22 tests)

## [1.0.0] - 2026-01-15

### Added
- Initial release with basic token optimization
- Simple model routing
- File operations

---

[2.0.1]: https://github.com/itsmeadarsh2008/tokenette/releases/tag/v2.0.1
[2.0.0]: https://github.com/itsmeadarsh2008/tokenette/releases/tag/v2.0.0
[1.0.0]: https://github.com/itsmeadarsh2008/tokenette/releases/tag/v1.0.0
