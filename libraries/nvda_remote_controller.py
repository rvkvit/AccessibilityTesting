"""
NVDA Remote Controller

This module connects to NVDA using its remote protocol via TCP/IP.
This requires the NVDA Remote Support add-on to be installed in NVDA.
"""
import socket
import json
import time
import os
import subprocess
from robot.api import logger

# Default NVDA Remote settings
NVDA_HOST = "127.0.0.1"  # localhost
NVDA_PORT = 8765  # Default NVDA Remote port

# Track if we're connected
_connected = False
_socket = None

def ensure_nvda_running():
    """
    Ensure NVDA is running, attempt to start it if not.
    """
    # Check if NVDA process is running
    try:
        output = subprocess.check_output("tasklist /FI \"IMAGENAME eq nvda.exe\"", shell=True)
        if b"nvda.exe" not in output:
            logger.info("NVDA not found in running processes, attempting to start it")
            # Try to start NVDA
            nvda_path = r"C:\Program Files (x86)\NVDA\nvda.exe"
            if os.path.exists(nvda_path):
                subprocess.Popen([nvda_path])
                time.sleep(5)  # Wait for NVDA to start
                return True
            else:
                logger.warn(f"NVDA executable not found at {nvda_path}")
                return False
        return True
    except Exception as e:
        logger.error(f"Error checking/starting NVDA: {e}")
        return False

def connect_to_nvda():
    """
    Connect to NVDA's remote server.
    
    Returns:
        True if successfully connected, False otherwise
    """
    global _connected, _socket
    
    if _connected and _socket:
        return True
        
    try:
        # Ensure NVDA is running
        if not ensure_nvda_running():
            logger.warn("Failed to ensure NVDA is running")
            return False
            
        # Create a socket and connect to NVDA
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.settimeout(5)  # 5 second timeout
        _socket.connect((NVDA_HOST, NVDA_PORT))
        
        # Send authentication if needed
        # This depends on NVDA Remote's configuration
        
        _connected = True
        logger.info(f"Successfully connected to NVDA Remote at {NVDA_HOST}:{NVDA_PORT}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to NVDA Remote: {e}")
        _connected = False
        _socket = None
        return False

def disconnect_from_nvda():
    """
    Disconnect from NVDA Remote.
    """
    global _connected, _socket
    
    if _socket:
        try:
            _socket.close()
        except Exception as e:
            logger.error(f"Error closing NVDA Remote connection: {e}")
        _socket = None
    
    _connected = False

def send_command(command, data=None):
    """
    Send a command to NVDA.
    
    Args:
        command: Command name
        data: Optional data to send with the command
        
    Returns:
        True if successful, False otherwise
    """
    global _connected, _socket
    
    if not _connected:
        if not connect_to_nvda():
            return False
    
    try:
        # Format command
        message = {
            "type": command
        }
        
        if data:
            message.update(data)
            
        # Convert to JSON and send
        msg_json = json.dumps(message)
        _socket.sendall(msg_json.encode('utf-8') + b'\n')
        
        # Wait for response if needed
        # response = _socket.recv(4096).decode('utf-8')
        # logger.info(f"Response: {response}")
        
        return True
    except Exception as e:
        logger.error(f"Error sending command to NVDA: {e}")
        _connected = False
        return False

def nvdaController_testIfRunning():
    """
    Test if NVDA is running and we can connect to it.
    """
    if connect_to_nvda():
        return True
    else:
        raise RuntimeError("Could not connect to NVDA Remote")

def nvdaController_speakText(text):
    """
    Make NVDA speak the given text.
    
    Args:
        text: Text to speak
        
    Returns:
        True if successful, False otherwise
    """
    if not text:
        return False
        
    logger.info(f"Sending text to speak to NVDA: {text}")
    return send_command("speak", {"text": text})

def nvdaController_cancelSpeech():
    """
    Cancel current NVDA speech.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("Cancelling NVDA speech")
    return send_command("cancelSpeech")

def nvdaController_brailleMessage(message):
    """
    Display message on braille display.
    
    Args:
        message: Message to display
        
    Returns:
        True if successful, False otherwise
    """
    if not message:
        return False
        
    logger.info(f"Sending braille message to NVDA: {message}")
    return send_command("braille", {"text": message}) 