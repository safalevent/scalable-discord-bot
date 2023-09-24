#!/bin/bash
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'
if [ "$EUID" -ne 0 ]; then
  echo -e "{RED}This script must be run with sudo permissions.{NC}"
  exit 1
fi

install_python() {
    PYTHON_RESULT=true
    if ! [ sudo apt install python3.10 ]; then
        PYTHON_RESULT=false
        echo "{YELLOW}Installing python manually. This process will take a while. Please wait...{NC}"
        sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
        wget https://www.python.org/ftp/python/3.10.11/Python-3.10.11.tgz
        tar -xf Python-3.10.*.tgz
        cd Python-3.10.*/
        ./configure --prefix=/usr/local --enable-optimizations --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
        make -j $(nproc)
        sudo make altinstall
        cd ..
        rm -rf Python-3.10.*.tgz
        rm -rf Python-3.10.*
        PYTHON_RESULT=true
    fi
}

print_python_result() {
    if [ "$PYTHON_RESULT" = true ]; then
        echo "{GREEN}Python 3.10 has been installed.{NC}"
    else
        echo "{RED}Python 3.10 hasn't been installed due to errors.{NC}"
    fi
}

upgraded=false
# Check if Python 3.10 is installed
if command -v python3.10 &>/dev/null; then
    echo "{GREEN}Python 3.10 is already installed.{NC}"
elif command -v python3 &>/dev/null; then
    # Check if python3 points to Python 3.10
    if python3 -c 'import sys; exit(0) if sys.version_info >= (3, 10) else exit(1)'; then
        echo "{GREEN}Python 3.10 is already installed (via python3).{NC}"
    else
        echo "{YELLOW}Python 3.10 is not installed. Installing...{NC}"
        sudo apt update && sudo apt upgrade -y
        upgraded=true
        install_python
        print_python_result
    fi
elif command -v python &>/dev/null; then
    # Check if python points to Python 3.10
    if python -c 'import sys; exit(0) if sys.version_info >= (3, 10) else exit(1)'; then
        echo "{GREEN}Python 3.10 is already installed (via python).{NC}"
    else
        echo "{YELLOW}Python 3.10 is not installed. Installing...{NC}"
        sudo apt update && sudo apt upgrade -y
        upgraded=true
        install_python
        print_python_result
    fi
else
    echo "{YELLOW}Python 3.10 is not installed. Installing...{NC}"
    sudo apt update && sudo apt upgrade -y
    upgraded=true
    install_python
    print_python_result
fi

