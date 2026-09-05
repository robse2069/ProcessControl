$repoRoot = Split-Path -Parent $PSScriptRoot
$activateScript = Join-Path $repoRoot '.venv\Scripts\Activate.ps1'

if (-not (Test-Path -LiteralPath $activateScript -PathType Leaf)) {
    Write-Error "Project virtual environment not found. Create it with: python3 -m venv `"$repoRoot\.venv`""
    return
}

. $activateScript
