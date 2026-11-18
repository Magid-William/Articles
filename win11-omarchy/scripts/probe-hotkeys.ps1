#Requires -Version 5.1
<#
.SYNOPSIS
    Reports which key combinations Windows lets you have, and which it keeps.

.DESCRIPTION
    RegisterHotKey returns 1409 (ERROR_HOTKEY_ALREADY_REGISTERED) for a combination
    another process owns. That single fact explains almost every "why is this binding
    different from Omarchy's" question:

      Win+1..9            -> 1409, Explorer's taskbar slots
      Win+Shift+1..9      -> 1409, new instance of the taskbar app
      Win+L, Win+Tab, ... -> 1409, the shell
      Alt+1..9, Ctrl+Alt+* -> free, which is why the keymap uses them

    Caveat this script cannot show you: Win+Alt+<letter> REGISTERS fine and still never
    reaches a low-level keyboard hook, because the shell and Xbox Game Bar handle that
    family first. If a Win+Alt binding does nothing despite being "free" here, that is why.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File probe-hotkeys.ps1
#>
[CmdletBinding()]
param()

if (-not ('HotkeyProbe' -as [type])) {
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class HotkeyProbe {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool UnregisterHotKey(IntPtr hWnd, int id);
}
"@
}

$MOD_ALT = 1; $MOD_CTRL = 2; $MOD_SHIFT = 4; $MOD_WIN = 8

$tests = @(
    @{ Name = 'Win+1';           Mods = $MOD_WIN;                                  Vk = 0x31 }
    @{ Name = 'Win+4';           Mods = $MOD_WIN;                                  Vk = 0x34 }
    @{ Name = 'Win+Shift+1';     Mods = ($MOD_WIN -bor $MOD_SHIFT);                Vk = 0x31 }
    @{ Name = 'Win+L';           Mods = $MOD_WIN;                                  Vk = 0x4C }
    @{ Name = 'Win+Tab';         Mods = $MOD_WIN;                                  Vk = 0x09 }
    @{ Name = 'Win+Alt+L';       Mods = ($MOD_WIN -bor $MOD_ALT);                  Vk = 0x4C }
    @{ Name = 'Win+J';           Mods = $MOD_WIN;                                  Vk = 0x4A }
    @{ Name = 'Win+Y';           Mods = $MOD_WIN;                                  Vk = 0x59 }
    @{ Name = 'Win+Space';       Mods = $MOD_WIN;                                  Vk = 0x20 }
    @{ Name = 'Alt+1';           Mods = $MOD_ALT;                                  Vk = 0x31 }
    @{ Name = 'Alt+Shift+1';     Mods = ($MOD_ALT -bor $MOD_SHIFT);                Vk = 0x31 }
    @{ Name = 'Ctrl+Alt+L';      Mods = ($MOD_CTRL -bor $MOD_ALT);                 Vk = 0x4C }
    @{ Name = 'Ctrl+Alt+Shift+1';Mods = ($MOD_CTRL -bor $MOD_ALT -bor $MOD_SHIFT); Vk = 0x31 }
    @{ Name = 'Ctrl+Alt+Enter';  Mods = ($MOD_CTRL -bor $MOD_ALT);                 Vk = 0x0D }
)

Write-Host "`ncombination          available   last error" -ForegroundColor Cyan
$id = 700
foreach ($t in $tests) {
    $id++
    $ok  = [HotkeyProbe]::RegisterHotKey([IntPtr]::Zero, $id, $t.Mods, [uint32]$t.Vk)
    $err = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
    if ($ok) { [HotkeyProbe]::UnregisterHotKey([IntPtr]::Zero, $id) | Out-Null }

    $verdict = if ($ok) { 'free' } elseif ($err -eq 1409) { 'owned by another process' } else { "error $err" }
    $colour  = if ($ok) { 'Green' } else { 'DarkYellow' }
    Write-Host ("{0,-20} {1}" -f $t.Name, $verdict) -ForegroundColor $colour
}

Write-Host @"

Notes
  * 'owned' means something already registered it - usually the shell. A low-level
    keyboard hook (AutoHotkey's #UseHook) can still consume those where Windows allows it;
    Win+L is the one it cannot.
  * Win+Alt registrations can look free here and still never arrive. Treat them as dead.
"@ -ForegroundColor DarkGray
