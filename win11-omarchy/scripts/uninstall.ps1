#Requires -Version 5.1
<#
.SYNOPSIS
    Removes exactly what install.ps1 created. Nothing else.

.DESCRIPTION
    Stops komorebi, the bar and the keymap; restores your user PATH from the backup
    taken at install time; deletes the two program folders, the generated configs,
    the keymap and both autostart shortcuts.

    Your own files are never touched: no application data, no personal documents,
    no other shortcuts in shell:startup.

.PARAMETER Yes
    Actually do it. Without this the script only prints what it would remove.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File uninstall.ps1 -Yes
#>
[CmdletBinding()]
param([switch]$Yes)

$ErrorActionPreference = 'SilentlyContinue'

$programs  = Join-Path $env:LOCALAPPDATA 'Programs'
$stateDir  = Join-Path $env:USERPROFILE '.config\komorebi'
$startup   = [Environment]::GetFolderPath('Startup')

$kmDirs  = @(Get-ChildItem $programs -Directory -Filter 'komorebi-*' | Select-Object -ExpandProperty FullName)
$ahkDir  = Join-Path $programs 'autohotkey-v2'
$configs = @(
    (Join-Path $env:USERPROFILE 'komorebi.json'),
    (Join-Path $env:USERPROFILE 'komorebi.bar.json'),
    (Join-Path $env:USERPROFILE 'komorebi.ahk'),
    (Join-Path $env:USERPROFILE 'applications.json'),
    (Join-Path $env:USERPROFILE '.config\whkdrc')
)
$shortcuts = @(
    (Join-Path $startup 'komorebi.lnk'),
    (Join-Path $startup 'komorebi-hotkeys.lnk')
)

Write-Host "This will remove:" -ForegroundColor Cyan
@($kmDirs) + @($ahkDir) + @($configs) + @($shortcuts) + @((Join-Path $env:LOCALAPPDATA 'komorebi')) |
    Where-Object { $_ -and (Test-Path $_) } | ForEach-Object { Write-Host "  $_" }
Write-Host "and restore your user PATH from $stateDir\backup\user-path-before.txt"

if (-not $Yes) {
    Write-Host "`nDry run. Re-run with -Yes to proceed." -ForegroundColor Yellow
    return
}

# 1. stop everything
$komic = Get-ChildItem $programs -Directory -Filter 'komorebi-*' |
         ForEach-Object { Join-Path $_.FullName 'komorebic.exe' } |
         Where-Object { Test-Path $_ } | Select-Object -First 1
if ($komic) { & $komic stop --bar | Out-Null }
Start-Sleep -Seconds 1
Get-Process komorebi, komorebi-bar | Stop-Process -Force
Get-CimInstance Win32_Process -Filter "Name='AutoHotkey64.exe'" |
    Where-Object { $_.CommandLine -match 'komorebi\.ahk' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

# 2. PATH
$backup = Join-Path $stateDir 'backup\user-path-before.txt'
if (Test-Path $backup) {
    [Environment]::SetEnvironmentVariable('Path', (Get-Content $backup -Raw), 'User')
    Write-Host 'PATH restored from backup'
} else {
    $cur   = [Environment]::GetEnvironmentVariable('Path', 'User')
    $keep  = $cur.Split(';') | Where-Object { $_ -and ($_ -notmatch 'komorebi-') -and ($_ -notmatch 'autohotkey-v2') }
    [Environment]::SetEnvironmentVariable('Path', ($keep -join ';'), 'User')
    Write-Host 'PATH cleaned (no backup found)'
}

# 3. files
foreach ($p in @($shortcuts) + @($configs) + @($kmDirs) + @($ahkDir) + @((Join-Path $env:LOCALAPPDATA 'komorebi'))) {
    if ($p -and (Test-Path $p)) {
        Remove-Item $p -Force -Recurse
        Write-Host "removed $p"
    }
}

Write-Host "`nDone. Backups and this script are still in $stateDir - delete that folder to finish." -ForegroundColor Green
