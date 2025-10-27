# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 3.x.x   | :white_check_mark: |
| 2.x.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### How to Report

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please report security vulnerabilities by:

1. **Email**: Send details to the repository maintainers via GitHub's private vulnerability reporting feature
2. **GitHub Security Advisory**: Use the "Security" tab → "Report a vulnerability" in this repository

### What to Include

Please provide:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if you have one)
- Your contact information

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Varies by severity
  - Critical: 24-72 hours
  - High: 1-2 weeks
  - Medium: 2-4 weeks
  - Low: Next release cycle

### Security Disclosure Policy

Once a vulnerability is reported:

1. We will confirm receipt within 48 hours
2. We will investigate and validate the issue
3. We will develop and test a fix
4. We will release a security update
5. We will publicly disclose the vulnerability after the fix is available (coordinated disclosure)

## Security Best Practices for Users

### Credential Management

**DO:**
- ✅ Use SSH key authentication when possible
- ✅ Use interactive password prompts (default behavior)
- ✅ Rotate credentials regularly
- ✅ Use strong, unique passwords
- ✅ Store SSH keys with proper permissions (600 for private keys)
- ✅ Use SSH key passphrases for additional security
- ✅ Consider using credential management systems (Vault, AWS Secrets Manager)

**DON'T:**
- ❌ Never commit credentials to version control
- ❌ Never use password CLI arguments
- ❌ Never share credentials via email or chat
- ❌ Never store passwords in plain text files
- ❌ Never use the same password across multiple devices
- ❌ Never commit device inventory files with real IPs to public repositories

### Network Security

**Recommendations:**
- Use jump hosts/bastion servers for production environments
- Implement network segmentation
- Use SSH config files for complex network topologies
- Enable session logging only when required for compliance
- Review and audit command files before execution
- Limit concurrent connections (max_workers) to prevent accidental DDoS
- Use connection timeouts appropriate for your network

### File Security

**Device and Command Files:**
- Store CSV files outside of version control (add to .gitignore)
- Use restrictive file permissions (chmod 600 on Unix-like systems)
- Validate file contents before execution
- Keep device inventory files in secure locations
- Use encrypted storage for sensitive device lists

**SSH Keys:**
- Store private keys in `~/.ssh/` with 600 permissions
- Use different keys for different environments
- Never commit private keys to version control
- Use key passphrases
- Rotate keys periodically

### Code Security

**If Modifying the Code:**
- Run all security checks before committing: `pre-commit run --all-files`
- Review Bandit security scan results
- Keep dependencies updated
- Review dependency security with `pip-audit`
- Follow secure coding practices
- Validate all user inputs
- Avoid executing arbitrary commands

### Dependency Security

**Keep Dependencies Updated:**
```bash
# Check for vulnerabilities
pip-audit

# Update dependencies
pip install --upgrade -r requirements.txt
```

**Review Updates:**
- Review CHANGELOG before updating
- Test in non-production environment first
- Monitor security advisories for dependencies

## Security Features

### Built-in Security

This project includes multiple security layers:

**Authentication:**
- SSH key authentication support
- Interactive password prompts (no CLI password arguments)
- Enable mode password handling
- SSH config file integration

**Network Protection:**
- Connection timeouts (default: 30s)
- Command timeouts (default: 60s)
- Retry logic with exponential backoff
- Thread pool limits to prevent resource exhaustion

**Code Security:**
- Pre-commit hooks with security checks
- Bandit security scanning in CI/CD
- CodeQL static analysis
- Dependency vulnerability scanning (pip-audit)
- No hardcoded credentials
- Input validation on all user inputs

**Secrets Protection:**
- Pre-commit hook detects private keys
- .gitignore prevents committing sensitive files
- No credential logging
- Secure password handling with getpass

### CI/CD Security

**Automated Security Scans:**
- Bandit (Python security linter) - runs on every push/PR and weekly
- CodeQL (semantic code analysis) - runs weekly
- pip-audit (dependency scanning) - runs on every push/PR and weekly
- Dependency Review (PR dependency checks) - runs on every PR

**Workflow Security:**
- Minimal workflow permissions (principle of least privilege)
- Secrets stored in GitHub encrypted secrets
- No credentials in workflow files

## Compliance Considerations

### Enterprise/Regulated Environments

If using this tool in regulated environments (HIPAA, PCI-DSS, SOC 2, etc.):

**Audit Logging:**
- Enable session logging when required for compliance
- Store logs in secure, centralized location
- Implement log retention policies
- Review logs regularly for suspicious activity

**Access Control:**
- Implement role-based access control for script execution
- Restrict access to credential storage
- Use privileged access management (PAM) solutions
- Document access procedures

**Data Protection:**
- Command outputs may contain sensitive configuration data
- Implement encryption at rest for output files
- Use secure file transfer methods
- Follow data classification policies

**Network Security:**
- Use encrypted channels (SSH) for all communications
- Implement network segmentation
- Use jump hosts for production access
- Monitor and log all network connections

## Known Security Considerations

### Command Execution Risk

This tool executes commands on network devices via SSH. Key considerations:

**Risk:** Commands are read from CSV files. If a command file is compromised, malicious commands could be executed.

**Mitigations:**
- Commands execute with timeout protection
- No automatic privilege escalation (enable mode must be explicitly requested)
- All commands are logged
- Command files should be treated as trusted sources
- Implement file integrity monitoring for command files

### Subprocess Usage

The tool uses subprocess for editor/file opening operations (platform-specific):
- Properly sanitized with `# nosec` annotations
- Limited to specific, safe operations
- No shell=True usage
- Reviewed by security scanners

### File Path Security

Users can specify arbitrary file paths for SSH keys, configs, and device files:

**Protections:**
- Path validation and existence checks
- Expansion of ~ to home directory
- Proper error handling for invalid paths

**Recommendations:**
- Use absolute paths when possible
- Validate file permissions before use
- Store sensitive files in secure locations

## Third-Party Dependencies

### Core Dependencies

- **netmiko** - SSH connection library (actively maintained, security focused)
- **paramiko** - SSH protocol implementation (well-vetted, widely used)
- **typer** - CLI framework (actively maintained)

### Security Dependencies

- **bandit** - Python security linter
- **pip-audit** - Dependency vulnerability scanner
- **safety** - Additional dependency security checks

All dependencies are:
- Regularly updated via Dependabot
- Scanned for vulnerabilities in CI/CD
- Specified with minimum versions to allow security patches
- From trusted sources (PyPI)

## Security Updates

### Staying Informed

- Watch this repository for security advisories
- Subscribe to GitHub security alerts
- Monitor dependency security advisories
- Review CHANGELOG for security-related updates

### Applying Updates

```bash
# Update to latest version
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Run security checks
pip-audit
pre-commit run --all-files
```

## Contact

For security concerns or questions:
- Use GitHub's private vulnerability reporting
- Check existing security advisories
- Review this SECURITY.md document

---

**Last Updated:** 2025-10-27
**Security Policy Version:** 1.0
