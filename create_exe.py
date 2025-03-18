import os
import subprocess
import sys

def create_executable():
    """Create a standalone executable using PyInstaller."""
    try:
        # Check if PyInstaller is installed
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    print("Creating executable with PyInstaller...")
    subprocess.check_call([
        sys.executable, 
        "-m", 
        "PyInstaller", 
        "--onefile", 
        "--name", 
        "wifi_scanner",
        "--icon", 
        "NONE", 
        "scanner.py"
    ])
    
    print("\nExecutable created successfully!")
    print("You can find it in the 'dist' folder.")

if __name__ == "__main__":
    create_executable() 