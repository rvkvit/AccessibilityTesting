#!/usr/bin/env python3
"""
Script to run accessibility tests with screen reader integration.
Automatically uses NVDA on Windows and VoiceOver on macOS.
"""
import os
import sys
import argparse
import subprocess
import platform
from pathlib import Path

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run Robot Framework accessibility tests")
    parser.add_argument("--browser", default="chromium", 
                        choices=["chromium", "firefox", "webkit"],
                        help="Browser to use for testing")
    parser.add_argument("--headless", action="store_true",
                        help="Run browser in headless mode")
    parser.add_argument("--url", default="https://www.google.com",
                        help="URL to test")
    parser.add_argument("--use-screen-reader", action="store_true",
                        help="Attempt to use actual screen reader (NVDA on Windows, VoiceOver on macOS)")
    parser.add_argument("--test", default="tests/accessibility_tests.robot",
                        help="Test file to run")
    parser.add_argument("--output-dir", default="results",
                        help="Directory for test results")
    return parser.parse_args()

def initialize_browser_library():
    """Initialize the Robot Framework Browser library."""
    print("Initializing Browser library...")
    try:
        result = subprocess.run(["rfbrowser", "init"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               check=True,
                               text=True)
        print("Browser library initialized successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to initialize Browser library: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("rfbrowser command not found. Make sure Robot Framework Browser library is installed.")
        print("Run: pip install robotframework-browser && rfbrowser init")
        return False

def check_and_start_screen_reader(use_screen_reader):
    """Check and start the appropriate screen reader based on the OS."""
    if not use_screen_reader:
        print("Screen reader integration disabled, will use simulation mode.")
        return True
    
    system = platform.system()
    tools_dir = Path(__file__).parent / "tools"
    screen_reader_control = tools_dir / "nvda_control.py"
    
    if not screen_reader_control.exists():
        print(f"Screen reader control script not found at: {screen_reader_control}")
        return False
    
    try:
        # Check if screen reader is already running
        status_proc = subprocess.run([sys.executable, str(screen_reader_control), "status"],
                                    stdout=subprocess.PIPE,
                                    text=True)
        
        if "not running" in status_proc.stdout:
            # Start screen reader
            reader_name = "NVDA" if system == "Windows" else "VoiceOver"
            print(f"Starting {reader_name}...")
            start_proc = subprocess.run([sys.executable, str(screen_reader_control), "start"],
                                       stdout=subprocess.PIPE,
                                       text=True)
            if "successfully started" in start_proc.stdout:
                print(f"{reader_name} started successfully.")
                return True
            else:
                print(f"Failed to start {reader_name}. Will use simulation mode.")
                return False
        else:
            reader_name = "NVDA" if system == "Windows" else "VoiceOver"
            print(f"{reader_name} is already running.")
            return True
    except Exception as e:
        print(f"Error controlling screen reader: {str(e)}")
        return False

def run_robot_tests(args):
    """Run Robot Framework tests."""
    test_path = Path(args.test)
    output_dir = Path(args.output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build robot command
    robot_cmd = [
        "robot",
        "--outputdir", str(output_dir),
        "--variable", f"BROWSER:{args.browser}",
        "--variable", f"HEADLESS:{str(args.headless).lower()}",
        "--variable", f"GOOGLE_URL:{args.url}",
        str(test_path)
    ]
    
    print(f"Running tests with command: {' '.join(robot_cmd)}")
    
    try:
        # Run the tests
        subprocess.run(robot_cmd, check=True)
        print(f"Tests completed. Results available in {output_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Test execution failed with exit code: {e.returncode}")
        return False

def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Print OS information
    system = platform.system()
    print(f"Operating System: {system}")
    print(f"Using {'NVDA' if system == 'Windows' else 'VoiceOver'} for screen reader accessibility testing")
    
    # Initialize Browser library if needed
    if not initialize_browser_library():
        return 1
    
    # Check and start screen reader if requested
    check_and_start_screen_reader(args.use_screen_reader)
    
    # Run the tests
    success = run_robot_tests(args)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 