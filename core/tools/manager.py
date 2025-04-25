"""
Tools Manager for handling various system operations like opening websites and applications.
"""

import os
import logging
import webbrowser
import subprocess
from typing import Dict, Any, Optional
import platform

logger = logging.getLogger(__name__)

class ToolManager:
    """Manages various system tools and operations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the tools manager."""
        self.config = config
        self.logger = logger
        self.system = platform.system().lower()
        
        # Common application paths
        self.app_paths = {
            'windows': {
                'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                'firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe',
                'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                'notepad': r'C:\Windows\System32\notepad.exe',
                'calculator': r'C:\Windows\System32\calc.exe',
                'explorer': r'C:\Windows\explorer.exe'
            },
            'darwin': {  # macOS
                'chrome': '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                'firefox': '/Applications/Firefox.app/Contents/MacOS/firefox',
                'safari': '/Applications/Safari.app/Contents/MacOS/Safari',
                'calculator': '/Applications/Calculator.app/Contents/MacOS/Calculator',
                'finder': '/System/Library/CoreServices/Finder.app/Contents/MacOS/Finder'
            },
            'linux': {
                'chrome': '/usr/bin/google-chrome',
                'firefox': '/usr/bin/firefox',
                'calculator': '/usr/bin/gnome-calculator',
                'file_manager': '/usr/bin/nautilus'
            }
        }
        
    async def initialize(self):
        """Initialize the tools manager."""
        self.logger.info("Initializing tools manager...")
        # Verify common applications exist
        for app, path in self.app_paths.get(self.system, {}).items():
            if os.path.exists(path):
                self.logger.info(f"Found {app} at {path}")
            else:
                self.logger.warning(f"Could not find {app} at {path}")
    
    async def open_website(self, url: str) -> bool:
        """
        Open a website in the default browser.
        
        Args:
            url: The URL to open
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure URL has proper format
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            self.logger.info(f"Opening website: {url}")
            webbrowser.open(url)
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening website: {str(e)}")
            return False
    
    async def open_application(self, app_name: str) -> bool:
        """
        Open a system application.
        
        Args:
            app_name: Name of the application to open
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the path for the application
            app_path = self.app_paths.get(self.system, {}).get(app_name.lower())
            
            if not app_path:
                self.logger.error(f"Application {app_name} not found in configuration")
                return False
                
            if not os.path.exists(app_path):
                self.logger.error(f"Application path does not exist: {app_path}")
                return False
                
            self.logger.info(f"Opening application: {app_name}")
            
            # Open the application
            if self.system == 'windows':
                subprocess.Popen([app_path], shell=True)
            else:
                subprocess.Popen([app_path])
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening application: {str(e)}")
            return False
    
    async def execute_command(self, command: str) -> bool:
        """
        Execute a system command.
        
        Args:
            command: The command to execute
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Executing command: {command}")
            subprocess.run(command, shell=True, check=True)
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing command: {str(e)}")
            return False
    
    async def shutdown(self):
        """Clean up resources."""
        self.logger.info("Shutting down tools manager...") 