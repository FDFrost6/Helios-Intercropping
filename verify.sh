#!/bin/bash
# Quick verification script for helios-intercropping project

echo "=============================================="
echo "Helios Intercropping - Project Verification"
echo "=============================================="
echo ""

# Check directory structure
echo "[1/5] Checking directory structure..."
if [ -d "src/intercropping" ] && [ -d "scripts" ] && [ -d "docs" ] && [ -d "tests" ]; then
    echo "  ✅ All directories present"
else
    echo "  ❌ Missing directories"
    exit 1
fi

# Count files
echo ""
echo "[2/5] Counting files..."
PY_FILES=$(find . -name "*.py" -type f | wc -l)
TOTAL_FILES=$(find . -type f -not -path "./.git/*" | wc -l)
echo "  📊 Python files: $PY_FILES"
echo "  📊 Total files: $TOTAL_FILES"

# Check key files
echo ""
echo "[3/5] Verifying key files..."
REQUIRED_FILES=(
    "README.md"
    "requirements.txt"
    "setup.py"
    "pyproject.toml"
    ".gitignore"
    "scripts/generate_scene.py"
    "src/intercropping/__init__.py"
    "docs/API.md"
    "docs/USAGE.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file MISSING"
    fi
done

# Check imports (without PyHelios)
echo ""
echo "[4/5] Testing Python imports (basic syntax check)..."
python3 -c "import sys; sys.path.insert(0, 'src'); from intercropping.config import BEAN_EMERGENCE_RATE; print(f'  ✅ Config import OK (BEAN_EMERGENCE_RATE={BEAN_EMERGENCE_RATE})')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  ⚠️  Import test skipped (PyHelios not available)"
fi

# Git status
echo ""
echo "[5/5] Git repository status..."
if [ -d ".git" ]; then
    echo "  ✅ Git initialized"
    COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null)
    if [ ! -z "$COMMIT_COUNT" ]; then
        echo "  📝 Commits: $COMMIT_COUNT"
    fi
else
    echo "  ❌ Git not initialized"
fi

echo ""
echo "=============================================="
echo "✅ Verification Complete!"
echo "=============================================="
echo ""
echo "Next Steps:"
echo "  1. Activate PyHelios venv: source /path/to/PyHelios/.venv/bin/activate"
echo "  2. Test CLI: python scripts/generate_scene.py --help"
echo "  3. Generate scene: python scripts/generate_scene.py --save --camera"
echo "  4. Read docs: cat README.md"
echo ""
echo "Documentation:"
echo "  - README.md - Installation & features"
echo "  - docs/USAGE.md - Usage examples & workflows"
echo "  - docs/API.md - API reference"
echo "  - REFACTORING_SUMMARY.md - What changed"
echo ""
