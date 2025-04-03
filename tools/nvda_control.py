#!/usr/bin/env python3
"""
Utility script to start and stop screen readers (NVDA on Windows, VoiceOver on macOS).
"""
import os
import sys
import time
import argparse
import subprocess
import platform

# Default paths for screen readers
SCREEN_READER_PATHS = {
    "Windows": {
        "name": "NVDA",
        "path": "C:\\Program Files (x86)\\NVDA\\nvda.exe"
    },
    "Darwin": {
        "name": "VoiceOver",
        "path": None  # VoiceOver is built into macOS, no path needed
    }
}

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Control screen readers for accessibility testing")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"],
                        help="Action to perform with screen reader")
    parser.add_argument("--path", help="Path to screen reader executable (Windows only)")
    parser.add_argument("--wait", type=int, default=5,
                        help="Seconds to wait after starting the screen reader")
    parser.add_argument("--config", help="Path to screen reader configuration file (Windows/NVDA only)")
    return parser.parse_args()

def is_screen_reader_running():
    """Check if the appropriate screen reader is currently running."""
    system = platform.system()
    try:
        if system == "Windows":
            output = subprocess.check_output("tasklist", shell=True).decode()
            return "nvda.exe" in output
        elif system == "Darwin":  # macOS
            # Check if VoiceOver is running
            output = subprocess.check_output(
                ["osascript", "-e", 'tell application "System Events" to set voStatus to UIElementsEnabled'],
                text=True
            )
            return "true" in output.lower()
        else:  # Linux
            # For Linux, we could check for screen readers like Orca
            return False
    except subprocess.CalledProcessError:
        return False

def start_screen_reader(path=None, config_path=None, wait_time=5):
    """Start the appropriate screen reader."""
    system = platform.system()
    
    if is_screen_reader_running():
        reader_name = SCREEN_READER_PATHS.get(system, {}).get("name", "Screen reader")
        print(f"{reader_name} is already running.")
        return True
        
    try:
        if system == "Windows":
            # For Windows, we use NVDA
            if not path:
                path = SCREEN_READER_PATHS["Windows"]["path"]
                
            if not os.path.exists(path):
                print(f"NVDA executable not found at: {path}")
                return False
                
            cmd = [path]
            if config_path:
                cmd.extend(["--config", config_path])
                
            # Start NVDA
            subprocess.Popen(cmd)
            
        elif system == "Darwin":
            # For macOS, we use VoiceOver
            subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to keystroke "F5" using {control down, option down}'],
                check=True
            )
        else:
            print(f"Starting screen readers on {system} is not supported.")
            return False
            
        print(f"Starting {SCREEN_READER_PATHS.get(system, {}).get('name', 'screen reader')}. Waiting {wait_time} seconds...")
        time.sleep(wait_time)
        
        if is_screen_reader_running():
            print(f"{SCREEN_READER_PATHS.get(system, {}).get('name', 'Screen reader')} successfully started.")
            return True
        else:
            print(f"Failed to start {SCREEN_READER_PATHS.get(system, {}).get('name', 'screen reader')}.")
            return False
    except Exception as e:
        print(f"Error starting screen reader: {str(e)}")
        return False

def stop_screen_reader():
    """Stop the screen reader if it's running."""
    system = platform.system()
    reader_name = SCREEN_READER_PATHS.get(system, {}).get("name", "Screen reader")
    
    try:
        if not is_screen_reader_running():
            print(f"{reader_name} is not running.")
            return True
            
        if system == "Windows":
            subprocess.call("taskkill /f /im nvda.exe", shell=True)
        elif system == "Darwin":
            # Toggle VoiceOver off if it's on
            subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to keystroke "F5" using {control down, option down}'],
                check=True
            )
        else:
            print(f"Stopping screen readers on {system} is not supported.")
            return False
            
        time.sleep(2)
        
        if not is_screen_reader_running():
            print(f"{reader_name} successfully stopped.")
            return True
        else:
            print(f"Failed to stop {reader_name}.")
            return False
    except Exception as e:
        print(f"Error stopping {reader_name}: {str(e)}")
        return False

def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Get system platform
    system = platform.system()
    if system not in SCREEN_READER_PATHS:
        print(f"Unsupported platform: {system}")
        print("This script is designed for Windows (NVDA) and macOS (VoiceOver).")
        return 1
        
    # Use specified path or default
    path = args.path or SCREEN_READER_PATHS.get(system, {}).get("path")
    
    if args.action == "start":
        success = start_screen_reader(path, args.config, args.wait)
    elif args.action == "stop":
        success = stop_screen_reader()
    elif args.action == "restart":
        stop_screen_reader()
        time.sleep(2)
        success = start_screen_reader(path, args.config, args.wait)
    elif args.action == "status":
        reader_name = SCREEN_READER_PATHS.get(system, {}).get("name", "Screen reader")
        if is_screen_reader_running():
            print(f"{reader_name} is currently running.")
            success = True
        else:
            print(f"{reader_name} is not running.")
            success = True
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 