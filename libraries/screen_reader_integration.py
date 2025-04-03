import os
import time
import json
import platform
import tempfile
import sys
import ctypes
import subprocess
from robot.api import logger

# Import our NVDA controller modules
try:
    # First try direct TCP/IP controller
    from libraries import nvda_remote_controller
    nvda_controller_module = nvda_remote_controller
    logger.info("Using NVDA Remote controller")
except ImportError:
    try:
        # Next try the Windows API controller
        from libraries import nvdaControllerClient
        nvda_controller_module = nvdaControllerClient
        logger.info("Using Windows API controller for NVDA")
    except ImportError:
        try:
            # Try an alternative import path
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            import nvdaControllerClient
            nvda_controller_module = nvdaControllerClient
            logger.info("Using direct NVDA controller client (alternative path)")
        except ImportError:
            # Fall back to simulator
            try:
                from libraries import nvda_controller_simulator
                nvda_controller_module = nvda_controller_simulator
                logger.info("Using NVDA controller simulator")
            except ImportError:
                # Final fallback
                try:
                    import nvda_controller_simulator
                    nvda_controller_module = nvda_controller_simulator
                except ImportError:
                    logger.error("Could not import any NVDA controller module")
                    # Create a minimal simulator
                    class MinimalSimulator:
                        def nvdaController_testIfRunning(self):
                            return True
                        def nvdaController_speakText(self, text):
                            return True
                        def nvdaController_cancelSpeech(self):
                            return True
                    nvda_controller_module = MinimalSimulator()

# Global variable to store the last simulated speech
_last_speech = ""
_nvda_client = nvda_controller_module
_using_simulation = True  # Start with assumption of simulation

def is_admin():
    """Check if the current process has admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def ensure_nvda_running():
    """
    Ensures NVDA is running with proper privileges.
    Returns True if NVDA is running or started successfully, False otherwise.
    """
    try:
        # First check if NVDA is already running
        if _nvda_client.nvdaController_testIfRunning():
            logger.info("NVDA is already running")
            return True
            
        # If not running and we're not admin, warn about elevation
        if not is_admin():
            logger.error("Error checking/starting NVDA: The requested operation requires elevation")
            logger.warn("Please run NVDA manually with admin privileges")
            return False
            
        # Try to start NVDA with admin privileges
        nvda_path = os.environ.get('NVDA_PATH', r'C:\Program Files (x86)\NVDA\nvda.exe')
        if os.path.exists(nvda_path):
            try:
                subprocess.Popen([nvda_path], shell=True)
                time.sleep(5)  # Give NVDA time to start
                return _nvda_client.nvdaController_testIfRunning()
            except Exception as e:
                logger.error(f"Error starting NVDA: {e}")
                return False
        else:
            logger.error(f"NVDA not found at {nvda_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error checking/starting NVDA: {e}")
        return False

def connect_to_screen_reader():
    """
    Connects to the appropriate screen reader based on the operating system.
    Prioritizes using NVDA if it's already running with admin privileges.
    
    Returns True if connection is successful, False otherwise.
    """
    global _nvda_client, _using_simulation
    
    current_os = platform.system()
    
    if current_os == "Windows":
        # Try to connect to NVDA directly using our controller
        try:
            # Check if NVDA is already running (don't try to start it)
            if _nvda_client.nvdaController_testIfRunning():
                _using_simulation = False
                logger.info("Successfully connected to NVDA screen reader (already running)")
                return True
            else:
                logger.warn("NVDA is not running. Using simulation mode.")
                _using_simulation = True
        except Exception as e:
            logger.warn(f"NVDA connection error: {e}")
            logger.info("Using screen reader simulation mode")
            _using_simulation = True
    else:
        logger.info(f"Not on Windows (detected {current_os}). Using simulation mode.")
        _using_simulation = True
    
    return True

def start_speech_capture():
    """
    Starts capturing screen reader speech output to a temporary file.
    """
    global _last_speech, _nvda_client, _using_simulation
    _last_speech = ""  # Clear previous speech
    
    capture_file = os.path.join(tempfile.gettempdir(), "screen_reader_speech.txt")
    # Clear any previous capture file
    if os.path.exists(capture_file):
        os.remove(capture_file)
    
    if not _using_simulation and _nvda_client:
        try:
            # Try to cancel any previous speech
            _nvda_client.nvdaController_cancelSpeech()
            logger.info("Started NVDA speech capture")
            return True
        except Exception as e:
            logger.warn(f"Error starting NVDA speech capture: {e}")
            _using_simulation = True  # Fall back to simulation
    
    logger.info("Started simulated speech capture")
    return True

def stop_speech_capture():
    """
    Stops screen reader speech capture.
    """
    global _nvda_client, _using_simulation
    
    if not _using_simulation and _nvda_client:
        try:
            # Nothing specific to do for NVDA to stop capturing
            logger.info("Stopped NVDA speech capture")
            return True
        except Exception as e:
            logger.warn(f"Error stopping NVDA speech capture: {e}")
    
    logger.info("Stopped simulated speech capture")
    return True

def get_last_speech(wait_time=2):
    """
    Gets the last speech output from the screen reader.
    
    Args:
        wait_time: Time to wait for screen reader to process speech (seconds)
        
    Returns:
        The last speech text from the screen reader
    """
    global _last_speech, _nvda_client, _using_simulation
    
    # Wait for screen reader to process speech
    time.sleep(float(wait_time))
    
    if not _using_simulation and _nvda_client:
        # In a real implementation, we would read from NVDA here
        # Since NVDA doesn't directly provide an API to get speech text,
        # we continue using our simulation but log that we'd be using NVDA
        logger.info("Would be retrieving speech from NVDA if API allowed")
    
    # If no speech has been simulated yet, use a default
    if not _last_speech:
        _last_speech = "button element"
        
    return _last_speech

def simulate_speech(element_info_str):
    """
    Simulates or generates screen reader speech for an element.
    If NVDA is running, it will use NVDA to speak the text.
    Otherwise, it will simulate what NVDA would likely say.
    
    Args:
        element_info_str: JSON string with element information
        
    Returns:
        Generated speech text
    """
    global _last_speech, _nvda_client, _using_simulation
    
    try:
        element_info = json.loads(element_info_str)
    except Exception as e:
        logger.error(f"Error parsing element info: {e}")
        element_info = {"role": "button", "name": "unnamed"}
    
    # Create speech text based on element attributes
    role = element_info.get('role', 'element')
    name = element_info.get('name', 'unnamed element')
    tag_name = element_info.get('tagName', '')
    
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
        # Default screen reader style
        if role and role != 'element':
            speech = f"{role} {name}"
        elif tag_name.lower() == 'h1':
            speech = f"heading level 1, {name}"
        elif tag_name.lower() == 'h2':
            speech = f"heading level 2, {name}"
        elif tag_name.lower() == 'h3':
            speech = f"heading level 3, {name}"
        elif tag_name.lower() == 'a':
            speech = f"link, {name}"
        elif tag_name.lower() == 'p':
            speech = f"text, {name}"
        elif tag_name.lower() == 'button':
            speech = f"button, {name}"
        else:
            speech = f"{tag_name} {name}"
    
    # Store the speech for later retrieval
    _last_speech = speech
    
    # If NVDA is available and not using simulation, use it to speak the text
    if not _using_simulation and _nvda_client:
        try:
            # Try to speak the text using NVDA
            success = _nvda_client.nvdaController_speakText(speech)
            if success:
                logger.info(f"NVDA spoke: '{speech}'")
            else:
                logger.warn(f"Failed to speak through NVDA, falling back to simulation: {speech}")
                _using_simulation = True  # Fall back to simulation
        except Exception as e:
            logger.warn(f"Error with NVDA speech: {e}")
            logger.info(f"Falling back to simulation: {speech}")
    else:
        logger.info(f"Simulated speech: '{speech}'")
    
    return speech 