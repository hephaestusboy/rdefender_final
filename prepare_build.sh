#!/bin/bash
# R-Defender Linux Build Preparation Script
# Prepares the project for Windows packaging on Linux

set -e

echo ""
echo "🛡️  R-DEFENDER LINUX BUILD PREPARATION"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check requirements
echo "Checking requirements..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller is required but not installed."
    echo "Install with: pip install pyinstaller"
    exit 1
fi

echo "✅ Python 3 and PyInstaller found"
echo ""

# Check for model files
echo "Checking for model files..."
MODELS=(
    "rf_behavior_model_v5.joblib"
    "rf_artifact_model_v5.joblib"
    "xgb_behavior_model_v5.joblib"
    "xgb_artifact_model_v5.joblib"
    "lgbm_behavior_model_v5.joblib"
    "lgbm_artifact_model_v5.joblib"
    "catboost_behavior_model_v5.joblib"
    "catboost_artifact_model_v5.joblib"
    "fusion_model_v5.joblib"
    "thresholds_v5.json"
)

MISSING=0
for model in "${MODELS[@]}"; do
    if [ -f "$model" ]; then
        echo "✅ $model"
    else
        echo "❌ $model (MISSING)"
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -gt 0 ]; then
    echo ""
    echo "❌ Missing $MISSING model file(s). Cannot proceed."
    exit 1
fi

echo ""

# Check for required Python files
echo "Checking Python files..."
PYTHON_FILES=(
    "rdefender_ui_clr_copy.py"
    "rdefender_agent.py"
    "static_feature_extractor.py"
    "feature_vectorizer.py"
    "model_feature_groups.py"
    "feature_schema.py"
)

MISSING=0
for file in "${PYTHON_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (MISSING)"
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -gt 0 ]; then
    echo ""
    echo "❌ Missing $MISSING Python file(s). Cannot proceed."
    exit 1
fi

echo ""
echo "Checking config files..."
CONFIG_FILES=(
    "build_config.spec"
    "installer.nsi"
    "build.py"
    "build_requirements.txt"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (MISSING)"
    fi
done

echo ""
echo "======================================"
echo -e "${GREEN}✅ All checks passed!${NC}"
echo "======================================"
echo ""

# Ask user what they want to do
echo "What would you like to do?"
echo ""
echo "1. View preparation summary (recommended)"
echo "2. Build executable (takes 5-10 minutes)"
echo "3. Create transfer package for Windows"
echo "4. Show deployment checklist"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}📋 PREPARATION SUMMARY${NC}"
        echo ""
        echo "✅ Your R-Defender project is ready for packaging!"
        echo ""
        echo "Next steps:"
        echo "1. Read: PACKAGING_SUMMARY.md"
        echo "2. Read: LINUX_BUILD_INFO.md"
        echo "3. Transfer project to Windows machine"
        echo "4. Follow: WINDOWS_BUILD.md"
        echo ""
        echo "Files to transfer to Windows:"
        echo "- rf/xgb/lgbm/catboost behavior+artifact _v5.joblib (8 files)"
        echo "- fusion_model_v5.joblib"
        echo "- thresholds_v5.json"
        echo "- All .py Python files"
        echo "- build_config.spec"
        echo "- installer.nsi"
        echo "- build.py"
        echo "- build_requirements.txt"
        echo "- requirements.txt"
        echo ""
        ;;
    2)
        echo ""
        echo -e "${YELLOW}⏳ Building executable (this may take 5-10 minutes)...${NC}"
        echo ""
        source virtual/bin/activate 2>/dev/null || true
        pyinstaller build_config.spec --clean
        echo ""
        echo -e "${GREEN}✅ Build complete!${NC}"
        echo ""
        echo "Output folder: dist/RDefender/"
        echo ""
        ;;
    3)
        echo ""
        echo -e "${BLUE}📦 Creating transfer package...${NC}"
        echo ""
        PACKAGE_NAME="RDefender-Windows-Build.tar.gz"
        
        tar --exclude='.git' \
            --exclude='__pycache__' \
            --exclude='build' \
            --exclude='dist' \
            --exclude='*.pyc' \
            --exclude='virtual' \
            -czf "$PACKAGE_NAME" .
        
        SIZE=$(du -h "$PACKAGE_NAME" | cut -f1)
        echo -e "${GREEN}✅ Package created: $PACKAGE_NAME ($SIZE)${NC}"
        echo ""
        echo "Transfer this file to Windows and extract it"
        echo ""
        ;;
    4)
        echo ""
        echo -e "${BLUE}📋 WINDOWS DEPLOYMENT CHECKLIST${NC}"
        echo ""
        echo "Before going to Windows, verify:"
        echo "☐ All 9 .joblib model files present (8 base + 1 fusion)"
        echo "☐ thresholds_v5.json present"
        echo "☐ All 6 Python files present"
        echo "☐ build_config.spec present"
        echo "☐ installer.nsi present"
        echo "☐ build.py present"
        echo "☐ requirements.txt present"
        echo "☐ build_requirements.txt present"
        echo ""
        echo "On Windows, verify:"
        echo "☐ Python 3.8+ installed"
        echo "☐ Python added to PATH"
        echo "☐ NSIS installed"
        echo "☐ All three tools verify (version commands work)"
        echo ""
        echo "Build on Windows:"
        echo "☐ pip install -r build_requirements.txt"
        echo "☐ pip install -r requirements.txt"
        echo "☐ python build.py"
        echo ""
        echo "Result:"
        echo "☐ RDefender-Setup.exe created"
        echo "☐ ~350 MB file ready to distribute"
        echo ""
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "For more information, see:"
echo "- PACKAGING_SUMMARY.md"
echo "- LINUX_BUILD_INFO.md"
echo "- WINDOWS_BUILD.md"
echo ""
