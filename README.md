# Cross-Platform Accessibility Testing Framework

A Robot Framework-based automated testing framework for accessibility testing across different platforms, supporting both VoiceOver (macOS) and NVDA (Windows).

## Features

- Cross-platform support for screen readers (VoiceOver on macOS, NVDA on Windows)
- Automated accessibility testing using Robot Framework
- Screen reader speech capture and verification
- Simulated mode for development and testing
- Browser-based testing using Playwright
- Detailed test reports and logging

## Prerequisites

- Python 3.11 or higher
- Robot Framework
- Node.js and npm (for Browser library)
- Chrome/Chromium browser
- For Windows: NVDA screen reader
- For macOS: VoiceOver (built-in)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rvkvit/AccessibilityTesting.git
cd AccessibilityTesting
```

2. Install Python dependencies:
```bash
# On macOS:
python3 -m pip install -r requirements.txt

# On Windows:
python -m pip install -r requirements.txt
```

3. Platform-specific setup:

### Windows Setup
Run the NVDA installation helper script:
```bash
python tools/install_nvda.py
```
This will:
- Download the NVDA installer
- Install Python dependencies
- Provide instructions for NVDA setup

After running the script:
1. Run the downloaded NVDA installer (`tools/nvda_installer.exe`)
2. Follow the installation wizard
3. Enable the Controller Client in NVDA:
   - Open NVDA
   - Press NVDA+N to open the menu
   - Go to Tools -> Remote
   - Check 'Allow this computer to be controlled remotely'
4. Restart NVDA

### macOS Setup
VoiceOver is built into macOS. To enable it:
1. Press Command+F5 to toggle VoiceOver
2. Grant terminal access in System Preferences:
   - Open System Preferences > Security & Privacy > Privacy
   - Select 'Accessibility'
   - Enable access for your terminal application

4. Initialize the Browser library:
```bash
rfbrowser init
```

## Project Structure

```
AccessibilityTesting/
├── libraries/
│   └── screen_reader_integration.py
├── resources/
│   └── accessibility_keywords.resource
├── tests/
│   └── accessibility_tests.robot
├── tools/
│   └── install_nvda.py
├── requirements.txt
└── README.md
```

## Running Tests

To run the accessibility tests:

```bash
python3 -m robot tests/accessibility_tests.robot
```

The tests will:
1. Open the BBC Accessibility page
2. Test screen reader output for various elements
3. Verify navigation and content accessibility
4. Generate detailed test reports

## Test Reports

After running the tests, you can find the following reports in the project root:
- `log.html`: Detailed test execution log
- `report.html`: Test results summary
- `output.xml`: Raw test output data

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
