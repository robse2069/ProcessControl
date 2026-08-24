*** Settings ***
Library    SmokeTestLibrary.py

*** Test Cases ***
Process Control Test Framework Is Available
    ${framework_is_available}=    Framework Is Available
    Should Be True    ${framework_is_available}