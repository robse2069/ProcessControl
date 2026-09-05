$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$guiPath = Join-Path $repoRoot "GUI"
$pythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"
$port = 8765
$restUrl = "http://127.0.0.1:$port/api/v1"
$backendProcess = $null

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

try {
    $backendProcess = Start-Process `
        -FilePath $pythonPath `
        -ArgumentList @("main.py", "--host", "127.0.0.1", "--port", $port) `
        -WorkingDirectory $guiPath `
        -PassThru

    $ready = $false
    for ($attempt = 0; $attempt -lt 50; $attempt++) {
        if ($backendProcess.HasExited) {
            throw "Backend exited before opening port $port (exit code $($backendProcess.ExitCode))."
        }
        if (Test-TcpPort -ComputerName "127.0.0.1" -Port $port) {
            $ready = $true
            break
        }
        [System.Threading.Thread]::Sleep(100)
    }

    if (-not $ready) {
        throw "Backend did not open port $port within 5 seconds."
    }

    $env:PROCESS_CONTROL_REST_URL = $restUrl
    Push-Location $guiPath
    try {
        & $pythonPath -m pytest tests -q
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
}
