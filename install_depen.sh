#!/bin/bash

# Ratatouille Environment Setup for Kali Linux
# This script installs all dependencies required for the Ratatouille RAT project

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# Display welcome message with gradient colors
echo -e "${RED}=======${RED}=======${RESET}=======${BLUE}=======${BLUE}=======${RESET}"
echo -e "${RED}W${RED}E${RED}L${RED}C${RESET}O${RESET}M${RESET}E ${RED}T${RED}O ${RED}R${RED}A${RED}T${RED}A${RESET}T${RESET}O${BLUE}U${BLUE}I${BLUE}L${BLUE}L${BLUE}E${RESET}"
echo -e "${RED}=======${RED}=======${RESET}=======${BLUE}=======${BLUE}=======${RESET}"

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo -e "\n${RED}${BOLD}[!] This script requires root privileges.${RESET}"
  echo -e "${RED}${BOLD}[!] Please run with sudo or as root.${RESET}\n"
  exit 1
fi

# Create temp directory
TEMP_DIR="/tmp/dev_setup_$RANDOM"
DESKTOP_PATH="$HOME/Desktop"
LOG_FILE="$TEMP_DIR/setup_log.txt"
mkdir -p "$TEMP_DIR" 2>/dev/null

echo -e "${CYAN}${BOLD}[*] Setting up development environment...${RESET}"
echo -e "${CYAN}[*] Temporary directory: $TEMP_DIR${RESET}"

# Check internet connection
echo -e "${CYAN}${BOLD}[*] Checking internet connection...${RESET}"
if ! ping -c 1 www.google.com >/dev/null 2>&1; then
  echo -e "${RED}${BOLD}[!] No internet connection detected.${RESET}"
  exit 1
fi
echo -e "${GREEN}${BOLD}[+] Internet connection verified.${RESET}"

# Update package lists
echo -e "${CYAN}[*] Updating package lists...${RESET}"
apt update -y
if [ $? -ne 0 ]; then
  echo -e "${RED}${BOLD}[!] Failed to update package lists.${RESET}"
  exit 1
fi
echo -e "${GREEN}[+] Package lists updated.${RESET}"

# Install Python and pip
echo -e "${CYAN}[*] Installing Python and pip...${RESET}"
apt install -y python3 python3-pip python3-venv
if [ $? -ne 0 ]; then
  echo -e "${RED}${BOLD}[!] Failed to install Python.${RESET}"
  exit 1
fi
echo -e "${GREEN}[+] Python installation complete!${RESET}"

# Install development tools
echo -e "${CYAN}[*] Installing development tools...${RESET}"
apt install -y build-essential cmake git libssl-dev libffi-dev python3-dev
if [ $? -ne 0 ]; then
  echo -e "${RED}${BOLD}[!] Failed to install development tools.${RESET}"
  exit 1
fi
echo -e "${GREEN}[+] Development tools installed.${RESET}"

# Install C++ compiler and required libraries
echo -e "${CYAN}[*] Installing C++ compiler and required libraries...${RESET}"
apt install -y g++ libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev
if [ $? -ne 0 ]; then
  echo -e "${RED}${BOLD}[!] Failed to install C++ compiler and libraries.${RESET}"
  exit 1
fi
echo -e "${GREEN}[+] C++ compiler and libraries installed.${RESET}"

# Install Python packages
echo -e "${CYAN}[*] Installing Python packages...${RESET}"
python3 -m pip install --upgrade pip setuptools virtualenv
python3 -m pip install colorama pyinstaller cx_Freeze requests pillow
if [ $? -ne 0 ]; then
  echo -e "${YELLOW}[!] Warning: Some Python packages may not have installed correctly.${RESET}"
else
  echo -e "${GREEN}[+] Python packages installed.${RESET}"
fi

# Create symbolic links for python command
echo -e "${CYAN}[*] Creating symbolic links...${RESET}"
if [ ! -e /usr/bin/python ]; then
  ln -s /usr/bin/python3 /usr/bin/python
fi
echo -e "${GREEN}[+] Symbolic links created.${RESET}"

# Verify installations
echo -e "${CYAN}${BOLD}[*] Verifying installations...${RESET}"

# Verify Python installation
echo -e "${CYAN}[*] Checking Python installation...${RESET}"
PYTHON_VERSION=$(python3 --version)
if [ $? -eq 0 ]; then
  echo -e "${GREEN}[+] $PYTHON_VERSION successfully installed.${RESET}"
else
  echo -e "${RED}[!] Python verification failed. Please check installation.${RESET}"
fi

# Verify G++ installation
echo -e "${CYAN}[*] Checking G++ installation...${RESET}"
GCC_VERSION=$(g++ --version | head -n 1)
if [ $? -eq 0 ]; then
  echo -e "${GREEN}[+] G++ ($GCC_VERSION) successfully installed.${RESET}"
else
  echo -e "${RED}[!] G++ verification failed. Please check installation.${RESET}"
fi

# Make the script executable
echo -e "${CYAN}[*] Making setup_and_run.sh executable...${RESET}"
if [ -f "setup_and_run.sh" ]; then
  chmod +x setup_and_run.sh
  echo -e "${GREEN}[+] setup_and_run.sh is now executable.${RESET}"
else
  echo -e "${YELLOW}[!] setup_and_run.sh not found in current directory.${RESET}"
fi

echo -e "\n${GREEN}${BOLD}[+] Setup complete!${RESET}"
echo -e "${YELLOW}[!] You can now run ./setup_and_run.sh to configure and launch the server.${RESET}"
echo -e "\n${CYAN}[*] This window will close in 10 seconds...${RESET}"

# Countdown timer
for i in {10..1}; do
  echo -e "${CYAN}[*] Closing in $i seconds...${RESET}"
  sleep 1
done

exit 0