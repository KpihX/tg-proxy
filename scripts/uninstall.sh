#!/usr/bin/env bash
set -euo pipefail

echo "🗑️  Uninstalling tg-proxy..."
uv tool uninstall tg-proxy 2>/dev/null || true
rm -rf ~/.config/tg-proxy
echo "✅ tg-proxy fully removed."
