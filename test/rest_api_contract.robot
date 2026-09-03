*** Settings ***
Documentation    Contract tests for Process Control REST API v1.
Library          MockRestApiLibrary.py
Library          Collections
Suite Setup      Start Mock Backend
Suite Teardown   Stop Mock Backend

*** Variables ***
${NODE_ID_str}       2047
${NODE_ID_int}       ${{2047}}
${UNKNOWN_NODE_str}  999
${UNKNOWN_NODE_int}  ${{999}}
${VALUE_int}         ${{120}}
${MIN_VALUE_int}     ${{-100}}
${MAX_VALUE_int}     ${{500}}
${SET_VALUE_int}     ${{100}}
${ERROR_CODE_int}    ${{0}}

*** Test Cases ***
Health Reports Software And Connected CSN Versions
    Request Health
    Response Status Should Be    200
    Response Field Should Be    status    ok
    Response Field Should Be    software.gui    2.0.0
    Response Field Should Be    software.backend    2.0.0
    Response Field Should Be    software.configurator    2.0.0
    Response Field Should Be    backend.rest_api    v1
    Response Field Should Be    backend.can.status    connected
    Response Field Should Be    backend.can.interface    can0
    ${api}=    Get Library Instance    MockRestApiLibrary
    ${connected_node}=    Evaluate    $api.last_json["connected_csn"][0]
    Should Be Equal As Integers    ${connected_node}[node_id]    ${NODE_ID_int}
    Should Be Equal    ${connected_node}[firmware_version]    1.3.0
    Should Be Equal    ${connected_node}[hardware_version]    1.0
    Response Field Should Exist    timestamp
    Should Not Be Empty    ${connected_node}[last_seen]
    Response Recent Errors Should Not Exceed    10

Health Reports Unavailable Backend
    Set Mock Failure Status    503
    Request Health
    Response Status Should Be    200
    Response Field Should Be    status    unavailable
    Clear Mock Failure

Runtime Values Return Complete Snapshot
    ${default_value_int}=    Convert To Integer    0
    Request Node Values    ${NODE_ID_str}
    Response Status Should Be    200
    Response Field Should Be    node_id    ${NODE_ID_int}
    Response Field Should Be    value    ${VALUE_int}
    Response Field Should Be    min_value    ${MIN_VALUE_int}
    Response Field Should Be    max_value    ${MAX_VALUE_int}
    Response Field Should Be    set_value    ${SET_VALUE_int}
    Response Field Should Be    default_value    ${default_value_int}
    Response Field Should Be    state    running
    Response Field Should Be    error_code    ${ERROR_CODE_int}
    Response Field Should Exist    timestamp

Unknown Node Returns Not Found
    Request Node Values    ${UNKNOWN_NODE_str}
    Response Status Should Be    404
    Response Field Should Be    error.code    NODE_NOT_FOUND
    Response Field Should Exist    error.message
    Response Field Should Exist    error.details
    Response Field Should Exist    timestamp

Setup Returns Complete Configuration
    Request Node Setup    ${NODE_ID_str}
    Response Status Should Be    200
    Response Field Should Be    node_id    ${NODE_ID_int}
    Response Field Should Exist    configuration.name
    Response Field Should Exist    configuration.unit
    Response Field Should Exist    configuration.value
    Response Field Should Exist    configuration.value_set
    Response Field Should Exist    configuration.value_default
    Response Field Should Exist    configuration.value_min
    Response Field Should Exist    configuration.value_max
    Response Field Should Exist    configuration.value_offset
    Response Field Should Exist    configuration.value_multiplier
    Response Field Should Exist    configuration.update_rate_ms
    Response Field Should Exist    configuration.node_type
    Response Field Should Exist    configuration.can_id
    Response Field Should Exist    configuration.last_error_code

Configuration Read Returns All Parameters
    Request Configuration    ${NODE_ID_str}
    Response Status Should Be    200
    Response Field Should Exist    name
    Response Field Should Exist    unit
    Response Field Should Exist    value
    Response Field Should Exist    value_set
    Response Field Should Exist    value_default
    Response Field Should Exist    value_min
    Response Field Should Exist    value_max
    Response Field Should Exist    value_offset
    Response Field Should Exist    value_multiplier
    Response Field Should Exist    update_rate_ms
    Response Field Should Exist    node_type
    Response Field Should Exist    can_id
    Response Field Should Exist    last_error_code

Configuration Write Accepts Complete Parameter Set
    &{configuration}=    Create Dictionary
    ...    name=CSN configured
    ...    unit=Volt
    ...    value=200
    ...    value_set=-20
    ...    value_default=0
    ...    value_min=-100
    ...    value_max=500
    ...    value_offset=5
    ...    value_multiplier=1000
    ...    update_rate_ms=250
    ...    node_type=2
    ...    can_id=${NODE_ID_int}
    ...    last_error_code=0
    Write Configuration    ${NODE_ID_str}    ${configuration}
    Response Status Should Be    200
    Response Field Should Be    accepted    ${True}
    Response Field Should Be    configuration.name    CSN configured
    Response Field Should Be    configuration.value_set    -20
    Response Field Should Be    configuration.value_min    -100
    Response Field Should Be    configuration.value_max    500
    Response Field Should Be    configuration.value_offset    5
    Response Field Should Be    configuration.value_multiplier    1000
    Response Field Should Be    configuration.update_rate_ms    250
    Response Field Should Be    configuration.node_type    2
    Response Field Should Be    configuration.can_id    ${NODE_ID_int}
    Response Field Should Be    configuration.last_error_code    0

Incomplete Configuration Returns Unprocessable Entity
    Request    PUT    /nodes/${NODE_ID_str}/configuration    {"name": "incomplete"}
    Response Status Should Be    422
    Response Field Should Be    error.code    INVALID_CONFIGURATION

Complete Setup Returns Result
    Complete Node Setup    ${NODE_ID_str}
    Response Status Should Be    200
    Response Field Should Be    node_id    ${NODE_ID_int}
    Response Field Should Be    accepted    ${True}

Logging Accepts Custom Filename
    Start Logging    test-run-001.csv
    Response Status Should Be    201
    Response Field Should Be    state    active
    Response Field Should Be    filename    test-run-001.csv

Logging Status Returns State And Filename
    Request Logging Status
    Response Status Should Be    200
    Response Field Should Be    state    active
    Response Field Should Be    filename    test-run-001.csv
    Response Field Should Exist    started_at
    Response Field Should Exist    records_written

Logging Rejects Unsafe Filename
    Start Logging    ../outside.csv
    Response Status Should Be    400
    Response Field Should Be    error.code    INVALID_FILENAME

Logging Stop Returns Closed State
    Stop Logging
    Response Status Should Be    200
    Response Field Should Be    state    inactive
    Response Field Should Be    filename    test-run-001.csv

Configured Error Responses Use Common Contract
    Set Mock Failure Status    409
    Request Node Values    ${NODE_ID_str}
    Response Status Should Be    409
    Response Field Should Be    error.code    REQUEST_BUSY
    Response Field Should Exist    error.message
    Response Field Should Exist    error.details
    Clear Mock Failure
    Set Mock Failure Status    500
    Request Node Values    ${NODE_ID_str}
    Response Status Should Be    500
    Response Field Should Be    error.code    BACKEND_ERROR
    Clear Mock Failure
    Set Mock Failure Status    504
    Request Node Values    ${NODE_ID_str}
    Response Status Should Be    504
    Response Field Should Be    error.code    CAN_TIMEOUT
    Clear Mock Failure
