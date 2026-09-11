$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$guiPath = Join-Path $repoRoot "GUI"
$pythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"
$configPath = Join-Path $guiPath "config.xml"
$config10MsPath = Join-Path $guiPath "config_simulated_10ms.xml"
$port = 8765
$port10Ms = 8766
$restUrl = "http://127.0.0.1:$port/api/v1"
$restUrl10Ms = "http://127.0.0.1:$port10Ms/api/v1"
$backendProcess = $null
$backend10MsProcess = $null
$oldRestUrl = $env:PROCESS_CONTROL_REST_URL
$oldSimulatedRestUrl = $env:PROCESS_CONTROL_SIMULATED_REST_URL
$oldSimulatedRestUrl10Ms = $env:PROCESS_CONTROL_SIMULATED_REST_URL_10MS

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Project Python environment not found: $pythonPath"
}

function Test-TcpPort {
    param(
        [string]$ComputerName,
        [int]$Port
    )

    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $connect = $client.BeginConnect($ComputerName, $Port, $null, $null)
        if (-not $connect.AsyncWaitHandle.WaitOne(250)) {
            return $false
        }
        $client.EndConnect($connect)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $client.Close()
    }
}

function Wait-ForBackend {
    param(
        [System.Diagnostics.Process]$Process,
        [int]$Port
    )

    for ($attempt = 0; $attempt -lt 50; $attempt++) {
        if ($Process.HasExited) {
            throw "Backend exited before opening port $Port (exit code $($Process.ExitCode))."
        }
        if (Test-TcpPort -ComputerName "127.0.0.1" -Port $Port) {
            return
        }
        [System.Threading.Thread]::Sleep(100)
    }

    throw "Backend did not open port $Port within 5 seconds."
}

try {
    $configContent = Get-Content -LiteralPath $configPath -Raw
    $configContent = $configContent -replace '(<logging\s+name="cycletime"\s+value=")100("\s+unit="ms")', '${1}10$2'
    Set-Content -LiteralPath $config10MsPath -Value $configContent -Encoding UTF8

    $backendProcess = Start-Process `
        -FilePath $pythonPath `
        -ArgumentList @("main.py", "--config", $configPath, "--host", "127.0.0.1", "--port", $port) `
        -WorkingDirectory $guiPath `
        -PassThru
    $backend10MsProcess = Start-Process `
        -FilePath $pythonPath `
        -ArgumentList @("main.py", "--config", $config10MsPath, "--host", "127.0.0.1", "--port", $port10Ms) `
        -WorkingDirectory $guiPath `
        -PassThru

    Wait-ForBackend -Process $backendProcess -Port $port
    Wait-ForBackend -Process $backend10MsProcess -Port $port10Ms

    $env:PROCESS_CONTROL_REST_URL = $restUrl
    $env:PROCESS_CONTROL_SIMULATED_REST_URL = $restUrl
    $env:PROCESS_CONTROL_SIMULATED_REST_URL_10MS = $restUrl10Ms
    Push-Location $guiPath
    try {
        & $pythonPath -m pytest tests -m simulation_tests -q
        $testExitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    exit $testExitCode
}
finally {
    if ($null -ne $backendProcess -and -not $backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force
        $backendProcess.WaitForExit()
    }
    if ($null -ne $backend10MsProcess -and -not $backend10MsProcess.HasExited) {
        Stop-Process -Id $backend10MsProcess.Id -Force
        $backend10MsProcess.WaitForExit()
    }
    if (Test-Path -LiteralPath $config10MsPath) {
        Remove-Item -LiteralPath $config10MsPath -Force
    }
    $env:PROCESS_CONTROL_REST_URL = $oldRestUrl
    $env:PROCESS_CONTROL_SIMULATED_REST_URL = $oldSimulatedRestUrl
    $env:PROCESS_CONTROL_SIMULATED_REST_URL_10MS = $oldSimulatedRestUrl10Ms
}
