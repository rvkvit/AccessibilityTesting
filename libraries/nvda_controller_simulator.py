"""
NVDA Controller Client Simulator

This module simulates the NVDA Controller Client API for testing when the actual NVDA
controller client is not available or not functioning properly.
"""
from robot.api import logger

# Flag to indicate if NVDA is running
_nvda_running = True

def nvdaController_testIfRunning():
    """
    Tests if NVDA is running.
    Returns True if running, raises an exception if not.
    """
    if _nvda_running:
        logger.info("NVDA is simulated as running")
        return True
    else:
        raise RuntimeError("Simulated NVDA is not running")

def nvdaController_speakText(text):
    """
    Speaks the given text through NVDA.
    In simulation mode, just logs the text.
    """
    if not _nvda_running:
        raise RuntimeError("Simulated NVDA is not running")
    
    logger.info(f"NVDA would speak: {text}")
    return True

def nvdaController_cancelSpeech():
    """
    Cancels speech in NVDA.
    In simulation mode, just logs the action.
    """
    if not _nvda_running:
        raise RuntimeError("Simulated NVDA is not running")
    
    logger.info("NVDA speech cancelled")
    return True

def nvdaController_brailleMessage(message):
    """
    Displays a message on the braille display.
    In simulation mode, just logs the message.
    """
    if not _nvda_running:
        raise RuntimeError("Simulated NVDA is not running")
    
    logger.info(f"NVDA would display on braille: {message}")
    return True 