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

echo "==> Packaging and building with Flet..."

cd "$ROOT_DIR"

# Pre-sync to flutter shell if it exists
if [ -d "$APP_DIR/template/android" ] && [ -d "$APP_DIR/build/flutter/android" ]; then
    echo "==> Syncing native Android template files..."
    cp -r "$APP_DIR/template/android/app/src/main/"* "$APP_DIR/build/flutter/android/app/src/main/"
fi

# We build using flet build, and ensure the native code is compiled into the APK
"$APP_DIR/.venv/bin/flet" build apk apps \
    --project "CashflowTracking" \
    --org "com.cashflowtracking" \
    --yes

# Now re-apply native files and do a direct flutter build inside apps/build/flutter
# to guarantee that custom MainActivity.kt and BankNotificationListener.kt are included
echo "==> Applying native files and compiling native code into final APK..."
cp -r "$APP_DIR/template/android/app/src/main/"* "$APP_DIR/build/flutter/android/app/src/main/"

cd "$APP_DIR/build/flutter"
export SERIOUS_PYTHON_SITE_PACKAGES="$APP_DIR/build/site-packages"
export SERIOUS_PYTHON_APP="$APP_DIR/build/python-app"

flutter build apk --release

# Copy generated apk to apps/build/apk/
mkdir -p "$APP_DIR/build/apk"
cp "$APP_DIR/build/flutter/build/app/outputs/flutter-apk/app-release.apk" "$APP_DIR/build/apk/CashflowTracking.apk"


echo "==> Build complete:"
echo "    $APP_DIR/build/apk/CashflowTracking.apk"