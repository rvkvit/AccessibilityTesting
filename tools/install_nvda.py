import os
import sys
import platform
import subprocess
import urllib.request
import zipfile
import shutil

def download_nvda_package():
    """
    Downloads and installs the NVDA package for Windows.
    """
    if platform.system() != "Windows":
        print("This script is only for Windows systems.")
        sys.exit(1)

    # Create tools directory if it doesn't exist
    os.makedirs("tools", exist_ok=True)

    # Download NVDA Controller Client
    nvda_url = "https://www.nvaccess.org/files/nvda/releases/2023.1/nvda_2023.1.exe"
    nvda_installer = os.path.join("tools", "nvda_installer.exe")
    
    print("Downloading NVDA installer...")
    try:
        urllib.request.urlretrieve(nvda_url, nvda_installer)
    except Exception as e:
        print(f"Error downloading NVDA: {e}")
        sys.exit(1)

    print("Installing Python dependencies...")
    pip_command = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    try:
        subprocess.run(pip_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

    print("""
NVDA Setup Instructions:
1. Run the downloaded NVDA installer (tools/nvda_installer.exe)
2. Follow the installation wizard
3. Enable 'Controller Client' in NVDA settings:
   - Open NVDA
   - Press NVDA+N to open the menu
   - Go to Tools -> Remote
   - Check 'Allow this computer to be controlled remotely'
4. Restart NVDA

After completing these steps, you can run the accessibility tests.
""")

if __name__ == "__main__":
    download_nvda_package() 