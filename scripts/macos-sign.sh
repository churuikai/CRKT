#!/bin/bash
set -euo pipefail

APP="src-tauri/target/release/bundle/macos/Translator.app"
# BINARY name is the Cargo package name from src-tauri/Cargo.toml.
BINARY="$APP/Contents/MacOS/crkt-tauri"
ENTITLEMENTS="src-tauri/Entitlements.plist"
# Source of truth: must match tauri.conf.json `identifier`. macOS TCC uses the
# codesign identifier as part of the designated requirement, so any drift
# silently invalidates previously granted Accessibility/Input Monitoring grants.
IDENTIFIER=$(plutil -extract identifier raw -o - src-tauri/tauri.conf.json)
PRODUCT=$(plutil -extract productName raw -o - src-tauri/tauri.conf.json)
VERSION=$(plutil -extract version raw -o - src-tauri/tauri.conf.json)
case $(uname -m) in
    arm64) ARCH=aarch64 ;;
    x86_64) ARCH=x86_64 ;;
    *) ARCH=$(uname -m) ;;
esac
DMG="src-tauri/target/release/bundle/dmg/${PRODUCT}_${VERSION}_${ARCH}.dmg"

if [ ! -d "$APP" ]; then
    echo "Error: $APP not found"
    exit 1
fi

echo "Re-signing with identifier-based designated requirement..."

codesign --force --sign - \
    --identifier "$IDENTIFIER" \
    --entitlements "$ENTITLEMENTS" \
    --options runtime \
    -r="designated => identifier \"$IDENTIFIER\"" \
    "$BINARY"

codesign --force --sign - \
    --identifier "$IDENTIFIER" \
    --entitlements "$ENTITLEMENTS" \
    --options runtime \
    -r="designated => identifier \"$IDENTIFIER\"" \
    "$APP"

echo "Verifying signature..."
codesign -dvv "$APP" 2>&1 | grep -E "Identifier|Info.plist|Internal requirements"
codesign -d -r- "$APP" 2>&1 | grep "designated"

# Tauri creates the DMG before this script runs, so it ships the original
# cdhash-based signature regardless of the re-sign above. Repackage the
# now-correctly-signed .app into a fresh DMG, with an /Applications symlink
# next to it so users can drag-to-install.
echo "Repackaging DMG with the re-signed .app..."
mkdir -p "$(dirname "$DMG")"
rm -f "$DMG"

STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING"' EXIT
cp -R "$APP" "$STAGING/"
ln -s /Applications "$STAGING/Applications"

hdiutil create -volname "$PRODUCT" -srcfolder "$STAGING" -ov -format UDZO "$DMG" >/dev/null

echo "Done."
echo "  App: $APP"
echo "  DMG: $DMG"
