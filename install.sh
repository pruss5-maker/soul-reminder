#!/usr/bin/env bash
set -euo pipefail

# Soul Reminder plugin installer for Hermes Agent
# One-command install: symlinks plugin into HERMES_HOME/plugins and enables it

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_NAME="soul-reminder"

# Resolve HERMES_HOME
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
PLUGINS_DIR="$HERMES_HOME/plugins"
PLUGIN_SRC="$SCRIPT_DIR"
PLUGIN_DST="$PLUGINS_DIR/$PLUGIN_NAME"

echo "🔌 Installing $PLUGIN_NAME plugin..."

# Check Hermes is installed
if [ ! -d "$HERMES_HOME" ]; then
    echo "❌ Hermes home not found at $HERMES_HOME"
    echo "   Install Hermes first: curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"
    exit 1
fi

# Create plugins dir if needed
mkdir -p "$PLUGINS_DIR"

# Symlink plugin
if [ -L "$PLUGIN_DST" ]; then
    echo "   Removing existing symlink..."
    rm "$PLUGIN_DST"
elif [ -d "$PLUGIN_DST" ]; then
    echo "   Removing existing plugin directory..."
    rm -rf "$PLUGIN_DST"
fi

ln -s "$PLUGIN_SRC" "$PLUGIN_DST"
echo "   ✅ Symlinked $PLUGIN_SRC -> $PLUGIN_DST"

# Enable the plugin
if command -v hermes &>/dev/null; then
    echo "   Enabling plugin..."
    hermes plugins enable "$PLUGIN_NAME" 2>/dev/null || echo "   (enable via: hermes plugins enable $PLUGIN_NAME)"
else
    echo "   ⚠️  hermes CLI not found in PATH. Enable manually after restart:"
    echo "      hermes plugins enable $PLUGIN_NAME"
fi

echo ""
echo "✅ $PLUGIN_NAME installed!"
echo ""
echo "Next steps:"
echo "  1. Restart Hermes (new session or /reset)"
echo "  2. Check status: /soul status"
echo "  3. Your SOUL.md at $HERMES_HOME/SOUL.md will be auto-read"
echo "  4. Set custom interval: /soul interval 5"
echo "  5. Set custom concepts: /soul set \"don't lie, validate first, fewest words\""
