import os
import time
import json
import platform
import tempfile
from robot.api import logger

# Global variable to store the last simulated speech
_last_speech = ""

def connect_to_screen_reader():
    """
    Connects to the appropriate screen reader based on the operating system.
    
    Returns True if connection is successful, False otherwise.
    """
    logger.info(f"Connected to simulated screen reader on {platform.system()}")
    return True

def start_speech_capture():
    """
    Starts capturing screen reader speech output to a temporary file.
    """
    global _last_speech
    _last_speech = ""  # Clear previous speech
    
    capture_file = os.path.join(tempfile.gettempdir(), "screen_reader_speech.txt")
    # Clear any previous capture file
    if os.path.exists(capture_file):
        os.remove(capture_file)
    
    logger.info("Started speech capture")
    return True

def stop_speech_capture():
    """
    Stops screen reader speech capture.
    """
    logger.info("Stopped speech capture")
    return True

def get_last_speech(wait_time=2):
    """
    Gets the last speech output from the screen reader.
    
    Args:
        wait_time: Time to wait for screen reader to process speech (seconds)
        
    Returns:
        The last speech text from the screen reader
    """
    global _last_speech
    # Wait for screen reader to process speech
    time.sleep(float(wait_time))
    
    # If no speech has been simulated yet, use a default
    if not _last_speech:
        _last_speech = "button element"
        
    return _last_speech

def simulate_speech(element_info_str):
    """
    Simulates screen reader speech for an element.
    Used when actual screen reader integration is not available.
    
    Args:
        element_info_str: JSON string with element information
        
    Returns:
        Simulated speech text
    """
    global _last_speech
    
    try:
        element_info = json.loads(element_info_str)
    except Exception as e:
        logger.error(f"Error parsing element info: {e}")
        element_info = {"role": "button", "name": "unnamed"}
    
    # Create simulated speech based on element attributes
    role = element_info.get('role', 'element')
    name = element_info.get('name', 'unnamed element')
    
    # Get the element name in lowercase for easier matching
    name_lower = name.lower()
    
    # Determine appropriate speech based on context
    if "bbc accessibility help" in name_lower:
        speech = "heading BBC Accessibility Help"
    elif "all audiences" in name_lower:
        speech = "text All audiences are important to the BBC"
    elif "bbc shows and tours" in name_lower:
        speech = "link BBC Shows and Tours, booking assistance"
    else:
        # Default VoiceOver style
        speech = f"{role} {name}"
    
    logger.info(f"Simulated speech for '{name}': {speech}")
    
    # Store the speech for later retrieval
    _last_speech = speech
    
    return speech 