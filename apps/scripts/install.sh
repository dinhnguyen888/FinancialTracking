#!/usr/bin/env bash
set -e

# ==============================================================================
# Install CashflowTracking APK to connected Android device
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

APK_PATH="$APP_DIR/build/apk/CashflowTracking.apk"
PACKAGE_NAME="com.cashflowtracking.cashflowtracking"

echo "==> Checking ADB..."

if ! command -v adb >/dev/null 2>&1; then
    echo "ERROR: adb not found in PATH."
    exit 1
fi

echo "==> Starting ADB server..."
adb start-server

DEVICE_COUNT=$(adb devices | awk 'NR > 1 && $2 == "device" { count++ } END { print count+0 }')

if [ "$DEVICE_COUNT" -eq 0 ]; then
    echo "ERROR: No Android device connected."
    exit 1
fi

if [ "$DEVICE_COUNT" -gt 1 ]; then
    echo "ERROR: Multiple Android devices detected:"
    adb devices
    exit 1
fi

DEVICE_ID=$(adb devices | awk 'NR > 1 && $2 == "device" { print $1 }')

echo "==> Device: $DEVICE_ID"

if [ ! -f "$APK_PATH" ]; then
    echo "ERROR: APK not found:"
    echo "  $APK_PATH"
    exit 1
fi

echo "==> APK: $APK_PATH"

echo "==> Installing APK..."

adb -s "$DEVICE_ID" install -r "$APK_PATH"

echo "==> Installation complete."

echo "==> Launching CashflowTracking..."

adb -s "$DEVICE_ID" shell monkey \
    -p "$PACKAGE_NAME" \
    -c android.intent.category.LAUNCHER \
    1 >/dev/null 2>&1 || true

echo "==> Done."