*** Settings ***
Documentation     Accessibility testing with screen readers (NVDA on Windows, VoiceOver on macOS)
Resource          ${CURDIR}/../resources/accessibility_keywords.resource
Suite Setup       Suite Setup Keywords
Suite Teardown    Suite Teardown Keywords
Test Teardown     Test Teardown Keywords

*** Variables ***
${CURRENT_OS}         ${EMPTY}
${TIMEOUT}           30s

*** Test Cases ***
Verify Lahitapiola Accessibility
    [Documentation]    Tests the accessibility of Lahitapiola site using screen reader
    [Tags]            accessibility    a11y    lahitapiola
    [Timeout]         3 minutes
    
    # Open browser and navigate to Lahitapiola site
    Run Keyword And Continue On Failure    Open Browser And Navigate To Site
    
    # Start screen reader and prepare for capturing
    ${status}=    Connect To Screen Reader
    Log    Screen reader connection status: ${status}    level=INFO
    ${capture_status}=    Start Speech Capture
    Log    Speech capture started with status: ${capture_status}    level=INFO
    
    # Wait for Release Flag Section to be visible
    Run Keyword And Continue On Failure    Wait For Release Flag Section
    
    # Test all elements in the Release Flag Section
    Run Keyword And Continue On Failure    Test All Elements In Release Flag Section
    
    # Verify we're still on the site
    ${current_url}=    Get Url
    Run Keyword And Continue On Failure    Should Contain    ${current_url}    lahitapiola    msg=Not on Lahitapiola site

*** Keywords ***
Suite Setup Keywords
    Log    Starting accessibility testing with screen reader    console=True
    ${CURRENT_OS}=    Get Operating System
    Set Global Variable    ${CURRENT_OS}
    Run Keyword If    '${CURRENT_OS}' == 'Darwin'    Log    Running on macOS with VoiceOver support    console=True

Suite Teardown Keywords
    Log    Finished accessibility testing with screen reader    console=True

Test Teardown Keywords
    Run Keyword And Ignore Error    Take Screenshot
    Run Keyword And Ignore Error    Clean Up Resources 