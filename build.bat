@echo off
chcp 65001 > nul
cls

:: Check if running with administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    :: If running with administrator privileges, create virtual environment and then run with normal user privileges
    if not exist venv (
        echo ℹ️ 正在創建虛擬環境...
        python -m venv venv
    )
    
    :: Run remaining steps with normal user privileges
    echo ℹ️ 以普通用戶權限繼續...
    powershell -Command "Start-Process -FilePath '%comspec%' -ArgumentList '/c cd /d %cd% && %~f0 run' -Verb RunAs:NO"
    exit /b
) else (
    :: Check if running in second stage
    if "%1"=="run" (
        goto RUN_BUILD
    ) else (
        :: If running with normal privileges and creating virtual environment is required, request administrator privileges
        if not exist venv (
            echo ⚠️ Requires administrator privileges to create virtual environment
            echo ℹ️ Requesting administrator privileges...
            powershell -Command "Start-Process -Verb RunAs -FilePath '%comspec%' -ArgumentList '/c cd /d %cd% && %~f0'"
            exit /b
        ) else (
            goto RUN_BUILD
        )
    )
)

:RUN_BUILD
echo ℹ️ Starting virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to start virtual environment
    pause
    exit /b 1
)

:: Check and install missing dependencies
echo ℹ️ Checking dependencies...
for /f "tokens=1" %%i in (requirements.txt) do (
    pip show %%i >nul 2>&1 || (
        echo ℹ️ Installing %%i...
        pip install %%i
    )
)

echo ℹ️ Starting build...
python build.py
if errorlevel 1 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo ✅ Completed!
pause 