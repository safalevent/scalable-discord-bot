@echo off

REM Check if Python 3.10 is installed
python --version 2>NUL | findstr /C:"Python 3.10" >NUL
if %errorlevel% NEQ 0 (
    echo Python 3.10 is not installed. Installing...
    REM Download Python 3.10 installer (adjust the URL if needed)
    curl -L -o python310.msi https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe

    REM Install Python 3.10 silently
    msiexec /i python310.msi /qn

    REM Delete the installer file
    del python310.msi

    echo Python 3.10 has been installed.
) else (
    echo Python 3.10 is already installed.
)

pause
