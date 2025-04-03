import os
import sys
import platform
import subprocess
import urllib.request
import winreg

def check_nvda_installed():
    """
    Check if NVDA is already installed on Windows.
    Returns True if installed, False otherwise.
    """
    try:
        # Try to open NVDA registry key
        winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\NVDA", 0, winreg.KEY_READ)
        return True
    except WindowsError:
        return False

def setup_nvda():
    """
    Sets up NVDA for accessibility testing.
    """
    if platform.system() != "Windows":
        print("This script is only for Windows systems.")
        sys.exit(1)

    nvda_installed = check_nvda_installed()
    
    if nvda_installed:
        print("NVDA is already installed on this system.")
        print("\nPlease ensure the Controller Client is enabled in NVDA:")
        print_nvda_instructions()
    else:
        print("NVDA is not installed. Would you like to download and install it? (y/n)")
        choice = input().lower()
        if choice == 'y':
            download_nvda()
        else:
            print("\nSkipping NVDA installation.")
            print("Please note that NVDA is required for actual screen reader testing.")
            print("You can still run tests in simulation mode without NVDA.")

    print("\nInstalling Python dependencies...")
    install_dependencies()

def download_nvda():
    """
    Downloads the NVDA installer.
    """
    # Create tools directory if it doesn't exist
    os.makedirs("tools", exist_ok=True)

    # Download NVDA Controller Client
    nvda_url = "https://www.nvaccess.org/files/nvda/releases/2023.1/nvda_2023.1.exe"
    nvda_installer = os.path.join("tools", "nvda_installer.exe")
    
    print("Downloading NVDA installer...")
    try:
        urllib.request.urlretrieve(nvda_url, nvda_installer)
        print(f"\nNVDA installer downloaded to: {nvda_installer}")
        print("Please run the installer and follow the installation wizard.")
        print_nvda_instructions()
    except Exception as e:
        print(f"Error downloading NVDA: {e}")
        sys.exit(1)

def install_dependencies():
    """
    Installs required Python dependencies.
    """
    pip_command = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    try:
        subprocess.run(pip_command, check=True)
        print("\nPython dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def print_nvda_instructions():
    """
    Prints instructions for configuring NVDA.
    """
    print("""
NVDA Configuration Instructions:
1. Enable 'Controller Client' in NVDA settings:
   - Open NVDA
   - Press NVDA+N to open the menu
   - Go to Tools -> Remote
   - Check 'Allow this computer to be controlled remotely'
2. Restart NVDA

After completing these steps, you can run the accessibility tests.
""")

if __name__ == "__main__":
    setup_nvda() 