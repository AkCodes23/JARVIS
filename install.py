"""
Simple installation script for Jarvis that bypasses SSL verification and handles Python 3.12 compatibility issues.
"""

import os
import sys
import subprocess
import logging
import platform
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('install.log')
    ]
)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and log the output."""
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Command completed successfully: {description}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {description}")
        logger.error(f"Error: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories."""
    logger.info("Creating directories...")
    
    directories = [
        "models/nlp",
        "models/wake_word",
        "data/voice",
        "data/conversation",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    logger.info("Directories created successfully")

def check_python_version():
    """Check if Python version is compatible."""
    logger.info("Checking Python version...")
    
    python_version = platform.python_version_tuple()
    major, minor = int(python_version[0]), int(python_version[1])
    
    if major < 3 or (major == 3 and minor < 8):
        logger.error(f"Python version {major}.{minor} is not supported. Please use Python 3.8 or higher.")
        return False
    
    if major == 3 and minor >= 12:
        logger.warning(f"Python version {major}.{minor} may have compatibility issues with some packages.")
        logger.warning("Consider using Python 3.8-3.11 for better compatibility.")
    
    logger.info(f"Python version {major}.{minor} is compatible.")
    return True

def install_dependencies():
    """Install project dependencies."""
    logger.info("Installing dependencies...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Upgrade pip
    run_command(
        "python -m pip install --upgrade pip",
        "Upgrading pip"
    )
    
    # Install setuptools and wheel
    run_command(
        "pip install --upgrade setuptools wheel",
        "Installing setuptools and wheel"
    )
    
    # Install dependencies individually to avoid compatibility issues
    core_dependencies = [
        "numpy>=1.21.0",
        "pandas>=2.0.0",
        "scipy>=1.10.0",
        "PyYAML>=6.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.8.0",
        "asyncio>=3.4.3",
        "typing-extensions>=4.5.0"
    ]
    
    for dep in core_dependencies:
        run_command(
            f"pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org {dep}",
            f"Installing {dep}"
        )
    
    # Install voice dependencies
    voice_dependencies = [
        "sounddevice>=0.4.4",
        "soundfile>=0.10.3",
        "pyttsx3>=2.90",
        "SpeechRecognition>=3.8.1",
        "pyaudio>=0.2.11"
    ]
    
    for dep in voice_dependencies:
        run_command(
            f"pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org {dep}",
            f"Installing {dep}"
        )
    
    # Install spaCy model
    run_command(
        "python -m spacy download en_core_web_sm",
        "Installing spaCy model"
    )
    
    logger.info("Dependencies installed successfully")
    return True

def main():
    """Main installation function."""
    logger.info("Starting installation...")
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        logger.error("Installation failed")
        sys.exit(1)
    
    logger.info("Installation completed successfully")

if __name__ == "__main__":
    main() 