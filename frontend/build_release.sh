#!/bin/bash

# Build script for Project Eden V2 - Flutter App
# This script builds release versions of the app

set -e  # Exit on error

echo "🚀 Building Project Eden V2 - Release"
echo "======================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo -e "${RED}❌ Flutter is not installed${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Getting dependencies...${NC}"
flutter pub get

echo -e "${BLUE}🔍 Running code analysis...${NC}"
flutter analyze
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Code analysis failed${NC}"
    exit 1
fi

echo -e "${BLUE}🧪 Running tests...${NC}"
flutter test
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Tests failed${NC}"
    exit 1
fi

echo -e "${BLUE}🔨 Building release APK (Android)...${NC}"
flutter build apk --release
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Android APK built successfully${NC}"
    echo -e "   Location: build/app/outputs/flutter-apk/app-release.apk"
else
    echo -e "${RED}❌ Android build failed${NC}"
fi

echo -e "${BLUE}🔨 Building iOS (if on macOS)...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    flutter build ios --release --no-codesign
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ iOS build successful (not signed)${NC}"
    else
        echo -e "${RED}❌ iOS build failed${NC}"
    fi
else
    echo -e "Skipping iOS build (not on macOS)"
fi

echo ""
echo -e "${GREEN}✅ Build complete!${NC}"
echo ""
echo "Build outputs:"
echo "  - Android APK: build/app/outputs/flutter-apk/app-release.apk"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  - iOS: build/ios/Release-iphoneos/Runner.app"
fi
