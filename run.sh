#!/bin/sh
# Run mitmproxy with selective TLS interception for api.anthropic.com.
# Listens on 127.0.0.1:8080 — point Thunderbird's HTTP/HTTPS proxy there.
set -e

cd "$(dirname "$0")"

exec mitmdump \
  --listen-host 127.0.0.1 \
  --listen-port 8080 \
  --allow-hosts 'api\.anthropic\.com' \
  -s strip_origin.py
