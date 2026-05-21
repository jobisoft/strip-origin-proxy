# Strip Origin Proxy

A small local proxy that strips two headers (`anthropic-dangerous-direct-browser-access`
and `Origin`) from outbound requests to `https://api.anthropic.com`. All other
traffic is tunneled through untouched, including TLS, so cert pinning for
unrelated sites still works.

Internally it's a [mitmproxy](https://mitmproxy.org/) instance with selective
TLS interception (`--allow-hosts api.anthropic.com`) and a ~25-line addon that
edits matching requests.

## Files

- `run.sh`: launcher script
- `strip_origin.py`: the mitmproxy addon that does the header stripping

## Install mitmproxy

### Linux

```sh
sudo apt install mitmproxy
```

### macOS

```sh
brew install mitmproxy
```

Verify:

```sh
mitmdump --version
```

## First-time setup

### 1. Generate the local CA

Start the proxy once so mitmproxy creates its CA cert under `~/.mitmproxy/`:

```sh
./run.sh
```

Leave it running, or stop it (Ctrl+C) after a few seconds. The cert files
exist after the first launch.

### 2. Trust the CA in Thunderbird

The proxy intercepts TLS for `api.anthropic.com` using a cert signed by the
local mitmproxy CA. Thunderbird needs to trust that CA, or the connection will
fail.

1. Thunderbird → **Settings** → **Privacy & Security**
2. Scroll to **Certificates** → click **View Certificates…**
3. Open the **Authorities** tab → **Import…**
4. Pick `~/.mitmproxy/mitmproxy-ca-cert.pem`
5. Tick **"Trust this CA to identify websites"** → OK

To remove it later, find **mitmproxy** in the Authorities tab and click
**Delete or Distrust…**.

### 3. Point Thunderbird at the proxy

Thunderbird → **Settings** → scroll to **Network & Disk Space** →
**Connection… → Settings…** → choose **Manual proxy configuration**:

- **HTTP Proxy:** `127.0.0.1`  **Port:** `8080`
- Tick **"Also use this proxy for HTTPS"**
- **Leave SOCKS Host empty**
- **Do not** tick "Use this proxy server for all protocols"
- **No proxy for:** can be left blank

Click OK.

## Usage

Open a terminal and run:

```sh
cd /path/to/strip-origin-proxy
./run.sh
```

The proxy listens on `127.0.0.1:8080`. Stop it with Ctrl+C or by closing the
terminal.

When a matching request goes through you'll see:

```
[strip-origin] POST /v1/messages — stripped: origin, anthropic-dangerous-direct-browser-access
```

## How interception is scoped

The launcher passes `--allow-hosts 'api\.anthropic\.com'` to mitmdump, which
restricts TLS interception to that one host. Every other HTTPS connection from
Thunderbird is forwarded as raw encrypted bytes — mitmproxy never sees inside,
the local CA is never presented, and cert pinning behaves normally.

## Security notes

- The local CA can sign certs for any hostname while it's trusted in
  Thunderbird. Don't share `~/.mitmproxy/mitmproxy-ca-key.pem`, and remove the
  CA from Thunderbird's trust store when you no longer need this proxy.
- The proxy binds to `127.0.0.1` only — it isn't reachable from other machines.
- The addon logs header **names** only, never values. Bodies are never logged.
