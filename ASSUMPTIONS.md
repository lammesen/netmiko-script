# Project Assumptions

This document records assumptions made during the repository audit and improvement process. These assumptions guide decision-making and can be revisited as the project evolves.

## Last Updated
2025-10-27

## Core Project Assumptions

### 1. User Base & Audience
**Assumption**: The primary users are network engineers and system administrators managing Cisco network devices.

**Evidence**:
- README mentions "network devices using SSH"
- Default device type is `cisco_ios`
- Command database includes Cisco-specific commands
- Documentation examples use Cisco command syntax

**Impact**: 
- Features should prioritize network automation workflows
- Documentation should assume networking knowledge
- CLI UX should match network engineer expectations

**Reversible**: Yes, can expand to other device types/audiences

---

### 2. Target Platform
**Assumption**: Primary deployment target is Windows 11 workstations.

**Evidence**:
- Problem statement specifies "TARGET_PLATFORMS: Windows 11"
- Code includes Windows-specific UTF-8 console handling
- README shows Windows command examples
- File path handling considers Windows paths

**Impact**:
- Test on Windows environments
- Ensure Windows compatibility for all features
- Consider PowerShell integration
- Handle Windows path separators correctly

**Reversible**: Yes, can maintain cross-platform support

---

### 3. Deployment Model
**Assumption**: Tool is deployed as a standalone CLI executable, not as a library or service.

**Evidence**:
- Single script architecture
- No API endpoints or web interface
- Command-line argument parsing with Typer
- Direct execution model

**Impact**:
- Focus on CLI UX and ergonomics
- No need for API documentation
- Distribution as executable or Python script
- Configuration via CLI flags and config file

**Reversible**: Yes, could add library interface later

---

### 4. Security Posture
**Assumption**: Security is paramount due to SSH credential handling and device access.

**Evidence**:
- Problem statement: "SECURITY_SENSITIVITY: high"
- Extensive security documentation in README and SECURITY.md
- Multiple security scanners in CI (Bandit, CodeQL, pip-audit)
- Pre-commit hooks for secret scanning
- No password arguments in CLI (interactive only)

**Impact**:
- All changes must pass security review
- Credentials must never be logged or committed
- Authentication methods must be secure
- Audit logging for compliance

**Reversible**: No, security requirements are fixed

---

### 5. Network Environment
**Assumption**: Users operate in enterprise networks with SSH access to devices, potentially through jump hosts.

**Evidence**:
- SSH config file support
- Proxy/jump server examples in documentation
- Connection timeout configurations
- SSH key authentication support

**Impact**:
- Must support complex network topologies
- Jump host/bastion configuration is important
- Network timeouts must be configurable
- SSH config integration is valuable

**Reversible**: No, enterprise scenarios are core use case

---

### 6. Device Inventory Management
**Assumption**: Users maintain device inventories in CSV format and command lists in text files.

**Evidence**:
- CSV-based device input
- Text file command lists
- Multiple example files provided
- No database or external system integration

**Impact**:
- File-based I/O is primary interface
- CSV format must be maintained
- No need for database integration (yet)
- File validation is important

**Reversible**: Yes, could add database support later

---

### 7. Concurrent Processing
**Assumption**: Users need to process multiple devices simultaneously for efficiency.

**Evidence**:
- ThreadPoolExecutor implementation
- Configurable worker count (1-20)
- Performance examples showing speedup
- Progress indicators for parallel execution

**Impact**:
- Concurrency must be stable and safe
- Thread safety is critical
- Resource limits are important
- Error handling per device required

**Reversible**: No, concurrency is core feature

---

### 8. Output Formats
**Assumption**: Users need flexibility in output formats for different use cases (reporting, automation, analysis).

**Evidence**:
- Multiple output formats: CSV, JSON, HTML, Markdown, Excel
- Rich CLI output with tables
- Timestamped output files
- Session logging capability

**Impact**:
- Format support must be maintained
- New formats should be easy to add
- Output must be well-structured
- Parsing downstream is a use case

**Reversible**: Partially, core formats must remain

---

### 9. Backward Compatibility
**Assumption**: Existing device CSV files and command lists should continue working.

**Evidence**:
- Problem statement emphasizes stability
- Production use indicated
- Multiple example files show expected formats
- No breaking changes in recent versions

**Impact**:
- File format changes require migration path
- CLI flag changes need deprecation warnings
- Configuration changes need defaults
- RFC process for breaking changes

**Reversible**: No, backward compatibility is critical

---

### 10. Development Environment
**Assumption**: Developers use Python 3.7+ with standard tooling (pip, venv, make).

**Evidence**:
- pyproject.toml requires Python 3.7+
- Makefile for common tasks
- requirements.txt and requirements-dev.txt
- Pre-commit hooks configured

**Impact**:
- Python 3.7 compatibility must be maintained
- Standard tooling should be used
- Makefile targets should be comprehensive
- Virtual environments are expected

**Reversible**: Yes, can add Docker/devcontainer

---

### 11. Licensing & Compliance
**Assumption**: MIT license allows broad usage; no specific compliance requirements beyond general security.

**Evidence**:
- LICENSE file contains MIT license
- Problem statement: "LICENSE & COMPLIANCE NEEDS: MIT License"
- No HIPAA/PCI-DSS requirements mentioned

**Impact**:
- Can use MIT-compatible dependencies
- No special compliance documentation needed (yet)
- Open source contribution model
- Commercial use allowed

**Reversible**: No, license is fixed

---

### 12. CI/CD & Release Process
**Assumption**: GitHub Actions is the CI/CD platform; releases use semantic versioning.

**Evidence**:
- Problem statement: "CI/CD_PROVIDER: GitHub Actions"
- 13 GitHub Actions workflows configured
- CHANGELOG.md with version history
- Semantic versioning in use (though inconsistent)

**Impact**:
- GitHub Actions expertise required
- Workflows must be maintained
- Semantic versioning must be enforced
- Release automation valuable

**Reversible**: No, GitHub Actions is platform choice

---

### 13. Documentation Standards
**Assumption**: Comprehensive Markdown documentation with examples is expected.

**Evidence**:
- Extensive README.md
- CONTRIBUTING.md and SECURITY.md present
- Problem statement requires extensive docs
- GitHub-flavored Markdown used

**Impact**:
- All features must be documented
- Examples should be provided
- Documentation lives in repository
- Markdown format is standard

**Reversible**: No, documentation requirements are fixed

---

### 14. Code Quality Standards
**Assumption**: High code quality is required (linting, typing, testing, formatting).

**Evidence**:
- Problem statement: "Quality > speed"
- Multiple linters configured (pylint, flake8, mypy)
- Black and isort for formatting
- Pre-commit hooks enforced
- CI runs quality checks

**Impact**:
- All code must pass linters
- Test coverage should increase
- Type hints should be added
- Code must be formatted

**Reversible**: No, quality standards are fixed

---

### 15. Monolithic vs Modular
**Assumption**: Current monolithic design (2,837 lines) should be refactored to modular architecture.

**Evidence**:
- Problem statement: "Do not be afraid to completely remake the code base"
- Single file is unwieldy
- Testing is difficult
- Maintenance is challenging

**Impact**:
- Major refactoring likely needed
- RFC process for architecture changes
- Gradual migration path required
- Backward compatibility during transition

**Reversible**: Yes, but change is recommended

---

## Assumptions Requiring Validation

These assumptions should be confirmed with @lammesen:

1. **Version Number**: Which version is correct? (2.0.0, 3.0.0, or 4.0.0)
2. **Breaking Changes**: Are breaking changes acceptable if RFC approved?
3. **Refactoring Scope**: How aggressive should refactoring be?
4. **Testing Priority**: What's acceptable coverage target? (>80%?)
5. **Windows-Only**: Should Linux/macOS compatibility be maintained?
6. **Feature Additions**: Which features are highest priority?
7. **Release Cadence**: How often should releases occur?
8. **Community vs Internal**: Is this for internal use or public community?

---

## Decision Log

| Date | Decision | Rationale | Reversible |
|------|----------|-----------|------------|
| 2025-10-27 | Use `/docs`, `/src`, `/tests` structure | Standard Python project layout | Yes |
| 2025-10-27 | Maintain Python 3.7+ compatibility | Per pyproject.toml requirement | No |
| 2025-10-27 | Prioritize security in all changes | HIGH security sensitivity | No |
| 2025-10-27 | Create comprehensive documentation | Gap identified in audit | No |
| 2025-10-27 | Use RFC process for major changes | Per problem statement | No |

---

## Notes

- This document should be updated as assumptions are validated or invalidated
- New assumptions should be documented as they emerge
- Assumption changes may require plan adjustments
- Validate critical assumptions before major work

---
