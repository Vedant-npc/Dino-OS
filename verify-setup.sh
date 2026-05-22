#!/bin/bash
# DINO OS Setup Verification Script

echo ""
echo "╔════════════════════════════════════════╗"
echo "║    DINO OS - Setup Verification        ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Node.js
echo -n "Checking Node.js... "
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo -e "${GREEN}✓${NC} $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js not found"
    echo "  Install from: https://nodejs.org/"
fi

# Check npm
echo -n "Checking npm... "
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    echo -e "${GREEN}✓${NC} $NPM_VERSION"
else
    echo -e "${RED}✗${NC} npm not found"
fi

# Check Python
echo -n "Checking Python... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python not found"
    echo "  Install from: https://python.org/"
fi

# Check Git
echo -n "Checking Git... "
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo -e "${GREEN}✓${NC} $GIT_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Git not found (optional)"
fi

echo ""
echo "Checking project structure..."
echo ""

# Check .env file
echo -n "  .env file... "
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} Found"
    # Check for API key
    if grep -q "GEMINI_API_KEY=" .env; then
        if grep -q "GEMINI_API_KEY=your_" .env; then
            echo -e "    ${YELLOW}⚠${NC} API Key not configured"
        else
            echo -e "    ${GREEN}✓${NC} API Key configured"
        fi
    else
        echo -e "    ${RED}✗${NC} API Key not set"
    fi
else
    echo -e "${YELLOW}⚠${NC} Not found"
    echo "    Create from .env.example: cp .env.example .env"
fi

# Check frontend
echo -n "  frontend/node_modules... "
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Installed"
else
    echo -e "${YELLOW}⚠${NC} Not installed (run: cd frontend && npm install)"
fi

# Check backend venv
echo -n "  backend/venv... "
if [ -d "backend/venv" ]; then
    echo -e "${GREEN}✓${NC} Created"
else
    echo -e "${YELLOW}⚠${NC} Not created"
fi

echo ""
echo "Checking ports availability..."
echo ""

# Check port 3000
echo -n "  Port 3000 (Frontend)... "
if ! lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Available"
else
    echo -e "${YELLOW}⚠${NC} In use (kill with: lsof -ti:3000 | xargs kill -9)"
fi

# Check port 8000
echo -n "  Port 8000 (Backend)... "
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Available"
else
    echo -e "${YELLOW}⚠${NC} In use (kill with: lsof -ti:8000 | xargs kill -9)"
fi

echo ""
echo "═══════════════════════════════════════"
echo "Setup verification complete!"
echo ""
echo "Next steps:"
echo "  1. Configure .env with your Gemini API key"
echo "  2. Install dependencies:"
echo "     • cd frontend && npm install"
echo "     • cd backend && pip install -r requirements.txt"
echo "  3. Start the application:"
echo "     • On macOS/Linux: ./start-dino.sh"
echo "     • On Windows: start-dino.bat"
echo ""
echo "Documentation:"
echo "  • QUICKSTART.md - 5-minute setup"
echo "  • README.md - Full documentation"
echo "  • DEVELOPER.md - Development guide"
echo ""
echo "═══════════════════════════════════════"
