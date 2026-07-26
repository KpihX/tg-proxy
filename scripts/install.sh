#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Installing tg-proxy..."
uv tool install . --force
echo "✅ tg-proxy installed. Run 'tg-proxy --help' to start."
