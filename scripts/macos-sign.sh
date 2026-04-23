#!/bin/bash
set -euo pipefail

APP="src-tauri/target/release/bundle/macos/Translator.app"
BINARY="$APP/Contents/MacOS/crkt-tauri"
ENTITLEMENTS="src-tauri/Entitlements.plist"
IDENTIFIER="com.crkt.translator"

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

echo "Done."
