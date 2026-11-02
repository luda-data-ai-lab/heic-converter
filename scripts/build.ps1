# HEICConverter.exe 로컬 빌드 (Windows PowerShell 5.1+)
#   .\scripts\build.ps1          -> dist\HEICConverter.exe (GUI), dist\HEICConverter-cli.exe
#   .\scripts\build.ps1 -Clean   -> build/dist 폴더를 지우고 다시 빌드
#   .\scripts\build.ps1 -Installer -> 설치 파일 dist\HEICConverter-Setup-<버전>.exe도 생성 (Inno Setup 6 필요)
param([switch]$Clean, [switch]$Installer)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv가 없습니다. 설치: powershell -ExecutionPolicy ByPass -c \"irm https://astral.sh/uv/install.ps1 | iex\"" -ForegroundColor Yellow
    exit 1
}
if ($Clean) {
    foreach ($d in @("build", "dist", "packaging\build")) {
        if (Test-Path $d) { Remove-Item -Recurse -Force $d }
    }
}

uv sync --group build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
uv run python packaging/version_info.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
uv run pyinstaller --noconfirm --distpath dist --workpath build packaging/HEICConverter.spec
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& (Join-Path (Get-Location) "dist\HEICConverter-cli.exe") --version
$exe = Join-Path (Get-Location) "dist\HEICConverter.exe"
if ($Installer) {
    $iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
    if (-not (Test-Path $iscc)) { $iscc = Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe" }
    if (-not (Test-Path $iscc)) {
        Write-Host "Inno Setup 6이 없습니다. 설치: winget install JRSoftware.InnoSetup" -ForegroundColor Yellow
        exit 1
    }
    $v = uv run python -c "import heic_converter; print(heic_converter.__version__)"
    & $iscc /Qp "/DAppVersion=$v" packaging\installer.iss
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "설치 파일: dist\HEICConverter-Setup-$v.exe" -ForegroundColor Green
}
Write-Host ""
Write-Host "완료: $exe" -ForegroundColor Green
Write-Host "사용: HEICConverter.exe를 더블클릭하거나, HEIC 폴더를 아이콘 위에 끌어다 놓으세요."
