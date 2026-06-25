#!/usr/bin/env bash
set -euo pipefail

# Soul Reminder plugin uninstaller

PLUGIN_NAME="soul-reminder"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
PLUGINS_DIR="$HERMES_HOME/plugins"
PLUGIN_DST="$PLUGINS_DIR/$PLUGIN_NAME"

echo "🗑️  Uninstalling $PLUGIN_NAME plugin..."

# Disable the plugin
if command -v hermes &>/dev/null; then
    hermes plugins disable "$PLUGIN_NAME" 2>/dev/null || true
fi

# Remove symlink or directory
if [ -L "$PLUGIN_DST" ]; then
    rm "$PLUGIN_DST"
    echo "   ✅ Removed symlink $PLUGIN_DST"
elif [ -d "$PLUGIN_DST" ]; then
    rm -rf "$PLUGIN_DST"
    echo "   ✅ Removed directory $PLUGIN_DST"
else
    echo "   ℹ️  Plugin not found at $PLUGIN_DST (already removed?)"
fi

echo ""
echo "✅ $PLUGIN_NAME uninstalled. Restart Hermes to take effect."
echo "   Your SOUL.md and config files were NOT touched."
