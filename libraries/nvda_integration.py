import os
import time
import subprocess
import tempfile
from robot.api import logger
from nvda_automation import NVDAController

class NVDAIntegration:
    """
    A Robot Framework library for interacting with NVDA screen reader.
    """
    
    def __init__(self):
        self.nvda = None
        self.speech_capture_file = os.path.join(tempfile.gettempdir(), "nvda_speech.txt")
        
    def connect_to_nvda(self):
        """
        Connects to the running NVDA instance.
        
        Returns True if connection is successful, False otherwise.
        """
        try:
            self.nvda = NVDAController()
            logger.info("Successfully connected to NVDA")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to NVDA: {str(e)}")
            return False
            
    def start_speech_capture(self):
        """
        Starts capturing NVDA speech output to a temporary file.
        """
        try:
            # Clear any previous capture file
            if os.path.exists(self.speech_capture_file):
                os.remove(self.speech_capture_file)
                
            # Configure NVDA for speech capture
            self.nvda.set_speech_capture_file(self.speech_capture_file)
            self.nvda.enable_speech_capture()
            logger.info("Started capturing NVDA speech")
            return True
        except Exception as e:
            logger.error(f"Failed to start speech capture: {str(e)}")
            return False
            
    def stop_speech_capture(self):
        """
        Stops NVDA speech capture.
        """
        try:
            self.nvda.disable_speech_capture()
            logger.info("Stopped capturing NVDA speech")
            return True
        except Exception as e:
            logger.error(f"Failed to stop speech capture: {str(e)}")
            return False
    
    def get_last_speech(self, wait_time=2):
        """
        Gets the last speech output from NVDA.
        
        Args:
            wait_time: Time to wait for NVDA to process speech (seconds)
            
        Returns:
            The last speech text from NVDA
        """
        # Wait for NVDA to process speech
        time.sleep(wait_time)
        
        try:
            if os.path.exists(self.speech_capture_file):
                with open(self.speech_capture_file, 'r') as f:
                    speech_text = f.read().strip()
                return speech_text
            else:
                logger.warn("Speech capture file not found")
                return ""
        except Exception as e:
            logger.error(f"Failed to read speech capture: {str(e)}")
            return ""
    
    def simulate_nvda_speech(self, element_info):
        """
        For demo purposes, simulates NVDA speech for an element.
        Used when actual NVDA integration is not available.
        
        Args:
            element_info: Dictionary with element information
            
        Returns:
            Simulated speech text
        """
        # Create simulated speech based on element attributes
        role = element_info.get('role', 'button')
        name = element_info.get('name', 'unnamed element')
        state = element_info.get('state', '')
        
        speech = f"{name}, {role}"
        if state:
            speech += f", {state}"
            
        logger.info(f"Simulated NVDA speech: {speech}")
        
        # Write to the capture file for consistency
        with open(self.speech_capture_file, 'w') as f:
            f.write(speech)
            
        return speech 