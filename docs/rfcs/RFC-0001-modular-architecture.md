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

This RFC proposes refactoring the current monolithic 2,837-line `netmiko_collector.py` into a modular architecture with 8-10 focused modules under a `/src/netmiko_collector/` structure. This change will improve testability, maintainability, and extensibility while maintaining full backward compatibility for existing users.

**Key Benefits**:
- Test coverage improvement from 20% to >80%
- Each module <500 lines (down from 2,837)
- Clear separation of concerns
- Easier unit testing per module
- Better code reusability
- Simplified onboarding for contributors

**Migration Strategy**: Gradual extraction with feature flags, maintaining backward compatibility throughout.

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

## Migration Strategy

### Phase 1: Preparation (Week 1-2)
**Goal**: Establish safety net before changes

1. **Increase Test Coverage** (TEST-001)
   - Add unit tests for existing functions
   - Target: 50% coverage minimum
   - Focus on complex functions first
   - Create fixtures for test data

2. **Create Module Stubs**
   - Create `/src/netmiko_collector/` directory
   - Create empty module files with docstrings
   - Add `__init__.py` with version export
   - Verify imports work

3. **Set Up CI Gates**
   - Enforce minimum coverage in CI
   - Add import verification tests
   - Configure mypy for new modules

### Phase 2: Extract Utilities (Week 3)
**Goal**: Move standalone functions first (low risk)

1. **Extract `utils.py`**
   - Move: `expand_path()`, `get_positive_int_input()`
   - Add unit tests for each function
   - Update imports in main file
   - Verify all tests pass

2. **Extract `ui.py`**
   - Move: `print_banner()`, `print_success()`, etc.
   - Move: `select_from_menu()`
   - Add unit tests
   - Update imports

3. **Extract `models.py`**
   - Create: `Device`, `Command`, `Result` dataclasses
   - Gradually replace dict usage
   - Add validation methods

### Phase 3: Extract Core Logic (Week 4-5)
**Goal**: Move business logic modules

1. **Extract `config.py`**
   - Create `Config` class
   - Move configuration functions
   - Add unit tests for load/save
   - Maintain backward compatibility

2. **Extract `devices.py`**
   - Move `load_devices()` function
   - Add validation logic
   - Use `Device` model
   - Add comprehensive tests

3. **Extract `commands.py`**
   - Move `load_commands()` function
   - Move `DEVICE_COMMANDS` database
   - Add tests for all device types

### Phase 4: Extract SSH & Execution (Week 6-7)
**Goal**: Move complex SSH logic (highest risk)

1. **Extract `ssh.py`**
   - Create `SSHConnection` class
   - Move `connect_and_execute()`
   - Move retry logic
   - Extensive mocking in tests
   - Maintain exact behavior

2. **Extract `executor.py`**
   - Create `ParallelExecutor` class
   - Move `process_devices_parallel()`
   - Add progress tracking
   - Test with mock devices

### Phase 5: Extract Formatters (Week 8)
**Goal**: Modularize output generation

1. **Create Formatter Framework**
   - Create `formatters/` package
   - Create `base.py` with `OutputFormatter` ABC
   - Create formatter registry

2. **Extract Individual Formatters**
   - Move each `save_to_*()` function to own file
   - Implement `OutputFormatter` interface
   - Add tests for each formatter
   - Verify output format unchanged

### Phase 6: Extract CLI (Week 9)
**Goal**: Finalize with CLI layer

1. **Extract `cli.py`**
   - Move Typer command definitions
   - Wire up all modules
   - Maintain exact CLI behavior
   - Add CLI integration tests

2. **Create Entry Points**
   - Create `__main__.py`
   - Update `pyproject.toml` entry points
   - Test both execution methods

### Phase 7: Cleanup & Polish (Week 10)
**Goal**: Finalize migration

1. **Remove Old File**
   - Verify all functionality migrated
   - Run full test suite
   - Keep old file as `netmiko_collector_legacy.py` for one release
   - Add deprecation warning if imported

2. **Documentation Updates**
   - Update all documentation for new structure
   - Add migration guide for contributors
   - Update CODEMAP.md
   - Add API documentation

3. **Performance Verification**
   - Benchmark before/after
   - Ensure no performance regression
   - Optimize if needed

---

## Backward Compatibility Strategy

### For End Users
**Guarantee**: No changes to CLI interface or behavior

1. **CLI Commands Unchanged**
   ```bash
   # These work exactly the same:
   python netmiko_collector.py run -d devices.csv -c commands.txt
   netmiko-collector run -d devices.csv -c commands.txt
   ```

2. **File Formats Unchanged**
   - Device CSV format: Identical
   - Command TXT format: Identical
   - Output formats: Byte-for-byte identical
   - Config JSON: Backward compatible

3. **Behavior Unchanged**
   - Same error messages
   - Same progress indicators
   - Same logging format
   - Same session logs

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

1. **Breaking User Scripts**
   - **Risk**: Users import functions directly
   - **Likelihood**: LOW (primarily CLI tool)
   - **Impact**: HIGH (user frustration)
   - **Mitigation**: 
     - Compatibility shims in `__init__.py`
     - Deprecation warnings
     - Clear migration guide
     - Keep legacy file for one release

2. **Regression Bugs**
   - **Risk**: Behavior changes during refactoring
   - **Likelihood**: MEDIUM (complex code)
   - **Impact**: HIGH (production impact)
   - **Mitigation**:
     - Increase test coverage to >50% first
     - Add integration tests
     - Gradual migration with continuous testing
     - Beta testing period

3. **Performance Degradation**
   - **Risk**: Module imports add overhead
   - **Likelihood**: LOW (imports are fast)
   - **Impact**: MEDIUM (user experience)
   - **Mitigation**:
     - Benchmark before/after
     - Lazy imports where appropriate
     - Performance tests in CI

### Medium Risks 🟡

4. **Incomplete Migration**
   - **Risk**: Some functionality left behind
   - **Likelihood**: LOW (careful planning)
   - **Impact**: MEDIUM (technical debt)
   - **Mitigation**:
     - Checklist of all functions
     - Code coverage tracking
     - Comprehensive testing

5. **Import Cycles**
   - **Risk**: Circular dependencies created
   - **Likelihood**: MEDIUM (complex relationships)
   - **Impact**: MEDIUM (import errors)
   - **Mitigation**:
     - Careful dependency planning
     - Models as shared foundation
     - Dependency injection pattern

### Low Risks 🟢

6. **Documentation Lag**
   - **Risk**: Docs not updated in time
   - **Likelihood**: LOW (planned in migration)
   - **Impact**: LOW (temporary confusion)
   - **Mitigation**:
     - Update docs alongside code
     - Automated doc generation where possible

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
- ✅ All existing tests pass
- ✅ No CLI behavior changes
- ✅ Test coverage >80%
- ✅ All modules <500 lines
- ✅ No circular dependencies
- ✅ Documentation updated
- ✅ Migration guide provided

### Should Have (Important)
- ✅ Performance within 10% of baseline
- ✅ Type hints on all public functions
- ✅ Docstrings on all modules
- ✅ CI gates enforce coverage
- ✅ Example usage in docs

### Nice to Have (Optional)
- Async SSH option (future)
- Plugin system for formatters (future)
- API for programmatic use (future)

---

## Timeline & Resources

### Estimated Duration
- **Total**: 10 weeks
- **Phases**: 7 phases (preparation through cleanup)
- **Effort**: ~50-60 story points

### Resource Requirements
- **1 Senior Engineer**: Architecture, complex modules
- **1 Mid-Level Engineer**: Formatters, utilities, tests
- **Part-time QA**: Testing strategy, validation

### Milestones
1. **Week 2**: Test coverage >50%, modules stubbed
2. **Week 5**: Core logic extracted, tests passing
3. **Week 8**: All modules extracted, integration working
4. **Week 10**: Documentation complete, ready for release

---

## Alternatives Considered

### Alternative 1: Keep Monolithic, Add Classes
**Approach**: Convert to OOP within single file

**Decision**: Rejected - Doesn't address core issues (file size, navigation)

### Alternative 2: Microservices Architecture
**Approach**: Split into separate services

**Decision**: Rejected - Over-engineering for CLI tool

### Alternative 3: Plugin Architecture First
**Approach**: Create plugin system, then modularize

**Decision**: Deferred - Do basic modularization first, plugins later

---

## Open Questions

1. **Q**: Should we maintain `netmiko_collector.py` as a facade?
   **A**: Yes, for one release with deprecation warning

2. **Q**: Can we break import compatibility?
   **A**: No, maintain shims in `__init__.py` for one release

3. **Q**: Should we use dataclasses or Pydantic models?
   **A**: Start with dataclasses (stdlib), can upgrade to Pydantic later

4. **Q**: Async SSH now or later?
   **A**: Later (PERF-002), focus on modular structure first

---

## Stakeholder Sign-Off

### Required Approvals
- [ ] @lammesen (Repository Maintainer)
- [ ] Architecture Review
- [ ] Community Feedback (GitHub issue discussion)

### Feedback Period
- **Duration**: 1 week
- **Discussion**: GitHub issue #TBD
- **Deadline**: 2025-11-03

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
