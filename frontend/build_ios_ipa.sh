#!/bin/bash

# Project Eden V2 - iOS IPA Build Script
# Builds Ad Hoc IPA for distribution without USB

echo "🍎 Project Eden V2 - iOS IPA Builder"
echo "===================================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script must run on macOS"
    exit 1
fi

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode is not installed"
    exit 1
fi

echo "📋 Step 1: Clean previous builds..."
flutter clean
echo "✅ Clean complete"
echo ""

echo "📦 Step 2: Get Flutter dependencies..."
flutter pub get
echo "✅ Dependencies ready"
echo ""

echo "🔨 Step 3: Build iOS release..."
flutter build ios --release --no-codesign
echo "✅ iOS build complete"
echo ""

echo "📱 Step 4: Archive with Xcode..."
echo ""
echo "⚠️  MANUAL STEPS REQUIRED:"
echo ""
echo "1. Open Xcode workspace:"
echo "   open ios/Runner.xcworkspace"
echo ""
echo "2. In Xcode:"
echo "   - Select 'Any iOS Device (arm64)' as destination"
echo "   - Product > Archive"
echo "   - Wait for archive to complete"
echo ""
echo "3. In Organizer window (opens automatically):"
echo "   - Click 'Distribute App'"
echo "   - Select 'Ad Hoc'"
echo "   - Click Next > Next"
echo "   - Click 'Export'"
echo "   - Choose save location (Desktop recommended)"
echo ""
echo "4. Find your .ipa file in the export folder"
echo ""
echo "📤 Distribution methods:"
echo "   - AirDrop to iPhone"
echo "   - Email attachment"
echo "   - Cloud storage (Dropbox, iCloud, etc.)"
echo ""
echo "📲 Install on iPhone:"
echo "   1. Open .ipa file on iPhone"
echo "   2. Settings > General > VPN & Device Management"
echo "   3. Trust the developer profile"
echo "   4. App will appear on home screen"
echo ""

# Open Xcode workspace
read -p "Open Xcode now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    open ios/Runner.xcworkspace
    echo "✅ Xcode opened. Follow the manual steps above."
else
    echo "ℹ️  Run 'open ios/Runner.xcworkspace' when ready"
fi

echo ""
echo "🎉 Build script complete!"
