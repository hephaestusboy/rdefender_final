#!/bin/bash
# R-Defender Linux Build Preparation Script
# Prepares the project for Windows packaging on Linux

set -e

echo ""
echo "🛡️  R-DEFENDER LINUX BUILD PREPARATION  (v6)"
echo "============================================="
echo ""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

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

echo "Checking for model files..."
MODELS=(
    "rf_behavior_model_v6.joblib"
    "rf_artifact_model_v6.joblib"
    "xgb_behavior_model_v6.joblib"
    "xgb_artifact_model_v6.joblib"
    "fusion_model_v6.joblib"
    "thresholds_v6.json"
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
echo "============================================="
echo -e "${GREEN}✅ All checks passed!${NC}"
echo "============================================="
echo ""

echo "What would you like to do?"
echo ""
echo "1. View preparation summary"
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
        echo "✅ R-Defender v6 project is ready for packaging!"
        echo ""
        echo "Files to transfer to Windows:"
        echo "  Models (5):  rf/xgb behavior+artifact _v6.joblib + fusion_model_v6.joblib"
        echo "  Config (1):  thresholds_v6.json"
        echo "  Python (6):  rdefender_ui_clr_copy.py  rdefender_agent.py"
        echo "               static_feature_extractor.py  feature_vectorizer.py"
        echo "               model_feature_groups.py  feature_schema.py"
        echo "  Build  (4):  build_config.spec  installer.nsi  build.py  build_requirements.txt"
        echo "  Deps   (1):  requirements.txt"
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
        echo "Transfer this file to Windows and extract it"
        echo ""
        ;;
    4)
        echo ""
        echo -e "${BLUE}📋 WINDOWS DEPLOYMENT CHECKLIST${NC}"
        echo ""
        echo "Model files (5 + 1 threshold):"
        echo "  ☐ rf_behavior_model_v6.joblib"
        echo "  ☐ rf_artifact_model_v6.joblib"
        echo "  ☐ xgb_behavior_model_v6.joblib"
        echo "  ☐ xgb_artifact_model_v6.joblib"
        echo "  ☐ fusion_model_v6.joblib"
        echo "  ☐ thresholds_v6.json"
        echo ""
        echo "Python files:"
        echo "  ☐ rdefender_ui_clr_copy.py  rdefender_agent.py"
        echo "  ☐ static_feature_extractor.py  feature_vectorizer.py"
        echo "  ☐ model_feature_groups.py  feature_schema.py"
        echo ""
        echo "On Windows:"
        echo "  ☐ Python 3.8+ installed and in PATH"
        echo "  ☐ NSIS installed (https://nsis.sourceforge.io/Download)"
        echo "  ☐ pip install -r build_requirements.txt"
        echo "  ☐ pip install -r requirements.txt"
        echo "  ☐ python build.py"
        echo ""
        echo "Result: RDefender-Setup.exe (~200 MB, no lgbm/catboost)"
        echo ""
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
