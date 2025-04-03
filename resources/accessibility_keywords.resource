*** Settings ***
Library    Browser
Library    ${CURDIR}/../libraries/screen_reader_integration.py
Library    OperatingSystem
Library    Collections
Library    String
Library    Process

*** Variables ***
${BROWSER}          chromium
${HEADLESS}         False
${TIMEOUT}          20
${WEBSITE_URL}      https://www.bbc.co.uk/accessibility/
${PAGE_BODY}        css=body
${HEADING}          xpath=//h1[contains(text(), 'BBC Accessibility Help')]
${MAIN_PARAGRAPH}   xpath=//p[contains(text(), 'All audiences are important')]
${HELP_LINK}        xpath=//a[contains(text(), 'BBC Shows and Tours')]
${OS}              ${EMPTY}

*** Keywords ***
Get Operating System
    ${result}=    Run Process    python    ${CURDIR}/../get_os.py
    RETURN    ${result.stdout}

Open Browser And Navigate To Example Site
    New Browser    browser=${BROWSER}    headless=${HEADLESS}
    New Context    viewport={'width': 1280, 'height': 720}
    New Page       ${WEBSITE_URL}
    
    # Wait for body to be visible, indicating page has loaded
    Wait For Elements State    ${PAGE_BODY}    visible    timeout=${TIMEOUT}
    Sleep    1s

Element Should Be Visible
    [Arguments]    ${selector}    ${message}=Element not visible
    Wait For Elements State    ${selector}    visible    timeout=10s    error=${message}

Get Element Speech
    [Arguments]    ${selector}    ${element_name}
    # Clear previous speech
    Start Speech Capture
    
    # Get text and element properties for screen reader
    ${element}=    Get Element    ${selector}
    ${tag_name}=    Get Property    ${selector}    tagName
    ${text}=    Get Text    ${selector}
    
    # Try to get role attribute, with fallback
    ${has_role}=    Run Keyword And Return Status    Get Attribute    ${selector}    role
    ${role}=    Run Keyword If    ${has_role}    Get Attribute    ${selector}    role
    ...    ELSE    Set Variable    element
    
    # Create element info for screen reader integration
    ${element_info}=    Set Variable    {"role": "${role}", "name": "${text}", "tagName": "${tag_name}"}
    
    # Simulate speech for the library to capture
    ${speech_text}=    Simulate Speech    ${element_info}
    
    # If speech is None, provide a default response
    ${speech_text}=    Set Variable If    $speech_text == None    ${tag_name} ${text}    ${speech_text}
    
    # Log the speech in report
    Log    Element: ${element_name}, Speech: ${speech_text}    level=INFO
    
    RETURN    ${speech_text}

Click Element And Log Action
    [Arguments]    ${selector}    ${element_name}
    Click    ${selector}    button=left
    Log    Clicked on element: ${element_name}    level=INFO

Clean Up Resources
    Run Keyword And Ignore Error    Stop Speech Capture
    Close Browser 

Should Contain Any
    [Arguments]    ${string}    @{substrings}
    FOR    ${substring}    IN    @{substrings}
        ${status}=    Run Keyword And Return Status    Should Contain    ${string}    ${substring}
        Return From Keyword If    ${status}    ${True}
    END
    Fail    String '${string}' did not contain any of the expected substrings: ${substrings} 