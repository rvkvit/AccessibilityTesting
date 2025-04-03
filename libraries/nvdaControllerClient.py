"""
NVDA Controller Client

This module provides direct communication with NVDA screen reader
through Windows API calls to directly connect to the running NVDA process.
"""
import ctypes
import os
import sys
import subprocess
import time
from robot.api import logger

# Constants for Windows API
WM_COPYDATA = 0x004A
HWND_BROADCAST = 0xFFFF

# Define NVDA message constants
NVDA_ADDR = os.getenv('NVDA_ADDR', '127.0.0.1')
NVDA_PORT = int(os.getenv('NVDA_PORT', '25432'))
NVDA_FIND_WINDOW_NAME = "NVDA"
COPYDATA_GET_LAST_SPEECH = 1
COPYDATA_SPEAK_TEXT = 2
COPYDATA_CANCEL_SPEECH = 3
COPYDATA_SILENCE_SPEECH = 4
COPYDATA_BRAILLE_TEXT = 5

# Load the user32.dll library for Windows API functions
try:
    user32 = ctypes.windll.user32
except Exception as e:
    logger.error(f"Failed to load user32.dll: {e}")
    user32 = None

# Define the COPYDATASTRUCT structure for WM_COPYDATA
class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [
        ("dwData", ctypes.c_ulonglong),
        ("cbData", ctypes.c_ulong),
        ("lpData", ctypes.c_void_p)
    ]

def start_nvda():
    """
    Attempts to start NVDA if it's not already running.
    
    Returns:
        True if NVDA was started successfully, False otherwise
    """
    # Check common NVDA paths
    nvda_paths = [
        r"C:\Program Files (x86)\NVDA\nvda.exe",
        r"C:\Program Files\NVDA\nvda.exe"
    ]
    
    for nvda_path in nvda_paths:
        if os.path.exists(nvda_path):
            try:
                logger.info(f"Attempting to start NVDA from {nvda_path}")
                # Start NVDA as a subprocess
                subprocess.Popen([nvda_path])
                # Give NVDA some time to start
                time.sleep(5)
                # Check if NVDA is now running
                if find_nvda_window():
                    logger.info("Successfully started NVDA")
                    return True
            except Exception as e:
                logger.error(f"Error starting NVDA: {e}")
    
    logger.warn("Could not start NVDA automatically")
    return False

def find_nvda_window():
    """Find the NVDA main window handle."""
    if not user32:
        logger.error("user32.dll not loaded")
        return None
        
    # Try to find NVDA window by class name
    hwnd = user32.FindWindowA(b"wxWindowClassNR", b"NVDA")
    
    if not hwnd:
        # Try by window title
        hwnd = user32.FindWindowA(None, b"NVDA")
    
    if not hwnd:
        logger.warn("Could not find NVDA window handle")
    else:
        logger.info(f"Found NVDA window handle: {hwnd}")
        
    return hwnd

def send_message_to_nvda(message_id, data=None):
    """
    Send a message to NVDA.
    
    Args:
        message_id: Type of message to send
        data: String data to send with the message
        
    Returns:
        True if successful, False otherwise
    """
    try:
        hwnd = find_nvda_window()
        if not hwnd:
            return False
            
        if data:
            data_bytes = data.encode('utf-8')
            buffer = ctypes.create_string_buffer(data_bytes)
            cds = COPYDATASTRUCT()
            cds.dwData = message_id
            cds.cbData = len(data_bytes) + 1  # Include null terminator
            cds.lpData = ctypes.cast(buffer, ctypes.c_void_p)
            
            result = user32.SendMessageA(hwnd, WM_COPYDATA, 0, ctypes.byref(cds))
        else:
            result = user32.SendMessageA(hwnd, WM_COPYDATA, 0, message_id)
            
        if result:
            return True
        else:
            logger.warn(f"Failed to send message {message_id} to NVDA")
            return False
    except Exception as e:
        logger.error(f"Error sending message to NVDA: {e}")
        return False

def nvdaController_testIfRunning():
    """
    Tests if NVDA is running.
    Returns True if running, raises an exception if not.
    """
    hwnd = find_nvda_window()
    if hwnd:
        logger.info("NVDA is running")
        return True
    else:
        # Try to start NVDA
        if start_nvda():
            return True
        raise RuntimeError("NVDA is not running and could not be started")

def nvdaController_speakText(text):
    """
    Speaks the given text through NVDA.
    
    Args:
        text: The text to speak
        
    Returns:
        True if successful, False otherwise
    """
    if not text:
        return False
        
    logger.info(f"Speaking through NVDA: {text}")
    return send_message_to_nvda(COPYDATA_SPEAK_TEXT, text)

def nvdaController_cancelSpeech():
    """
    Cancels speech in NVDA.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("Cancelling NVDA speech")
    return send_message_to_nvda(COPYDATA_CANCEL_SPEECH)

def nvdaController_brailleMessage(message):
    """
    Displays a message on the braille display.
    
    Args:
        message: The message to display
        
    Returns:
        True if successful, False otherwise
    """
    if not message:
        return False
        
    logger.info(f"Sending message to NVDA braille display: {message}")
    return send_message_to_nvda(COPYDATA_BRAILLE_TEXT, message) 