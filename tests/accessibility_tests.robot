*** Settings ***
Documentation     Accessibility testing with screen readers (NVDA on Windows, VoiceOver on macOS)
Resource          ${CURDIR}/../resources/accessibility_keywords.resource
Suite Setup       Suite Setup Keywords
Suite Teardown    Suite Teardown Keywords
Test Teardown     Test Teardown Keywords

*** Variables ***
${HEADING}            xpath=//h1[contains(text(), 'BBC Accessibility Help')]
${MAIN_PARAGRAPH}     xpath=//p[contains(text(), 'All audiences are important')]
${HELP_LINK}         xpath=//a[contains(text(), 'BBC Shows and Tours')]
${CURRENT_OS}         ${EMPTY}

*** Test Cases ***
Verify BBC Accessibility Page
    [Documentation]    Tests the accessibility of BBC's accessibility page using screen reader
    [Tags]            accessibility    a11y    basic
    
    # Open browser and navigate to BBC accessibility page
    Open Browser And Navigate To Example Site
    
    # Start screen reader and prepare for capturing
    Start Screen Reader And Capture Speech
    
    # Verify elements exist - with longer timeouts
    Wait For Elements State    ${HEADING}    visible    timeout=10s    message=BBC Accessibility Help heading not found
    Log    Found BBC Accessibility Help heading    level=INFO
    
    Wait For Elements State    ${MAIN_PARAGRAPH}    visible    timeout=10s    message=Main paragraph not found
    Log    Found main paragraph element    level=INFO
    
    Wait For Elements State    ${HELP_LINK}    visible    timeout=10s    message=Help link not found
    Log    Found BBC Shows and Tours link    level=INFO
    
    # Test heading accessibility
    ${heading_speech}=    Hover On Element And Get Speech    ${HEADING}    BBC Accessibility Help heading
    Log    Heading speech: ${heading_speech}    level=INFO
    Should Contain Any    ${heading_speech}    heading    BBC    Accessibility    Help
    
    # Test paragraph accessibility
    ${paragraph_speech}=    Hover On Element And Get Speech    ${MAIN_PARAGRAPH}    Main paragraph
    Log    Paragraph speech: ${paragraph_speech}    level=INFO
    Should Contain Any    ${paragraph_speech}    text    All audiences    important    BBC
    
    # Test link accessibility
    ${link_speech}=    Hover On Element And Get Speech    ${HELP_LINK}    BBC Shows and Tours link
    Log    Link speech: ${link_speech}    level=INFO
    Should Contain Any    ${link_speech}    link    BBC Shows    Tours    booking assistance
    
    # Click the link and verify navigation
    Click Element And Log Action    ${HELP_LINK}    BBC Shows and Tours link
    Sleep    2s
    
    # Verify we navigated away from the accessibility page
    ${current_url}=    Get Url
    Should Contain    ${current_url}    shows    msg=Failed to navigate to Shows and Tours page

*** Keywords ***
Suite Setup Keywords
    Log    Starting accessibility testing with screen reader    console=True
    ${CURRENT_OS}=    Get Operating System
    Set Global Variable    ${CURRENT_OS}
    Run Keyword If    '${CURRENT_OS}' == 'Darwin'    Log    Running on macOS with VoiceOver support    console=True

Suite Teardown Keywords
    Log    Finished accessibility testing with screen reader    console=True

Test Teardown Keywords
    Take Screenshot
    Clean Up Resources 