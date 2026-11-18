#Requires -Version 5.1
<#
.SYNOPSIS
    Installs win11-omarchy: komorebi + AutoHotkey v2 + the bar, entirely in user scope.

.DESCRIPTION
    No administrator rights, no MSI, no UAC prompt.
      1. downloads the komorebi release ZIP and verifies it against the published checksums
      2. unpacks it and a portable AutoHotkey v2 under %LOCALAPPDATA%\Programs
      3. appends both to the *user* PATH (previous value backed up first)
      4. keeps your existing configs as a backup, then installs the ones from this repo
      5. starts komorebi + bar, and registers both at logon

.PARAMETER KomorebiVersion
    Release tag to install. Default 0.1.41 (the version this repo was built against).

.PARAMETER NoAutostart
    Skip the shell:startup shortcuts.

.PARAMETER SkipStart
    Install only; do not start komorebi now.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File install.ps1
#>
[CmdletBinding()]
param(
    [string]$KomorebiVersion = "0.1.41",
    [switch]$NoAutostart,
    [switch]$SkipStart
)

$ErrorActionPreference = 'Stop'

function Step($n, $text) { Write-Host "`n[$n] $text" -ForegroundColor Cyan }
function Note($text)     { Write-Host "    $text" -ForegroundColor DarkGray }

$repoConfig = Join-Path $PSScriptRoot '..\config'
$programs   = Join-Path $env:LOCALAPPDATA 'Programs'
$kmDir      = Join-Path $programs "komorebi-$KomorebiVersion"
$ahkDir     = Join-Path $programs 'autohotkey-v2'
$stateDir   = Join-Path $env:USERPROFILE '.config\komorebi'
$backupDir  = Join-Path $stateDir 'backup'
$stage      = Join-Path $env:TEMP 'win11-omarchy-install'

New-Item -ItemType Directory -Force $programs, $stateDir, $backupDir, $stage | Out-Null

# ---------------------------------------------------------------- 1. komorebi
Step 1 "komorebi $KomorebiVersion"
$zip  = Join-Path $stage "komorebi-$KomorebiVersion-x86_64-pc-windows-msvc.zip"
$sums = Join-Path $stage 'checksums.txt'
$base = "https://github.com/LGUG2Z/komorebi/releases/download/v$KomorebiVersion"

if (-not (Test-Path $zip)) {
    Note "downloading $base/$(Split-Path $zip -Leaf)"
    Invoke-WebRequest "$base/checksums.txt" -OutFile $sums -UseBasicParsing
    Invoke-WebRequest "$base/$(Split-Path $zip -Leaf)" -OutFile $zip -UseBasicParsing
}
Note ("downloaded {0:N1} MB" -f ((Get-Item $zip).Length / 1MB))

$exeName  = Split-Path $zip -Leaf
$expected = (Get-Content $sums | Select-String -SimpleMatch $exeName).ToString().Split(' ')[0]
$actual   = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
if ($expected -ne $actual) { throw "SHA256 mismatch for $exeName`n expected $expected`n actual   $actual" }
Note 'SHA256 verified'

New-Item -ItemType Directory -Force $kmDir | Out-Null
Expand-Archive -Path $zip -DestinationPath $kmDir -Force
Note "unpacked to $kmDir"

# --------------------------------------------------------------- 2. hotkeys
Step 2 'AutoHotkey v2 (portable)'
$ahkZip = Join-Path $stage 'ahk-v2.zip'
if (-not (Test-Path $ahkZip)) {
    Note 'downloading ahk-v2.zip from autohotkey.com'
    Invoke-WebRequest 'https://www.autohotkey.com/download/ahk-v2.zip' -OutFile $ahkZip -UseBasicParsing
}
New-Item -ItemType Directory -Force $ahkDir | Out-Null
Expand-Archive -Path $ahkZip -DestinationPath $ahkDir -Force
Note "unpacked to $ahkDir"

# ------------------------------------------------------------------- 3. PATH
Step 3 'user PATH'
$before = [Environment]::GetEnvironmentVariable('Path', 'User')
$beforeFile = Join-Path $backupDir 'user-path-before.txt'
if (-not (Test-Path $beforeFile)) { Set-Content -Path $beforeFile -Value $before -NoNewline }
$parts = @($before.Split(';') | Where-Object { $_ })
$add   = @($kmDir, $ahkDir) | Where-Object { $parts -notcontains $_ }
if ($add) {
    [Environment]::SetEnvironmentVariable('Path', (($parts + $add) -join ';'), 'User')
    Note "added: $($add -join ', ')"
} else {
    Note 'already present'
}
$env:Path = "$kmDir;$ahkDir;$env:Path"   # for this session

# ----------------------------------------------------------------- 4. configs
Step 4 'configuration files'
$komic = Join-Path $kmDir 'komorebic.exe'
# generate komorebi.json, komorebi.bar.json, applications.json, whkdrc
& $komic quickstart | Out-Null

foreach ($f in @('komorebi.json', 'komorebi.bar.json', 'komorebi.ahk')) {
    $target = Join-Path $env:USERPROFILE $f
    if (Test-Path $target) {
        Copy-Item $target (Join-Path $backupDir "$f.bak") -Force
        Note "backed up existing $f"
    }
    Copy-Item (Join-Path $repoConfig $f) $target -Force
    Note "installed $f"
}
Note 'applications.json left as generated (stock app rules) - see config/applications.chrome-pip.json'

# -------------------------------------------------------------- 5. start + login
if (-not $SkipStart) {
    Step 5 'starting komorebi'
    Get-Process komorebi -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Milliseconds 500
    Start-Process (Join-Path $kmDir 'komorebi.exe') -ArgumentList '--clean-state' -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Start-Process (Join-Path $kmDir 'komorebi-bar.exe') -WindowStyle Hidden
    Start-Process (Join-Path $ahkDir 'AutoHotkey64.exe') -ArgumentList ('"' + (Join-Path $env:USERPROFILE 'komorebi.ahk') + '"')
    Note 'komorebi, bar and keymap are running (windows opened before now are not managed - reopen them)'
}

if (-not $NoAutostart) {
    Step 6 'autostart at logon'
    & $komic enable-autostart --bar | Out-Null
    $wsh = New-Object -ComObject WScript.Shell
    $lnk = $wsh.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Startup')) 'komorebi-hotkeys.lnk'))
    $lnk.TargetPath = Join-Path $ahkDir 'AutoHotkey64.exe'
    $lnk.Arguments = '"' + (Join-Path $env:USERPROFILE 'komorebi.ahk') + '"'
    $lnk.Description = 'komorebi keymap (AutoHotkey v2)'
    $lnk.Save()
    Note 'komorebi.lnk + komorebi-hotkeys.lnk written to shell:startup'
}

Write-Host "`nDone." -ForegroundColor Green
Write-Host @"
Next:
  * shortcuts .......... ..\SHORTCUTS.md
  * make PiP sticky .... komorebic ignore-rule title "Picture in picture"
  * pause tiling ....... Ctrl+Alt+Shift+X
  * uninstall .......... scripts\uninstall.ps1 -Yes

Optional, needs administrator: enable long path support and/or run komorebi from an
elevated scheduled task if you want windows of admin apps tiled too.
"@ -ForegroundColor DarkGray
