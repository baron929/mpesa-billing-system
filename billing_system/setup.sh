#!/bin/bash
# Wi-Fi Billing System - Setup Script
# This script helps with initial setup and installation

echo "================================"
echo "Wi-Fi Billing System Setup"
echo "================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python installation
echo -e "${YELLOW}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python is installed${NC}"

# Check MySQL installation
echo -e "${YELLOW}Checking MySQL installation...${NC}"
if ! command -v mysql &> /dev/null; then
    echo -e "${YELLOW}MySQL is not installed. Please install MySQL 5.7 or higher.${NC}"
    echo "Visit: https://dev.mysql.com/downloads/mysql/"
else
    echo -e "${GREEN}✓ MySQL is installed${NC}"
fi

echo ""

# Create virtual environment
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
python3 -m venv venv
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${RED}Failed to create virtual environment${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo -e "${GREEN}✓ Virtual environment activated${NC}"

echo ""

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}Failed to install dependencies${NC}"
    exit 1
fi

echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}Please update .env with your database credentials${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Next steps:"
echo "1. Update .env with your MySQL credentials"
echo "2. Create the database:"
echo "   mysql -u root -p < models.sql"
echo "3. Start the Flask backend:"
echo "   python app.py"
echo "4. In another terminal, start Streamlit dashboard:"
echo "   streamlit run dashboard.py"
echo ""
echo "Access the application at: http://localhost:5000"
echo "Access the dashboard at: http://localhost:8501"
echo ""
