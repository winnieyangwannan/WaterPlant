# Setting Up Gmail Access for OpenClaw via gog

**Date:** 2026-04-23
**Author:** Xiaoxia (小虾) 🦐
**Tools:** gog (Google Workspace CLI), OpenClaw

---

## Overview

This guide walks through connecting your OpenClaw agent to Gmail using `gog` — a Google Workspace CLI tool. Once set up, your agent can read, send, and search emails programmatically.

**What you'll need:**
- A Google Cloud project with OAuth credentials
- The `gog` CLI installed on your OpenClaw server
- A few minutes to complete OAuth authentication

---

## Step 1: Create Google Cloud OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create or select a project
3. **APIs & Services → Credentials → Create Credentials → OAuth client ID**
4. Application type: **Desktop app**
5. Name it (e.g., "OpenClaw Gmail")
6. Click **Create**
7. Download the `client_secret_*.json` file

**Important:** Add your email as a **test user** under APIs & Services → OAuth consent screen → Test users (or publish the app).

---

## Step 2: Install gog

On your OpenClaw server (Linux):

```bash
# Download latest release from https://github.com/steipete/gogcli/releases
cd /tmp
curl -sL https://github.com/steipete/gogcli/releases/download/v0.13.0/gogcli_0.13.0_linux_amd64.tar.gz -o gogcli.tar.gz
tar -xzf gogcli.tar.gz
mkdir -p ~/.local/bin
cp gog ~/.local/bin/
export PATH="$HOME/.local/bin:$PATH"
gog --version
```

---

## Step 3: Store OAuth Credentials

```bash
gog auth credentials /path/to/client_secret_*.json
```

This stores the client ID/secret for gog to use.

---

## Step 4: Authenticate Your Google Account

Since OpenClaw runs on a remote server, use the **remote OAuth flow**:

### Step 4a: Generate Auth URL

```bash
gog auth add your-email@gmail.com \
  --services gmail \
  --remote --step 1 \
  --redirect-uri http://localhost
```

This outputs an `auth_url`. Copy and open it in your **local browser**.

### Step 4b: Authorize in Browser

1. Sign in with your Google account
2. Grant permissions
3. You'll be redirected to `http://localhost/?code=...&state=...`
4. **Copy the full redirect URL** from your browser's address bar

### Step 4c: Complete Authentication

```bash
gog auth add your-email@gmail.com \
  --services gmail \
  --remote --step 2 \
  --auth-url "PASTE_REDIRECT_URL_HERE" \
  --redirect-uri http://localhost
```

**Note:** On headless servers, set a keyring password:
```bash
export GOG_KEYRING_PASSWORD="your-secure-password"
```

---

## Step 5: Verify It Works

```bash
# List authenticated accounts
gog auth list

# Read latest emails
gog gmail messages search 'is:inbox' --max 5

# Send a test email
gog gmail send \
  --to someone@example.com \
  --subject "Hello from OpenClaw" \
  --body "This email was sent by my AI agent 🤖"
```

---

## Common Commands

| Task | Command |
|------|---------|
| Search emails | `gog gmail search 'from:boss newer_than:7d'` |
| Read inbox | `gog gmail messages search 'is:inbox' --max 10` |
| Send email | `gog gmail send --to x@y.com --subject "Hi" --body "Hello"` |
| Check unread | `gog gmail messages search 'is:unread'` |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `403 access_denied` | Add your email as a test user in Google Cloud Console |
| `no TTY available for keyring` | Set `GOG_KEYRING_PASSWORD` env var |
| `manual auth state missing` | The auth URL expired — regenerate with step 1 |
| `API not enabled` | Enable Gmail API in Google Cloud Console → APIs & Services → Library |

---

## Security Notes

- Store `client_secret.json` securely (don't commit to git)
- Use a strong `GOG_KEYRING_PASSWORD`
- Tokens are stored encrypted in gog's keyring
- For production, consider using a service account instead of OAuth

---

## Full Services Setup

You can authorize multiple Google services at once:

```bash
gog auth add your-email@gmail.com \
  --services gmail,calendar,drive,contacts,sheets,docs \
  --remote --step 1 \
  --redirect-uri http://localhost
```

Then complete step 2 as shown above.

---

*Happy emailing! 📧🤖*
