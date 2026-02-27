# 🔐 Wallet Key Rotation — 2026-02-27

**Status**: ✅ NEW KEY GENERATED AND INSTALLED  
**Old Key**: COMPROMISED (was in git history)  
**Action Required**: Fund new wallet, transfer funds, clean git history

---

## ✅ Completed

1. **Backup created**: `/tmp/poly-bot-backup/.env.backup.20260227_00xxxxx`
2. **New private key generated**: Installed in `.env`
3. **Old key replaced**: No longer in active config

---

## 🔴 CRITICAL: Next Steps (Do These Now)

### Step 1: Get Your New Wallet Address

Since `eth_account` isn't available, use one of these methods:

**Option A: Online Tool (Less Secure)**
- Go to https://www.myetherwallet.com/wallet/access/private-key
- Enter your new private key (from `.env`)
- Copy the address shown
- **Disconnect immediately after**

**Option B: MetaMask (More Secure)**
1. Open MetaMask
2. Click account icon → Import Account
3. Paste private key from `.env`
4. Copy the address
5. You can remove the account after copying address

**Option C: Python with web3**
```bash
cd /tmp/poly-bot-backup
source venv/bin/activate
python -c "from web3 import Web3; w3 = Web3(); acct = w3.eth.account.from_key('YOUR_KEY_HERE'); print(acct.address)"
```

---

### Step 2: Fund New Wallet

**Send to your new address:**
- **USDC**: Whatever amount you want to trade with
- **MATIC**: 0.5-1 MATIC for gas fees

**Network**: Polygon (not Ethereum mainnet)

---

### Step 3: Transfer Funds from Old Wallet

**Old wallet address**: `0x6Ca15Ec1764A7cE16B7ada4eC29934923f756a8a`

1. Check balance on https://polygonscan.com/address/0x6Ca15Ec1764A7cE16B7ada4eC29934923f756a8a
2. If any funds, transfer to new wallet
3. Keep some MATIC for gas if transferring

---

### Step 4: Remove Old Key from Git History

**⚠️ This is CRITICAL — the old key is in git history**

```bash
# Install BFG Repo-Cleaner
brew install bfg  # or download from https://rtyley.github.io/bfg-repo-cleaner/

# Clone a fresh copy of your repo
cd ~
git clone --mirror https://github.com/sentientsprite/nemo-agent.git nemo-agent-mirror

# Run BFG to remove the key
bfg --replace-text replacements.txt nemo-agent-mirror

# replacements.txt should contain:
# ***REMOVED***

# Clean up
cd nemo-agent-mirror
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (DESTRUCTIVE — Coordinate with any collaborators)
git push --force
```

**Alternative**: If repo is private and you're the only user, you could also:
- Delete the GitHub repo
- Re-create it with cleaned history
- Re-push

---

### Step 5: Secure Storage

**Store new private key in:**
- 1Password (recommended)
- Hardware wallet
- Encrypted USB drive
- **Never** in plaintext files or git

---

## 📋 Checklist

- [ ] Get new wallet address
- [ ] Fund new wallet with USDC
- [ ] Fund new wallet with MATIC for gas
- [ ] Transfer funds from old wallet (if any)
- [ ] Remove old key from git history
- [ ] Store new key securely (1Password)
- [ ] Delete any backups of old key
- [ ] Test new wallet connection

---

## 🔒 Security Best Practices Going Forward

1. **Never commit `.env`** — It's in `.gitignore` now, but double-check
2. **Use 1Password** — Store credentials there, reference in `.env` comments
3. **Rotate keys quarterly** — Good hygiene
4. **Monitor wallets** — Set up alerts for any activity
5. **Separate wallets** — Use different wallets for testing vs production

---

## 🆘 Emergency Contacts

If funds are stolen from old wallet:
1. Check https://polygonscan.com for transactions
2. File report with Polygon support
3. Consider reporting to FBI IC3 (if US)

---

**Key rotation complete. New key active. Old key must be purged from history.**

🛡️ **Security is only as strong as the weakest link.**
