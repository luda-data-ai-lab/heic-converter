# 개발용 실행 (Windows PowerShell 5.1+). exe를 만들지 않고 소스에서 바로 실행합니다.
#   .\scripts\dev.ps1               -> 창(GUI) 실행
#   .\scripts\dev.ps1 D:\Photos     -> 창을 열고 해당 폴더를 바로 변환
#   .\scripts\dev.ps1 -Cli D:\Photos -f png   -> 명령줄(CLI) 실행
#   .\scripts\dev.ps1 -Test         -> ruff + pytest
param([switch]$Cli, [switch]$Test, [Parameter(ValueFromRemainingArguments = $true)][string[]]$Rest)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv가 없습니다. 설치: powershell -ExecutionPolicy ByPass -c \"irm https://astral.sh/uv/install.ps1 | iex\"" -ForegroundColor Yellow
    exit 1
}
uv sync
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($Test) {
    uv run ruff check .
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    uv run pytest -q
    exit $LASTEXITCODE
}
if ($Cli) {
    uv run heic-convert @Rest
} else {
    uv run heic-converter @Rest
}
exit $LASTEXITCODE
