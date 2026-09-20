#!/usr/bin/env bash
set -e

# ==============================================================================
# Build Script for CashflowTracking Android APK
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "==> Preparing build environment..."
if [ -z "$ANDROID_HOME" ]; then
    if [ -d "$HOME/.buildozer/android/platform/android-sdk" ]; then
        export ANDROID_HOME="$HOME/.buildozer/android/platform/android-sdk"
    elif [ -d "$HOME/Android/Sdk" ]; then
        export ANDROID_HOME="$HOME/Android/Sdk"
    fi
fi

echo "Using ANDROID_HOME: $ANDROID_HOME"

# Ensure custom template files are synchronized before build
if [ -d "$SCRIPT_DIR/template/android" ] && [ -d "$SCRIPT_DIR/build/flutter/android" ]; then
    echo "==> Syncing native Android notification service..."
    cp -r "$SCRIPT_DIR/template/android/app/src/main/"* "$SCRIPT_DIR/build/flutter/android/app/src/main/"
fi

# Run Flet build
echo "==> Building APK with Flet..."
cd "$ROOT_DIR"
"$SCRIPT_DIR/.venv/bin/flet" build apk apps \
    --project "CashflowTracking" \
    --org "com.cashflowtracking" \
    --yes

# If fresh build just created flutter dir, re-apply template and finish
if [ -f "$SCRIPT_DIR/template/android/app/src/main/kotlin/com/cashflowtracking/cashflowtracking/BankNotificationListener.kt" ]; then
    if [ ! -f "$SCRIPT_DIR/build/flutter/android/app/src/main/kotlin/com/cashflowtracking/cashflowtracking/BankNotificationListener.kt" ]; then
        echo "==> Applying native listener to newly created shell..."
        cp -r "$SCRIPT_DIR/template/android/app/src/main/"* "$SCRIPT_DIR/build/flutter/android/app/src/main/"
        "$SCRIPT_DIR/.venv/bin/flet" build apk apps --project "CashflowTracking" --org "com.cashflowtracking" --yes
    fi
fi

echo "==> Build complete: $SCRIPT_DIR/build/apk/CashflowTracking.apk"
