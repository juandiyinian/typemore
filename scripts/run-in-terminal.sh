#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMAND="cd $(printf '%q' "$ROOT_DIR") && swift run --disable-sandbox"

osascript <<OSA
 tell application "Terminal"
   activate
   do script "$COMMAND"
 end tell
OSA
