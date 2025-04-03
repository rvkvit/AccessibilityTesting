# NVDA Setup for Accessibility Testing

This document explains how to set up NVDA to work properly with the accessibility tests.

## Prerequisites

- NVDA screen reader installed at `C:\Program Files (x86)\NVDA`
- Basic knowledge of NVDA keyboard shortcuts

## Setup Instructions

1. **Start NVDA Before Running Tests**
   
   The most important step is to make sure NVDA is running before you start your accessibility tests. Launch NVDA manually from your Start menu or desktop shortcut.

2. **Configure NVDA Remote Support** (Optional)

   To enable advanced integration:
   
   - Press NVDA+N to open the NVDA menu
   - Navigate to Tools > Remote
   - Check "Allow this computer to be controlled"
   - Restart NVDA if prompted

3. **Run Your Tests**

   Once NVDA is properly running, you can run your accessibility tests with:
   
   ```
   python -m robot tests/accessibility_tests.robot
   ```

## Troubleshooting

If you encounter any issues:

1. **NVDA Not Speaking During Tests**
   
   - Make sure NVDA's speech isn't muted
   - Press NVDA+S to cycle through speech modes

2. **Tests Failing to Connect to NVDA**
   
   - Ensure NVDA is running before starting the tests
   - Check if NVDA needs administrator privileges
   - Try restarting NVDA and then running tests

3. **"Simulator Used" Warning in Logs**

   This means the test couldn't connect to your NVDA installation and fell back to simulation mode. Verify that:
   
   - NVDA is running
   - You've enabled Remote Support if using the remote connection method

## Known Limitations

- Starting NVDA automatically requires administrator privileges
- Full speech capture requires NVDA to be running with specific configuration
- Some NVDA functionality may be limited depending on your version and settings

## Contact

If you have additional questions or need help setting up NVDA for accessibility testing, please contact the development team. 