@echo off
REM Setup environment variables for Jarvis

if not exist ".env" (
    echo GROQ_API_KEY=your_api_key_here > .env
    echo Created .env file. Please edit it with your actual API key.
) else (
    echo .env file already exists
)

for /f "tokens=1,* delims==" %%a in (.env) do (
    if not "%%a"=="" if not "%%b"=="" (
        setx %%a %%b
        set %%a=%%b
    )
)

echo Environment variables have been set.
echo Please restart your terminal for changes to take effect. 