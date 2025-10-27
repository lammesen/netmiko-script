# RFC-0001: Modular Architecture Redesign

## Metadata
- **RFC Number**: 0001
- **Title**: Modular Architecture Redesign
- **Author**: Repository Audit Process
- **Status**: Draft
- **Created**: 2025-10-27
- **Updated**: 2025-10-27
- **Related Items**: ARCH-001, TEST-001
- **Priority**: P0 (Critical)

---

## Executive Summary

This RFC proposes a **complete rewrite** of the current monolithic 2,837-line `netmiko_collector.py` into a modern, modular architecture with 8-10 focused modules under a `/src/netmiko_collector/` structure. This change will improve testability, maintainability, and extensibility with a clean-slate approach.

**Key Benefits**:
- Test coverage improvement from 20% to >80%
- Each module <500 lines (down from 2,837)
- Clear separation of concerns
- Easier unit testing per module
- Better code reusability
- Simplified onboarding for contributors
- Modern Python best practices (type hints, dataclasses, protocols)
- Clean architecture without legacy constraints

**Migration Strategy**: Complete rewrite approach approved by maintainer. No backward compatibility constraints. Focus on best practices and optimal design.

---

## Problem Statement

### Current State
The application consists of a single 2,837-line file (`netmiko_collector.py`) containing:
- 39 functions
- 0 classes
- Mixed responsibilities (CLI, config, SSH, I/O, formatting)
- 20% test coverage (893/1117 statements uncovered)
- High cyclomatic complexity in 5 functions (>15)

### Issues with Current Architecture

1. **Low Testability**
   - Monolithic structure makes unit testing difficult
   - Functions tightly coupled to file I/O and SSH operations
   - Mock setup is complex and brittle
   - Coverage stuck at 20%

2. **High Maintenance Burden**
   - 2,837 lines is overwhelming for new contributors
   - Changes in one area risk breaking unrelated functionality
   - Difficult to locate specific functionality
   - Code review is time-consuming

3. **Limited Extensibility**
   - Adding new output formats requires editing large file
   - New features increase file size further
   - Duplicate code patterns emerge
   - Refactoring is risky without tests

4. **Complexity Hotspots**
   - `connect_and_execute()`: 280 lines, complexity ~25
   - `process_devices_parallel()`: 180 lines, complexity ~20
   - `show_settings_menu()`: 130 lines, complexity ~18
   - `save_to_html()`: 200 lines, complexity ~15
   - `run_collection()`: 150 lines, complexity ~15

### Why This Matters
- Current architecture blocks increasing test coverage (TEST-001 depends on this)
- Future features (dry-run, filtering, templating) are harder to add
- Contributors struggle with large file size
- Code quality improvements are risky without safety net

---

## Proposed Solution

### Target Architecture

```
src/
└── netmiko_collector/
    ├── __init__.py              # Package initialization, version export
    ├── __main__.py              # Entry point for -m execution
    ├── cli.py                   # Typer CLI commands (~300 lines)
    ├── config.py                # Configuration management (~150 lines)
    ├── models.py                # Data models (Device, Command, Result) (~100 lines)
    ├── devices.py               # Device loading and validation (~150 lines)
    ├── commands.py              # Command loading and management (~150 lines)
    ├── ssh.py                   # SSH connection and execution (~300 lines)
    ├── executor.py              # Parallel execution orchestration (~250 lines)
    ├── formatters/              # Output formatters package
    │   ├── __init__.py          # Formatter registration
    │   ├── base.py              # Abstract formatter interface (~50 lines)
    │   ├── csv_formatter.py     # CSV output (~100 lines)
    │   ├── json_formatter.py    # JSON output (~100 lines)
    │   ├── markdown_formatter.py # Markdown output (~100 lines)
    │   ├── html_formatter.py    # HTML output (~200 lines)
    │   └── excel_formatter.py   # Excel output (~150 lines)
    ├── ui.py                    # Rich UI utilities (~200 lines)
    └── utils.py                 # General utilities (~150 lines)
```

**Total Estimated Lines**: ~2,400 (down from 2,837 with better organization)

### Module Responsibilities

#### 1. `cli.py` - Command Line Interface
**Responsibility**: Typer command definitions and argument parsing

**Dependencies**: config, devices, commands, executor, formatters  
**Exports**: `app` (Typer application)

#### 2. `config.py` - Configuration Management
**Responsibility**: Load, save, and manage application configuration

**Dependencies**: None (pure Python stdlib)  
**Exports**: `Config` class

#### 3. `models.py` - Data Models
**Responsibility**: Define data structures for type safety

**Dependencies**: None (stdlib only)  
**Exports**: `Device`, `Command`, `Result` classes

#### 4. `devices.py` - Device Management
**Responsibility**: Load and validate device inventory from CSV

**Dependencies**: models, utils  
**Exports**: `load_devices()`, `validate_device()`

#### 5. `commands.py` - Command Management
**Responsibility**: Load and manage command lists

**Dependencies**: models  
**Exports**: `load_commands()`, `get_commands_for_device_type()`, `DEVICE_COMMANDS`

#### 6. `ssh.py` - SSH Operations
**Responsibility**: SSH connection, command execution, retry logic

**Dependencies**: netmiko, tenacity, models  
**Exports**: `SSHConnection` class

#### 7. `executor.py` - Parallel Execution
**Responsibility**: Orchestrate parallel device processing

**Dependencies**: models, ssh, concurrent.futures, rich  
**Exports**: `ParallelExecutor` class

#### 8. `formatters/` - Output Formatters
**Responsibility**: Format and save results in various formats

**Dependencies**: models  
**Exports**: `OutputFormatter`, `get_formatter()`, individual formatters

#### 9. `ui.py` - UI Utilities
**Responsibility**: Rich console utilities and interactive elements

**Dependencies**: rich  
**Exports**: UI utility functions

#### 10. `utils.py` - General Utilities
**Responsibility**: Shared utility functions

**Dependencies**: None (stdlib only)  
**Exports**: Utility functions

---

### Dependency Graph

```
cli.py
  ├─► config.py
  ├─► devices.py
  │     ├─► models.py
  │     └─► utils.py
  ├─► commands.py
  │     └─► models.py
  ├─► executor.py
  │     ├─► models.py
  │     ├─► ssh.py
  │     │     ├─► models.py
  │     │     └─► netmiko (external)
  │     └─► rich (external)
  ├─► formatters/
  │     └─► models.py
  └─► ui.py
        └─► rich (external)
```

**Key Design Principles**:
- **Low coupling**: Modules depend on models, not each other
- **High cohesion**: Related functionality grouped together
- **Dependency injection**: Pass dependencies explicitly
- **Single responsibility**: Each module has one clear purpose

---

## Migration Strategy - Complete Rewrite Approach

**Note**: Maintainer has approved a complete codebase rework with no backward compatibility requirements. This enables us to use modern best practices and optimal design patterns without legacy constraints.

### Phase 1: Foundation & Architecture (Week 1-2)
**Goal**: Establish new codebase structure with modern patterns

1. **Create New Module Structure**
   - Create `/src/netmiko_collector/` package
   - Set up modern Python packaging (pyproject.toml)
   - Configure strict type checking (mypy --strict)
   - Set up comprehensive test structure in `/tests`

2. **Define Core Models & Protocols**
   - Create modern dataclasses with validation (pydantic)
   - Define Protocol interfaces for extensibility
   - Implement proper error hierarchy
   - Add comprehensive type hints

3. **Establish Testing Framework**
   - Set up pytest with fixtures
   - Configure coverage reporting (>80% target)
   - Create mock factories for SSH/devices
   - Set up CI with strict quality gates

### Phase 2: Core Modules (Week 3-4)
**Goal**: Implement foundation modules with best practices

1. **Implement `models.py`**
   - Device, Command, Result dataclasses
   - Validation using pydantic or dataclasses
   - Immutable where appropriate
   - Comprehensive unit tests

2. **Implement `config.py`**
   - Type-safe configuration management
   - Environment variable support
   - Validation and defaults
   - JSON/YAML support

3. **Implement `utils.py`**
   - Pure functions for common operations
   - Full type coverage
   - Comprehensive tests
   - No side effects

### Phase 3: Business Logic (Week 4-6)
**Goal**: Implement core functionality with clean architecture

1. **Implement `devices.py` & `commands.py`**
   - CSV parsing with proper error handling
   - Data validation and transformation
   - Device grouping and filtering
   - Full test coverage

2. **Implement `ssh.py`**
   - Modern SSH connection handling
   - Context managers for resource cleanup
   - Retry logic with exponential backoff
   - Comprehensive error handling
   - Extensive mocking tests

3. **Implement `executor.py`**
   - ThreadPoolExecutor/ProcessPoolExecutor orchestration
   - Progress tracking with Rich
   - Error aggregation
   - Cancellation support

### Phase 4: Output & UI (Week 6-7)
**Goal**: Implement formatters and user interface

1. **Implement Formatter Framework**
   - Protocol-based formatter interface
   - Plugin system for extensibility
   - Factory pattern for formatter selection
   - Tests for each formatter

2. **Implement `ui.py`**
   - Rich-based progress and output
   - Interactive menus
   - Error display
   - Logging integration

### Phase 5: CLI & Integration (Week 7-8)
**Goal**: Wire everything together with modern CLI

1. **Implement `cli.py`**
   - Typer-based command structure
   - Subcommands for different operations
   - Rich help and error messages
   - Shell completion support

2. **Create Entry Points**
   - `__main__.py` for module execution
   - Console script in pyproject.toml
   - Proper signal handling
   - Graceful shutdown

### Phase 6: Testing & Documentation (Week 8-10)
**Goal**: Achieve production-ready quality

1. **Comprehensive Testing**
   - Unit tests for all modules (>80% coverage)
   - Integration tests with mocked SSH
   - End-to-end tests with fixtures
   - Performance tests

2. **Documentation**
   - API documentation with sphinx
   - User guide with examples
   - Architecture documentation
   - Contributing guide

3. **Quality Assurance**
   - Fix all mypy errors (--strict mode)
   - Security scan (bandit, safety)
   - Performance profiling
   - Code review

---

## Compatibility & Migration Notes

### No Backward Compatibility Requirements
**Maintainer Decision**: Complete rework approved with no backward compatibility constraints.

**What This Means**:
- Free to redesign CLI interface for better UX
- Can improve file formats (e.g., YAML for config)
- Can modernize output formats
- Can break existing scripts/workflows
- Can change default behaviors

**Recommended Approach**:
- Keep CLI intuitive and familiar where it makes sense
- Improve error messages and help text
- Add better validation and feedback
- Consider migration tooling if format changes significantly

### Version Bump
This rewrite will be released as **v3.0.0** (major version bump) to signal breaking changes.

### For Developers/Contributors
**Changes**: Import paths updated

**Before**:
```python
from netmiko_collector import load_devices, load_commands
```

**After**:
```python
from netmiko_collector.devices import load_devices
from netmiko_collector.commands import load_commands
```

**Migration Support**:
- Keep compatibility shims in `__init__.py` for one release
- Add deprecation warnings
- Provide migration script
- Update all examples

---

## Risk Assessment & Mitigation

### High Risks 🔴

1. **Regression Bugs**
   - **Risk**: Behavior changes during rewrite
   - **Likelihood**: MEDIUM-HIGH (complete rewrite)
   - **Impact**: HIGH (production impact)
   - **Mitigation**:
     - Build comprehensive test suite first (>80% coverage)
     - Add integration tests with real scenarios
     - Beta testing period with maintainer
     - Extensive manual testing

2. **Performance Degradation**
   - **Risk**: New architecture slower than original
   - **Likelihood**: LOW (module imports are fast)
   - **Impact**: MEDIUM (user experience)
   - **Mitigation**:
     - Benchmark before/after
     - Performance tests in CI
     - Profile hot paths
     - Optimize as needed

3. **Incomplete Feature Parity**
   - **Risk**: Missing functionality from original
   - **Likelihood**: MEDIUM (easy to miss edge cases)
   - **Impact**: HIGH (missing features)
   - **Mitigation**:
     - Comprehensive feature inventory
     - Checklist of all CLI commands and options
     - Test all output formats
     - Review with maintainer

### Medium Risks 🟡

4. **Import Cycles**
   - **Risk**: Circular dependencies in modules
   - **Likelihood**: MEDIUM (complex relationships)
   - **Impact**: MEDIUM (import errors)
   - **Mitigation**:
     - Careful dependency planning
     - Models as shared foundation
     - Dependency injection pattern
     - Protocol-based interfaces

5. **Over-Engineering**
   - **Risk**: Too much abstraction, complexity
   - **Likelihood**: MEDIUM (temptation with rewrite)
   - **Impact**: MEDIUM (maintenance burden)
   - **Mitigation**:
     - Keep it simple (YAGNI principle)
     - Favor composition over inheritance
     - Pragmatic abstractions only
     - Regular code review

### Low Risks 🟢

6. **Documentation Lag**
   - **Risk**: Docs not updated in time
   - **Likelihood**: LOW (planned in phases)
   - **Impact**: LOW (temporary confusion)
   - **Mitigation**:
     - Update docs alongside code
     - Automated doc generation (sphinx)
     - Examples in docstrings

---

## Testing Strategy

### Unit Tests (Target: >80% coverage)

**Per Module**:
```
tests/
├── unit/
│   ├── test_config.py           # Config class tests
│   ├── test_models.py           # Dataclass validation tests
│   ├── test_devices.py          # CSV parsing tests
│   ├── test_commands.py         # Command loading tests
│   ├── test_ssh.py              # SSH logic tests (mocked)
│   ├── test_executor.py         # Executor tests (mocked)
│   ├── test_formatters.py       # All formatter tests
│   ├── test_ui.py               # UI utility tests
│   └── test_utils.py            # Utility function tests
```

**Mock Strategy**:
- Mock file I/O with `tempfile`
- Mock SSH connections with `unittest.mock`
- Mock external libraries (netmiko, rich)
- Use fixtures for common test data

### Integration Tests

```
tests/
├── integration/
│   ├── test_device_loading.py   # CSV to Device objects
│   ├── test_ssh_execution.py    # SSH flow (mocked at Netmiko level)
│   ├── test_parallel_execution.py # Executor with multiple devices
│   └── test_end_to_end.py       # Full CLI workflow
```

### Regression Tests

- All existing tests must continue passing
- CLI output must match byte-for-byte
- Performance must not regress >10%

---

## Success Criteria

### Must Have (Mandatory)
- ✅ All core functionality working correctly
- ✅ Test coverage >80%
- ✅ All modules <500 lines
- ✅ No circular dependencies
- ✅ Documentation complete
- ✅ Zero regressions in core features
- ✅ CLI intuitive and user-friendly
- ✅ All output formats working

### Should Have (Important)
- ✅ Performance within 10% of baseline (or better)
- ✅ Type hints on all public functions (mypy --strict)
- ✅ Docstrings on all modules/functions
- ✅ CI gates enforce coverage and quality
- ✅ Comprehensive examples
- ✅ Clear error messages
- ✅ Modern Python best practices

### Nice to Have (Optional)
- Plugin system for formatters (future - P2)
- API for programmatic use (future - P2)
- Async SSH option (future - P3)
- Web dashboard integration (future - P3)

---

## Timeline & Resources

### Estimated Duration
- **Total**: 8-10 weeks
- **Phases**: 6 phases (foundation through QA)
- **Effort**: ~50-60 story points

### Resource Requirements
- **1 Senior Engineer**: Architecture design, core modules, SSH logic
- **OR Focused Development**: Maintainer-driven rewrite
- **Testing**: Comprehensive test suite development

### Milestones
1. **Week 2**: Foundation complete, models and tests established
2. **Week 4**: Core modules implemented with >50% coverage
3. **Week 6**: Business logic complete, formatters working
4. **Week 8**: CLI integrated, all features working
5. **Week 10**: Testing complete (>80% coverage), docs finalized, v3.0.0 release

---

## Alternatives Considered

### Alternative 1: Gradual Refactoring
**Approach**: Extract modules from existing file over time

**Decision**: Rejected - Maintainer approved complete rewrite for cleaner result

### Alternative 2: Keep Monolithic, Add Classes
**Approach**: Convert to OOP within single file

**Decision**: Rejected - Doesn't address core issues (file size, structure)

### Alternative 3: Microservices Architecture
**Approach**: Split into separate services

**Decision**: Rejected - Over-engineering for CLI tool

### Alternative 4: Plugin Architecture First
**Approach**: Create plugin system, then modularize

**Decision**: Deferred - Do basic modularization first, plugins later (P2)

---

## Open Questions

1. **Q**: Should we use dataclasses or Pydantic models?
   **A**: Start with dataclasses (stdlib), can upgrade to Pydantic if validation complexity increases

2. **Q**: Async SSH now or later?
   **A**: Later (PERF-002), focus on modular structure first

3. **Q**: What about the version number?
   **A**: Bump to v3.0.0 to signal major rewrite (currently at v2.0.0)

4. **Q**: TypeScript/Go/Rust rewrite?
   **A**: No, stay with Python (maintainer preference, ecosystem fit)

---

## Stakeholder Sign-Off

### Required Approvals
- [x] @lammesen (Repository Maintainer) - **APPROVED** (complete rework, no backward compatibility needed)
- [ ] Architecture Review (this RFC)

### Decision Record
- **Date**: 2025-10-27
- **Decision**: Complete codebase rewrite approved
- **Rationale**: Clean slate enables best practices without legacy constraints
- **Version**: Will be v3.0.0 (major breaking release)

---

## References

- [BACKLOG.md](../BACKLOG.md) - ARCH-001, TEST-001
- [CODEMAP.md](../CODEMAP.md) - Current architecture analysis
- [IMPROVEMENT_PLAN.md](../IMPROVEMENT_PLAN.md) - Strategic context

---

## Appendix A: Migration Checklist

### Pre-Migration
- [ ] Baseline test coverage measured (currently 20%)
- [ ] Performance benchmarks captured
- [ ] All existing tests passing
- [ ] Stakeholder approval received

### During Migration (Per Phase)
- [ ] Module created and tested
- [ ] Imports updated
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Code review completed

### Post-Migration
- [ ] All modules extracted
- [ ] Test coverage >80%
- [ ] Performance verified (within 10%)
- [ ] Documentation complete
- [ ] Migration guide published
- [ ] Announcement made

---

## Appendix B: Rollback Plan

If critical issues arise during migration:

1. **Immediate Rollback**
   - Revert to previous commit
   - Old file still in place as backup
   - Issue hotfix release if needed

2. **Partial Rollback**
   - Keep successfully migrated modules
   - Rollback problematic module
   - Fix and re-attempt

3. **Extended Timeline**
   - Pause migration
   - Fix issues
   - Resume when stable

**Rollback Criteria**:
- Test coverage drops below baseline (20%)
- Performance degrades >20%
- Critical bugs in production
- User scripts break unexpectedly

---

*RFC Status: Draft - Awaiting Stakeholder Approval*  
*Last Updated: 2025-10-27*  
*Next Review: 2025-11-03*
