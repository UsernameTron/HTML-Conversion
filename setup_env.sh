#!/bin/bash
# Setup script to configure the Python path for the HTML Converter project

# Get the directory where this script is located
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Add the src directory to PYTHONPATH
export PYTHONPATH="${PROJECT_ROOT}/src:${PYTHONPATH}"

echo "✅ Python path configured for HTML Converter project"
echo "📁 Project root: ${PROJECT_ROOT}"
echo "🐍 PYTHONPATH: ${PYTHONPATH}"
echo ""
echo "You can now run:"
echo "  python -m pytest tests/                    # Run tests"
echo "  python comprehensive_tester.py             # Run comprehensive tests"
echo "  streamlit run app.py                       # Start the application"
