# NEMO Trading Bot - Security Audit Report

**Date:** 2026-02-27  
**Auditor:** Security Agent, NEMO Mission Control  
**Scope:** `trading/nemo-trading/` codebase  
**Files Audited:**
- `main.py` — Main orchestrator
- `exchanges/polymarket.py` — Polymarket CLOB interface
- `exchanges/coinbase.py` — Coinbase exchange interface  
- `exchanges/websocket_client.py` — WebSocket client
- `utils/risk.py` — Risk management
- `utils/vpin.py` — VPIN toxicity detection
- `utils/kelly.py` — Kelly position sizing
- `config.py` — Configuration management
- `.env` — Environment variables
- `requirements.txt` — Dependencies

---

## Executive Summary

**CRITICAL SECURITY ISSUES DETECTED**

The trading bot codebase contains **1 CRITICAL** and **4 HIGH** severity security issues that require immediate attention. The most severe issue is a **hardcoded blockchain private key** in the `.env` file, which poses an immediate risk of fund theft if the repository is exposed.

### Severity Distribution
| Severity | Count | Status |
|----------|-------|--------|
| Critical | 1 | 🔴 Immediate action required |
| High | 4 | 🟠 Address within 24 hours |
| Medium | 3 | 🟡 Address within 1 week |
| Low | 2 | 🟢 Address when convenient |

---

## Critical Issues (Immediate Action Required)

### CRITICAL-001: Hardcoded Private Key in `.env` File

**File:** `trading/nemo-trading/.env`  
**Line:** 17  
**Severity:** 🔴 **CRITICAL**

#### Description
A real Ethereum private key (`0xac07f9ab179d4f3645322968c4c3fee5254f2eb4ffbd093ae6cdeea75390d9ad`) and funder address (`0x6Ca15Ec1764A7cE16B7ada4eC29934923f756a8a`) are hardcoded in the `.env` file. This is a private key for the Polymarket wallet.

#### Impact
- **Immediate fund theft risk** if repository is pushed to public GitHub
- Private key grants full control over the associated wallet
- Any user with repository access can drain funds
- Key may be exposed in shell history, backups, or logs

#### Evidence
```bash
# From .env file:
POLYMARKET_PRIVATE_KEY=0xac07f9ab179d4f3645322968c4c3fee5254f2eb4ffbd093ae6cdeea75390d9ad
FUNDER_ADDRESS=0x6Ca15Ec1764A7cE16B7ada4eC29934923f756a8a
```

#### Remediation
1. **IMMEDIATELY** rotate the private key on-chain (transfer funds to a new wallet)
2. Add `.env` to `.gitignore` if not already present
3. Remove the `.env` file from git history using `git filter-branch` or BFG Repo-Cleaner
4. Store credentials in a secure vault (1Password, AWS Secrets Manager, etc.)
5. Load credentials at runtime from secure storage, never commit to repo

---

## High Severity Issues

### HIGH-001: Private Key Stored in Memory Without Encryption

**File:** `exchanges/polymarket.py`  
**Lines:** 45-50, 56-60  
**Severity:** 🟠 **HIGH**

#### Description
The `PolymarketExchange` class stores the private key in plain text as an instance variable (`self.private_key`). This key remains in memory throughout the application lifecycle and could be extracted via:
- Memory dumps
- Core dumps on crash
- Debug logs
- Python object introspection

#### Evidence
```python
def __init__(self, private_key: str, funder_address: str, ...):
    self.private_key = private_key  # Stored in plaintext
    ...
    if not dry_run and POLYMARKET_SDK and private_key:
        self.client = ClobClient(
            host=clob_host,
            key=private_key,  # Passed to SDK
            ...
        )
```

#### Remediation
- Use environment variables loaded at initialization only
- Consider using key management services (KMS) or hardware security modules (HSM)
- Implement secure memory handling (zero out key after use when possible)
- Use session-based authentication where available

---

### HIGH-002: Missing Input Validation on Configuration Values

**File:** `config.py`  
**Lines:** 106-122 (`validate()` method)  
**Severity:** 🟠 **HIGH**

#### Description
The `Config.validate()` method only checks for presence of credentials but does not validate:
- Private key format (should be 64 hex characters with 0x prefix)
- API key format and length
- Address checksum validation (EIP-55 for Ethereum)
- Numeric range validation (e.g., `max_position_size` could be negative or excessively large)
- URL validation for `clob_host` and `gamma_host`

#### Impact
- Malformed private keys could cause crashes or undefined behavior
- Invalid URLs could lead to man-in-the-middle attacks
- Negative position sizes could bypass risk controls
- Untrusted input could lead to injection attacks

#### Evidence
```python
def validate(self) -> bool:
    if self.exchange == "coinbase":
        if not self.coinbase.api_key or not self.coinbase.api_secret:
            if not self.dry_run:
                raise ValueError("Coinbase API credentials required for live trading")
    # ... no format validation
```

#### Remediation
```python
import re
from web3 import Web3

def validate(self) -> bool:
    # Validate private key format
    if self.polymarket.private_key:
        if not re.match(r'^0x[a-fA-F0-9]{64}$', self.polymarket.private_key):
            raise ValueError("Invalid private key format")
        # Validate address checksum
        if not Web3.is_checksum_address(self.polymarket.funder_address):
            raise ValueError("Invalid funder address")
    
    # Validate numeric ranges
    if self.risk.max_position_size <= 0 or self.risk.max_position_size > 100000:
        raise ValueError("max_position_size must be between 0 and 100000")
    
    # Validate URLs
    if not self.polymarket.clob_host.startswith(('https://', 'wss://')):
        raise ValueError("CLOB host must use HTTPS or WSS")
```

---

### HIGH-003: Race Condition in Risk Manager Position Tracking

**File:** `utils/risk.py`  
**Lines:** 89-104, 107-131  
**Severity:** 🟠 **HIGH**

#### Description
The `RiskManager` class uses plain Python data structures (`dict`, `dataclass`) without any thread synchronization. The `can_trade()`, `open_position()`, and `close_position()` methods are not atomic and could lead to race conditions:

- Multiple concurrent trades could bypass `daily_trade_limit`
- `consecutive_losses` counter could be inaccurate
- Position dictionary could become corrupted
- Balance calculations could be wrong

#### Evidence
```python
# No threading locks or async locks
class RiskManager:
    def __init__(self, config: RiskConfig, start_balance: float = 10000.0):
        self.state = SessionState(...)  # Plain dataclass, no locks
    
    def can_trade(self, symbol: str, proposed_size: float) -> tuple[bool, str]:
        # Check-then-act race condition
        if self.state.trades_today >= self.config.daily_trade_limit:
            return False, "Daily trade limit reached"
        # Another thread could increment trades_today here
```

#### Remediation
```python
import asyncio
from threading import Lock

class RiskManager:
    def __init__(self, config: RiskConfig, start_balance: float = 10000.0):
        self._lock = asyncio.Lock()  # For async code
        # OR: self._lock = Lock()  # For threaded code
    
    async def can_trade(self, symbol: str, proposed_size: float) -> tuple[bool, str]:
        async with self._lock:
            # Atomic check and update
            if self.state.trades_today >= self.config.daily_trade_limit:
                return False, "Daily trade limit reached"
```

---

### HIGH-004: Insecure Logging of Potentially Sensitive Data

**File:** `main.py`  
**Lines:** 67-76, 355-365  
**Severity:** 🟠 **HIGH**

#### Description
The logging setup in `main.py` writes to `/tmp/nemo-trading.log` which:
1. Is world-readable on many systems (`/tmp` has 777 permissions)
2. Could persist across reboots depending on system configuration
3. May be included in crash reports or system diagnostics

Additionally, the `shutdown()` method logs detailed P&L information which, combined with other logs, could reveal trading strategies and performance.

#### Evidence
```python
def setup_logging(log_level: str = "INFO"):
    # File handler for persistence
    file_handler = logging.FileHandler('/tmp/nemo-trading.log', mode='a')
    # No permission restrictions on log file
```

#### Remediation
```python
import os
import stat

def setup_logging(log_level: str = "INFO"):
    log_path = '/tmp/nemo-trading.log'
    file_handler = logging.FileHandler(log_path, mode='a')
    
    # Restrict permissions to owner only (600)
    os.chmod(log_path, stat.S_IRUSR | stat.S_IWUSR)
    
    # Or better: use a private log directory
    log_dir = os.path.expanduser('~/.nemo/logs')
    os.makedirs(log_dir, mode=0o700, exist_ok=True)
    log_path = os.path.join(log_dir, 'trading.log')
```

---

## Medium Severity Issues

### MEDIUM-001: Path Traversal Risk in Log File Path

**File:** `main.py`  
**Line:** 66  
**Severity:** 🟡 **MEDIUM**

#### Description
The log file path `/tmp/nemo-trading.log` is hardcoded but if user input were ever allowed to influence the path, it could lead to path traversal attacks. The `config.py` file references `trades_log: str = "data/trades.jsonl"` which could be manipulated.

#### Remediation
- Never allow user input to influence file paths
- Use path canonicalization with `os.path.realpath()`
- Validate paths against allowed directories

---

### MEDIUM-002: Dependency Vulnerabilities in Requirements

**File:** `requirements.txt`  
**Severity:** 🟡 **MEDIUM**

#### Description
The requirements file uses loose version constraints (`>=`) which could pull in vulnerable versions:

```
requests>=2.31.0
flask>=2.3.0
web3>=6.0.0
```

Known vulnerabilities:
- `requests` < 2.32.0 has CVE-2024-35195 (authentication header leakage)
- `flask` < 2.3.3 has potential DoS issues
- `web3` < 6.11.0 has various security patches

#### Remediation
```
# Pin to specific secure versions
requests==2.32.3
flask==3.0.3
web3==6.15.1
coinbase-advanced-py==1.2.0
py-clob-client==0.34.0
python-dotenv==1.0.1
numpy==1.26.4
```

---

### MEDIUM-003: Missing Error Handling in WebSocket Client

**File:** `exchanges/websocket_client.py`  
**Lines:** 150-180  
**Severity:** 🟡 **MEDIUM**

#### Description
The WebSocket client's `_receive_loop()` catches generic `Exception` which could mask critical errors:

```python
except Exception as e:
    logging.error(f"❌ {self.name} receive error: {e}")
    await self._reconnect()
```

This could lead to infinite reconnection loops and mask security-related errors (TLS failures, certificate issues).

#### Remediation
Distinguish between recoverable and non-recoverable errors:
```python
from websockets.exceptions import InvalidHandshake, SecurityError

except SecurityError as e:
    logging.critical(f"Security error, not reconnecting: {e}")
    raise  # Don't reconnect on security errors
except InvalidHandshake:
    logging.error("TLS handshake failed")
    await self._reconnect()
```

---

## Low Severity Issues

### LOW-001: Weak Random Number Generation in Dry-Run Mode

**File:** `main.py`  
**Lines:** 307-313  
**Severity:** 🟢 **LOW**

#### Description
The dry-run simulation uses `random.random()` which is not cryptographically secure. While this is only for simulation, it could produce predictable "random" behavior.

#### Remediation
Use `secrets` module for better randomness:
```python
import secrets
current_delta = secrets.SystemRandom().uniform(8.0, 50.0)
```

---

### LOW-002: Information Disclosure via Version Strings

**File:** `main.py`  
**Lines:** 1-10 (docstring)  
**Severity:** 🟢 **LOW**

#### Description
The module docstring reveals internal integration dates and capabilities which could help attackers identify specific code versions and target known vulnerabilities.

#### Remediation
Keep docstrings generic and avoid revealing internal dates/codenames.

---

## Positive Security Observations

The following security practices were identified as positive:

1. **Dry-run mode by default** — The bot defaults to `dry_run=True` requiring explicit `--live` flag
2. **Live trading confirmation** — Requires typing "YES" to enable live trading (line 358-366)
3. **Risk limits enforcement** — Daily loss limits, drawdown controls, and position sizing limits
4. **VPIN kill switch** — Automatic trading halt on toxic flow detection
5. **Input validation for exchange/strategy** — Validates against allowed enum values
6. **No hardcoded API keys in source** — Keys loaded from environment (though `.env` is committed)
7. **Sandbox mode support** — Both exchanges support sandbox/testnet environments

---

## Recommendations Summary

| Priority | Action | Owner | Timeline |
|----------|--------|-------|----------|
| P0 | Rotate compromised private key and remove from git history | DevOps | Immediate |
| P0 | Add `.env` to `.gitignore` and use secure credential storage | Security | Immediate |
| P1 | Implement input validation in `Config.validate()` | Backend | 24 hours |
| P1 | Add thread-safety to `RiskManager` | Backend | 24 hours |
| P1 | Secure logging with restricted permissions | Backend | 24 hours |
| P2 | Pin dependency versions and audit for CVEs | DevOps | 1 week |
| P2 | Improve WebSocket error handling | Backend | 1 week |
| P3 | Use cryptographically secure RNG | Backend | Next sprint |

---

## Appendix: Verification Commands

```bash
# Check for hardcoded secrets in git history
git log --all --full-history -- .env
git log --all -p --grep="key\|secret\|password" -- . | grep -i "private\|secret"

# Verify .env is in .gitignore
grep -E "^\.env$" .gitignore

# Check file permissions
ls -la /tmp/nemo-trading.log
ls -la ~/.nemo/logs/ 2>/dev/null || echo "Private log dir not created"

# Dependency vulnerability scan
pip install safety
safety check -r requirements.txt
```

---

**End of Security Audit Report**

*This report was generated automatically by the NEMO Security Agent. For questions or clarifications, contact the security team.*
