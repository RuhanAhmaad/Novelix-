#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# NOVELIX 11.0 — VIP TERMINAL ADMIN LAUNCHER
# ═══════════════════════════════════════════════════════════════
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
node "$DIR/scripts/admin-cli.js" "$@"
