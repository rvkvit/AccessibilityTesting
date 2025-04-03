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
${OS}              ${EMPTY}

*** Keywords ***
Get Operating System
    ${result}=    Run Process    python    ${CURDIR}/../get_os.py
    RETURN    ${result.stdout}

Open Browser And Navigate To Site
    New Browser    browser=${BROWSER}    headless=${HEADLESS}
    New Context    viewport={'width': 1280, 'height': 720}
    
    # Try to load the page with multiple attempts if needed
    ${attempts}=    Set Variable    3
    FOR    ${attempt}    IN RANGE    ${attempts}
        TRY
            New Page       ${WEBSITE_URL}
            Wait For Elements State    css=body    state=attached    timeout=10
            Log    Page loaded successfully on attempt ${attempt+1}    level=INFO
            BREAK
        EXCEPT
            Log    Failed to load page on attempt ${attempt+1}    level=WARN
            Run Keyword If    ${attempt} < ${attempts-1}    Sleep    5s
            Run Keyword If    ${attempt} < ${attempts-1}    Close Page
        END
    END
    
    # Additional wait for page to stabilize
    Sleep    5s
    
    # If there's a cookie consent dialog, accept it
    ${cookie_dialog_exists}=    Run Keyword And Return Status    Get Element    [data-testid="cookie-consent"]
    Run Keyword If    ${cookie_dialog_exists}    Click    [data-testid="cookie-consent-accept"]
    
    # If there's a modal, try to close it (look for various close buttons)
    ${modal_close_exists}=    Run Keyword And Return Status    Get Element    button.close
    Run Keyword If    ${modal_close_exists}    Click    button.close
    
    Log    Page has been loaded and initial dialogs handled    level=INFO

Find And Click Release Flag Section
    # Look for elements with data-testid that might contain release or flag
    ${elements_with_testid}=    Get Elements    [data-testid]
    ${testid_count}=    Get Length    ${elements_with_testid}
    Log    Found ${testid_count} elements with data-testid, looking for release flag related elements    level=INFO
    
    FOR    ${element}    IN    @{elements_with_testid}
        ${test_id}=    Get Attribute    ${element}    data-testid
        Log    Checking element with test-id: ${test_id}    level=INFO
        
        # If testid contains release or flag, try clicking it
        ${contains_release}=    Run Keyword And Return Status    Should Contain    ${test_id}    release
        ${contains_flag}=    Run Keyword And Return Status    Should Contain    ${test_id}    flag
        ${contains_version}=    Run Keyword And Return Status    Should Contain    ${test_id}    version
        
        IF    ${contains_release} or ${contains_flag} or ${contains_version}
            Log    Found potential release flag element: ${test_id}    level=INFO
            Set Test Variable    ${RELEASE_FLAG_ELEMENT}    [data-testid="${test_id}"]
            
            # Try to click this element to see if it opens something
            TRY
                Click    ${RELEASE_FLAG_ELEMENT}
                Sleep    2s
                Log    Clicked on element with test-id: ${test_id}    level=INFO
                RETURN    ${True}
            EXCEPT
                Log    Could not click on element with test-id: ${test_id}    level=WARN
            END
        END
    END
    
    # If not found by data-testid, look for buttons or links with relevant text
    ${all_elements}=    Get Elements    button, a
    ${all_elements_count}=    Get Length    ${all_elements}
    Log    Looking through ${all_elements_count} buttons and links    level=INFO
    
    FOR    ${element}    IN    @{all_elements}
        TRY
            ${text}=    Get Text    ${element}
            # Check for keywords in the text
            ${contains_release}=    Run Keyword And Return Status    Should Contain    ${text}    release
            ${contains_flag}=    Run Keyword And Return Status    Should Contain    ${text}    flag
            ${contains_version}=    Run Keyword And Return Status    Should Contain    ${text}    version
            
            IF    ${contains_release} or ${contains_flag} or ${contains_version}
                Log    Found element with relevant text: "${text}"    level=INFO
                Click    ${element}
                Sleep    2s
                Log    Clicked on element with text: "${text}"    level=INFO
                RETURN    ${True}
            END
        EXCEPT
            # Continue with the next element if text retrieval fails
            CONTINUE
        END
    END
    
    # If everything else fails, assume we're already at the release flag section
    Log    Could not find specific release flag section, proceeding with main content area    level=INFO
    Set Test Variable    ${RELEASE_FLAG_ELEMENT}    main
    RETURN    ${True}

Get All Elements In Release Flag Section
    # If we have a specific release flag element, get elements inside it
    ${has_release_flag}=    Run Keyword And Return Status    Variable Should Exist    ${RELEASE_FLAG_ELEMENT}
    
    IF    ${has_release_flag}
        ${elements}=    Get Elements    ${RELEASE_FLAG_ELEMENT} button, ${RELEASE_FLAG_ELEMENT} a, ${RELEASE_FLAG_ELEMENT} input
    ELSE
        # Otherwise, get all interactive elements on the page
        ${elements}=    Get Elements    button, a, input[type=button], input[type=submit]
    END
    
    ${count}=    Get Length    ${elements}
    Log    Found ${count} interactive elements    level=INFO
    
    # If no elements found, use any elements with data-testid
    IF    ${count} == 0
        ${elements}=    Get Elements    [data-testid]
        ${count}=    Get Length    ${elements}
        Log    Falling back to elements with data-testid, found: ${count}    level=INFO
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
    Log    Found ${count} elements to test    level=INFO
    
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