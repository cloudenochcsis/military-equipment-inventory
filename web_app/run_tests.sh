#!/bin/bash
# Run all tests with coverage and generate report

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Military Equipment Inventory System   ${NC}"
echo -e "${BLUE}          Test Runner Script            ${NC}"
echo -e "${BLUE}=========================================${NC}"

# Ensure we're in the web_app directory
cd "$(dirname "$0")"

# Check if coverage is installed
if ! python -m pip show coverage > /dev/null; then
    echo -e "${YELLOW}Coverage package not found. Installing...${NC}"
    python -m pip install coverage
fi

# Run the tests with coverage
echo -e "${BLUE}Running tests with coverage...${NC}"
coverage run --source=. manage.py test --settings=inventory_project.settings

# Check if tests passed
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed successfully!${NC}"
    
    # Generate coverage report
    echo -e "${BLUE}Generating coverage report...${NC}"
    coverage report -m
    
    # Generate HTML report
    echo -e "${BLUE}Generating HTML coverage report...${NC}"
    coverage html
    
    echo -e "${GREEN}Coverage report generated in htmlcov/ directory${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"
    echo -e "${BLUE}To view detailed HTML report, open:${NC}"
    echo -e "${GREEN}htmlcov/index.html${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"
else
    echo -e "${RED}✗ Some tests failed. Fix the issues before generating coverage report.${NC}"
fi
