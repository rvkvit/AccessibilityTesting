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
${TIMEOUT}          30
${WEBSITE_URL}      https://sitaksasiointi.lahitapiola.fi/
${PAGE_BODY}        css=body
${RELEASE_FLAG_SECTION}    css=[data-testid="release-flag-section"]
${RELEASE_FLAG_ELEMENTS}    css=[data-testid^="release-flag-"]
${OS}              ${EMPTY}

*** Keywords ***
Get Operating System
    ${result}=    Run Process    python    ${CURDIR}/../get_os.py
    RETURN    ${result.stdout}

Open Browser And Navigate To Site
    New Browser    browser=${BROWSER}    headless=${HEADLESS}
    New Context    viewport={'width': 1280, 'height': 720}
    New Page       ${WEBSITE_URL}
    
    # Wait for body to be visible, indicating page has loaded
    Wait For Elements State    ${PAGE_BODY}    visible    timeout=${TIMEOUT}
    Sleep    5s
    
    # If there's a cookie consent dialog, accept it
    ${cookie_dialog_exists}=    Run Keyword And Return Status    Get Element    css=[data-testid="cookie-consent"]
    Run Keyword If    ${cookie_dialog_exists}    Click    css=[data-testid="cookie-consent-accept"]
    
    # If there's a modal or overlay, close it
    ${modal_exists}=    Run Keyword And Return Status    Get Element    css=.modal
    Run Keyword If    ${modal_exists}    Click    css=.modal .close
    
    Log    Page has been loaded and initial dialogs handled    level=INFO

Find And Click Release Flag Section
    # First check if release flag section exists directly
    ${release_flag_visible}=    Run Keyword And Return Status    Get Element    ${RELEASE_FLAG_SECTION}
    
    IF    ${release_flag_visible}
        Log    Release flag section found directly    level=INFO
    ELSE
        # Try to find a button or link that might open the release flag section
        ${buttons}=    Get Elements    css=button, a
        Log    Searching for release flag section through ${buttons.length} buttons/links    level=INFO
        
        FOR    ${button}    IN    @{buttons}
            ${text}=    Get Text    ${button}
            Log    Checking button/link: "${text}"    level=INFO
            
            # If the text mentions release, flag, or version, click it
            ${contains_release}=    Run Keyword And Return Status    Should Contain    ${text}    release
            ${contains_flag}=    Run Keyword And Return Status    Should Contain    ${text}    flag
            ${contains_version}=    Run Keyword And Return Status    Should Contain    ${text}    version
            
            IF    ${contains_release} or ${contains_flag} or ${contains_version}
                Log    Clicking button that might reveal release flag section: "${text}"    level=INFO
                Click    ${button}
                Sleep    2s
                ${section_found}=    Run Keyword And Return Status    Get Element    ${RELEASE_FLAG_SECTION}
                Return From Keyword If    ${section_found}    ${True}
            END
        END
        
        # If not found, try to find by looking at all elements with data-testid
        ${elements_with_testid}=    Get Elements    css=[data-testid]
        Log    Checking ${elements_with_testid.length} elements with data-testid    level=INFO
        
        FOR    ${element}    IN    @{elements_with_testid}
            ${test_id}=    Get Attribute    ${element}    data-testid
            Log    Found element with test-id: ${test_id}    level=INFO
            
            # If testid contains release or flag, mark as found
            ${contains_release}=    Run Keyword And Return Status    Should Contain    ${test_id}    release
            ${contains_flag}=    Run Keyword And Return Status    Should Contain    ${test_id}    flag
            
            IF    ${contains_release} or ${contains_flag}
                Log    Found element that appears to be related to release flags: ${test_id}    level=INFO
                ${elem_visible}=    Run Keyword And Return Status    Wait For Elements State    ${element}    visible    timeout=2s
                IF    ${elem_visible}
                    ${RELEASE_FLAG_SECTION}=    Set Variable    css=[data-testid="${test_id}"]
                    Set Global Variable    ${RELEASE_FLAG_SECTION}
                    ${RELEASE_FLAG_ELEMENTS}=    Set Variable    css=[data-testid^="${test_id}"]
                    Set Global Variable    ${RELEASE_FLAG_ELEMENTS}
                    RETURN    ${True}
                END
            END
        END
    END
    
    Fail    Could not find or open the release flag section

Get All Elements In Release Flag Section
    # Try to get elements with data-testid inside the release flag section
    ${elements}=    Get Elements    ${RELEASE_FLAG_ELEMENTS}
    ${count}=    Get Length    ${elements}
    
    # If no elements found, look for any interactive elements
    IF    ${count} == 0
        Log    No elements with data-testid found in release flag section, looking for any interactive elements    level=INFO
        ${elements}=    Get Elements    css=${RELEASE_FLAG_SECTION} button, ${RELEASE_FLAG_SECTION} a, ${RELEASE_FLAG_SECTION} input, ${RELEASE_FLAG_SECTION} select
    END
    
    RETURN    ${elements}

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
    
    # Try to get text - some elements may not have text
    ${text_status}=    Run Keyword And Return Status    Get Text    ${selector}
    ${text}=    Run Keyword If    ${text_status}    Get Text    ${selector}
    ...    ELSE    Set Variable    ""
    
    # If text is empty, try to get value or placeholder
    IF    $text == ""
        ${value_status}=    Run Keyword And Return Status    Get Attribute    ${selector}    value
        ${text}=    Run Keyword If    ${value_status}    Get Attribute    ${selector}    value
        ...    ELSE    Set Variable    ${text}
        
        # If still empty, try placeholder
        IF    $text == ""
            ${placeholder_status}=    Run Keyword And Return Status    Get Attribute    ${selector}    placeholder
            ${text}=    Run Keyword If    ${placeholder_status}    Get Attribute    ${selector}    placeholder
            ...    ELSE    Set Variable    ${text}
        END
    END
    
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

Test All Elements In Release Flag Section
    ${elements}=    Get All Elements In Release Flag Section
    ${count}=    Get Length    ${elements}
    Log    Found ${count} elements in Release Flag Section    level=INFO
    
    ${index}=    Set Variable    1
    FOR    ${element}    IN    @{elements}
        # Try to get test-id, fallback to index if not present
        ${test_id_exists}=    Run Keyword And Return Status    Get Attribute    ${element}    data-testid
        ${element_id}=    Run Keyword If    ${test_id_exists}    Get Attribute    ${element}    data-testid
        ...    ELSE    Set Variable    element-${index}
        
        # Try to get text
        ${text_status}=    Run Keyword And Return Status    Get Text    ${element}
        ${text}=    Run Keyword If    ${text_status}    Get Text    ${element}
        ...    ELSE    Set Variable    ""
        
        Log    Testing element ${index}/${count}: ${element_id} - "${text}"    level=INFO
        ${speech}=    Get Element Speech    ${element}    ${element_id}
        Log    Element ${element_id} speech: ${speech}    level=INFO
        ${index}=    Evaluate    ${index} + 1
    END

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