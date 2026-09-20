#!/usr/bin/env bash
set -e

# ==============================================================================
# Build Script for CashflowTracking Android APK
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
ROOT_DIR="$(dirname "$APP_DIR")"

echo "==> Preparing build environment..."

if [ -z "$ANDROID_HOME" ]; then
    if [ -d "$HOME/.buildozer/android/platform/android-sdk" ]; then
        export ANDROID_HOME="$HOME/.buildozer/android/platform/android-sdk"
    elif [ -d "$HOME/Android/Sdk" ]; then
        export ANDROID_HOME="$HOME/Android/Sdk"
    fi
fi

echo "Using ANDROID_HOME: $ANDROID_HOME"

# ==============================================================================
# Sync native Android template if Flutter shell already exists
# ==============================================================================

if [ -d "$APP_DIR/template/android" ] && [ -d "$APP_DIR/build/flutter/android" ]; then
    echo "==> Syncing native Android notification service..."

    cp -r \
        "$APP_DIR/template/android/app/src/main/"* \
        "$APP_DIR/build/flutter/android/app/src/main/"
fi

# ==============================================================================
# Run Flet build
# ==============================================================================

echo "==> Building APK with Flet..."

cd "$ROOT_DIR"

"$APP_DIR/.venv/bin/flet" build apk apps \
    --project "CashflowTracking" \
    --org "com.cashflowtracking" \
    --yes

# ==============================================================================
# Re-apply native listener if fresh Flutter shell was created
# ==============================================================================

LISTENER="$APP_DIR/template/android/app/src/main/kotlin/com/cashflowtracking/cashflowtracking/BankNotificationListener.kt"

GENERATED_LISTENER="$APP_DIR/build/flutter/android/app/src/main/kotlin/com/cashflowtracking/cashflowtracking/BankNotificationListener.kt"

if [ -f "$LISTENER" ]; then

    if [ ! -f "$GENERATED_LISTENER" ]; then

        echo "==> Applying native listener to newly created shell..."

        cp -r \
            "$APP_DIR/template/android/app/src/main/"* \
            "$APP_DIR/build/flutter/android/app/src/main/"

        echo "==> Rebuilding APK..."

        "$APP_DIR/.venv/bin/flet" build apk apps \
            --project "CashflowTracking" \
            --org "com.cashflowtracking" \
            --yes
    fi
fi

echo "==> Build complete:"
echo "    $APP_DIR/build/apk/CashflowTracking.apk"