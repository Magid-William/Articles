# Windows 11, the Omarchy way

Four workspaces on `Super+1…4`, windows that tile themselves, arrows that move focus, and a thin bar on top with your tray icons in it. No mouse required, no administrator rights, nothing to compile.

You are not installing a Linux desktop. You are putting the Omarchy muscle memory on top of Windows: [komorebi](https://github.com/LGUG2Z/komorebi) does the tiling, [AutoHotkey](https://www.autohotkey.com/) turns your keypresses into commands, and `komorebi-bar` draws the bar. Three small processes, about 30 MB of downloads, half an hour of setup.

Everything below was built and tested on Windows 11 build 26200 with komorebi 0.1.41. Most of the odd-looking decisions are Windows' fault, not taste — [section 11](#11-windows-fights-back) explains each one, and [ARTICLE.md](./ARTICLE.md) has the receipts.

## Contents

1. [What you get](#1-what-you-get)
2. [The three pieces](#2-the-three-pieces)
3. [Install in four steps](#3-install-in-four-steps)
4. [Workspaces](#4-workspaces)
5. [Navigating windows](#5-navigating-windows)
6. [Layouts](#6-layouts)
7. [Window state](#7-window-state)
8. [Groups](#8-groups)
9. [Launching things](#9-launching-things)
10. [The bar](#10-the-bar)
11. [Windows fights back](#11-windows-fights-back)
12. [Things that will bite you](#12-things-that-will-bite-you)
13. [Getting out](#13-getting-out)
14. [Files](#14-files)

## 1. What you get

You press `Super+2` and the screen becomes workspace 2, with its own windows, exactly like Hyprland on Omarchy. Windows opened while you are there stay there. `Super+←` moves focus left; `Super+Shift+←` moves the *window* left. Nothing overlaps, nothing is dragged, and the gaps are zero because a dense grid is the point.

The shortcuts follow Omarchy's [navigation manual](https://omarchy.org/manual/navigation) wherever Windows allows it:

| You want | You press |
|---|---|
| workspace 2 | `Super+2` |
| move this window to workspace 3 and follow it | `Super+Shift+3` |
| move it there while you stay put | `Ctrl+Alt+Shift+3` |
| focus the window to the right | `Super+→` |
| swap it with its neighbour | `Super+Shift+→` |
| stack two windows instead of splitting | `Super+J` |
| scrolling layout with two visible columns | `Ctrl+Alt+L` |
| float / unfloat | `Super+T` |
| close | `Super+Q` |

Full reference: [SHORTCUTS.md](./SHORTCUTS.md).

## 2. The three pieces

**komorebi** is a tiling window manager that extends the Windows Desktop Window Manager. It moves and sizes windows, keeps four virtual workspaces per monitor, and hides what is not on screen.

**komorebic** is how you talk to it: one process, one command, one effect. `komorebic focus-workspaces 1` is "go to workspace 2". That is the entire API you need.

**AutoHotkey** is the keyboard. This matters more than it sounds. komorebi's own documentation says it plainly:

> neither `komorebi.exe` nor `komorebic.exe` handle key bindings, because `komorebi` is a tiling window manager and not a hotkey daemon.

So something has to translate a keypress into a `komorebic` call. The official companion is [whkd](https://github.com/LGUG2Z/whkd), and it cannot take `Super+1…9` — that is the single fact that shapes this whole setup. Windows registers `Win+digit` for the taskbar, and whkd uses `RegisterHotKey`, which fails with error 1409 on a combination Windows already owns. AutoHotkey can drop one level lower, to a keyboard hook, and consume the key before Explorer sees it.

**komorebi-bar** is the bar at the top: workspaces, layout, focused window, tray icons, clock. It ships in the same archive.

## 3. Install in four steps

No MSI, no `winget` prompt, no admin. The archive is unpacked into your own profile and added to your user `PATH`.

```powershell
# 1. komorebi, verified against the release checksums
$stage = "$env:TEMP\komorebi"
Invoke-WebRequest "https://github.com/LGUG2Z/komorebi/releases/download/v0.1.41/checksums.txt" -OutFile "$stage.sums"
Invoke-WebRequest "https://github.com/LGUG2Z/komorebi/releases/download/v0.1.41/komorebi-0.1.41-x86_64-pc-windows-msvc.zip" -OutFile "$stage.zip"
# compare (Get-FileHash "$stage.zip").Hash with the line in checksums.txt, then:
Expand-Archive "$stage.zip" "$env:LOCALAPPDATA\Programs\komorebi-0.1.41"

# 2. AutoHotkey v2, portable
Invoke-WebRequest "https://www.autohotkey.com/download/ahk-v2.zip" -OutFile "$env:TEMP\ahk-v2.zip"
Expand-Archive "$env:TEMP\ahk-v2.zip" "$env:LOCALAPPDATA\Programs\autohotkey-v2"

# 3. put both on your user PATH, then generate the stock configs
$env:Path = "$env:LOCALAPPDATA\Programs\komorebi-0.1.41;$env:LOCALAPPDATA\Programs\autohotkey-v2;$env:Path"
komorebic quickstart        # writes komorebi.json, komorebi.bar.json, applications.json to %USERPROFILE%

# 4. replace the generated configs with the ones in this folder, then start
Copy-Item .\config\komorebi.json, .\config\komorebi.bar.json $env:USERPROFILE -Force
Copy-Item .\config\komorebi.ahk $env:USERPROFILE -Force
komorebic start --bar
```

Then the bar process and the keymap, and autostart:

```powershell
# keymap
Start-Process "$env:LOCALAPPDATA\Programs\autohotkey-v2\AutoHotkey64.exe" '"C:\...\komorebi.ahk"'

# autostart at logon (user-level: no UAC, no scheduled task)
komorebic enable-autostart --bar
$s = New-Object -ComObject WScript.Shell
$l = $s.CreateShortcut("$([Environment]::GetFolderPath('Startup'))\komorebi-hotkeys.lnk")
$l.TargetPath = "$env:LOCALAPPDATA\Programs\autohotkey-v2\AutoHotkey64.exe"
$l.Arguments = '"' + $env:USERPROFILE + '\komorebi.ahk"'
$l.Save()
```

`scripts/install.ps1` in this folder does all of it, including the hash check, the `PATH` backup, and both shortcuts. `scripts/uninstall.ps1` removes exactly what it created.

Two optional, admin-only extras that the install deliberately skips: enabling `LongPathsEnabled` in the registry (komorebi's docs recommend it) and running komorebi elevated so it can also tile windows of administrator apps.

## 4. Workspaces

Four, not ten. `Super+1` through `Super+4`, and the bar shows four numbers.

Ten workspaces is what Omarchy ships and what komorebi's example config does — and it looks wrong on a Windows bar, because six of them are always empty. Four is what a 2560-wide screen actually holds. Want more? Add entries to `monitors[0].workspaces` in `komorebi.json`, restart, and extend the digit keys in `komorebi.ahk`; focusing a non-existent index silently creates it, which would also put it back in the bar.

| Keys | Action |
|---|---|
| `Super+1…4` | go to that workspace |
| `Alt+1…4` | same, for when the shell steals the Super version |
| `Super+Shift+1…4` | move the focused window there and follow it |
| `Ctrl+Alt+Shift+1…4` | move it there and stay where you are |
| `Super+Tab` / `Super+Shift+Tab` | next / previous workspace |
| `Super+Ctrl+Tab` | back to the last one |

The `Alt+digit` duplicates exist because `Win+digit` is Explorer's; see [section 11](#11-windows-fights-back).

## 5. Navigating windows

`Super+←↑→↓` moves focus in that direction — Vim-style, but with arrows so it works while you are still learning. `Super+Shift+←↑→↓` takes the focused window and drops it on that side, swapping with whatever was there.

There is no "move to the next monitor" here because this machine has one screen. komorebi can do it with `cycle-send-to-monitor next` if you add a second.

## 6. Layouts

The default is **BSP**: the first window takes half the screen, the next takes half of what is left, and so on. `Super+J` turns the split vertical so windows stack on top of each other; `Super+Shift+J` puts them back side by side. That is Omarchy's `Super+J`, expressed as two keys instead of a toggle, because komorebi takes a target layout rather than flipping.

`Super+Y` walks the layout list — BSP, columns, rows, vertical stack, horizontal stack, ultrawide stack, grid, right-main stack, scrolling — and `Super+Shift+Y` walks back.

`Ctrl+Alt+L` is the interesting one. It toggles **scrolling**: windows line up side by side and continue past the right edge of the display. Two things are worth knowing:

- Omarchy's scrolling shows **two** columns; komorebi's default is **three**. `layout_defaults.Scrolling.layout_options.columns = 2` in `komorebi.json` fixes it permanently, and the toggle applies it every time regardless.
- It is a real toggle. The keymap asks komorebi what the current layout is (`komorebic query focused-workspace-layout`) and returns you to it — so if you were in `vertical-stack`, `Ctrl+Alt+L` twice leaves you in `vertical-stack`, not BSP.

Direct jumps, if you do not want to cycle: `Ctrl+Alt+B` bsp, `Ctrl+Alt+V` vertical-stack, `Ctrl+Alt+H` horizontal-stack, `Ctrl+Alt+G` grid.

## 7. Window state

`Super+T` floats the focused window (and unfloats it). Floating means "not tiled, I will place it myself" — it still belongs to its workspace.

`Super+F` is fullscreen in the tiling sense (komorebi calls it monocle: the window fills the workspace and its neighbours hide). `Ctrl+Alt+F` maximises inside the work area so the bar stays visible, and `Ctrl+Alt+Shift+F` sends `F11` to the window itself, which is what you want for a browser video. `Super+Q` closes, `Ctrl+Alt+M` minimises.

## 8. Groups

Omarchy groups windows into tabs with `Super+G`. komorebi's equivalent is a *stack*: `Ctrl+Alt+Shift+G` stacks everything on the workspace into one tabbed container, `Ctrl+Alt+Shift+U` releases it, and `Ctrl+Alt+Shift+←→` walks the tabs. There is no per-pair grouping key — komorebi stacks per workspace, which in practice is what you want: one tabbed container, everything in it.

## 9. Launching things

Thin wrappers, so your hands never leave the keyboard: `Ctrl+Alt+Enter` terminal (Windows Terminal), `Ctrl+Alt+Shift+Enter` browser, `Super+Shift+F` Explorer, `Ctrl+Alt+T` Task Manager.

`` Super+` `` is the quake console: `wt -w _quake` drops Windows Terminal's own quake window over whatever you are doing, and running it again puts it away.

## 10. The bar

Twenty-eight pixels tall, at the top, because 50 (the default) eats a line of your screen for no reason:

```json
"height": 28,
"font_size": 12,
"padding": { "horizontal": 10, "vertical": 2 }
```

Left to right: workspaces, layout, focused window title, tray icons, date, clock. The clock is 12-hour without seconds (`"format": "TwelveHourWithoutSeconds"`).

**Tray icons** come from the `Systray` widget (new in 0.1.41). It cannot enumerate the existing tray on Windows 11 — it broadcasts `TaskbarCreated` and collects whatever re-registers, so an app that does not handle that message never appears, and neither does anything it registered before the bar started. Icons that show up in the native taskbar's overflow tray usually *do* appear, since the shell re-registers them on the same broadcast.

Two useful knobs: `"hidden_icons": ["OneDrive.exe"]` to drop noisy ones, and `"info_button": "Overflow"` to add a button that lists every icon with its exe, tooltip and GUID — copy exact names from there.

## 11. Windows fights back

Every deviation from Omarchy's keymap is Windows holding a combination hostage. Check it yourself before blaming the keymap:

```powershell
# scripts/probe-hotkeys.ps1 does this for a list of combinations
Add-Type @"
using System;using System.Runtime.InteropServices;
public class RH{ [DllImport("user32.dll", SetLastError=true)] public static extern bool RegisterHotKey(IntPtr h, int id, uint mods, uint vk); }
"@
[RH]::RegisterHotKey([IntPtr]::Zero, 1, 8, 0x31)   # MOD_WIN + "1"
[Runtime.InteropServices.Marshal]::GetLastWin32Error()
```

| Combination | Result | Consequence |
|---|---|---|
| `Win+1…9` | error 1409, "already registered" — Explorer owns it | `Alt+digit` duplicates for workspaces |
| `Win+Shift+1…9` | same | the "move and follow" keys also exist on `Alt+Shift` |
| `Win+Alt+<letter>` | registers fine, but the shell/Game Bar swallows it before AutoHotkey's hook sees it | every "Alt under Super" key was moved to `Ctrl+Alt` |
| `Win+L` | the lock screen, cannot be intercepted | layout cycling lives on `Super+Y`, not `Super+L` |
| `Win+W`, `Win+M`, `Win+Tab`, `Win+F` | taken by Widgets, minimise-all, Task View, Feedback | close is `Super+Q`, minimise `Ctrl+Alt+M` |
| `Win+Space` | keyboard layout switch — do not touch it if you type more than one language | unused on purpose |

There is a second trap underneath: **AutoHotkey implements hotkeys with `RegisterHotKey` by default**, which *adds* a handler instead of consuming the keystroke. So `Super+1` fired komorebi *and* Explorer's taskbar action — two things at once. `#UseHook True` at the top of the script is what prevents that; it moves every hotkey onto the low-level keyboard hook, which can swallow the key. If a key ever does two things, that line is the first thing to check.

## 12. Things that will bite you

**komorebi only tiles windows that appear while it is running.** Windows that were already open are never adopted — not by restarting it, not by `komorebic manage`, not by `force-focus` followed by `manage`. Close and reopen the app once and it joins the layout. This looks like "the workspaces do nothing" on day one, which is exactly what it is: the workspaces are fine, there is just nothing in them.

**Floating is not sticky.** A floated window is hidden when you switch workspace. What stays on screen everywhere is an *unmanaged* window, because komorebi never hides what it does not manage. That is the trick for a picture-in-picture video:

```powershell
komorebic ignore-rule title "Picture in picture"
```

Chrome's PiP window is titled exactly that, so from the next PiP onward komorebi ignores it: it sits on top of every workspace, draggable, exactly like Omarchy's popped window (`Super+O`). Rules apply to windows created after them, so close the current PiP and reopen it. For permanence, add the same rule to your app-specific configuration:

```json
"Google Chrome": {
  "ignore_rules": [
    { "kind": "Title", "id": "Picture in picture", "matching_strategy": "Equals" }
  ]
}
```

**The bar can die quietly.** In my first day it exited with no panic and no Windows error record, at the moment a terminal window closed — the systray widget tracks tray-icon owner windows, and a window being destroyed is its weak spot. komorebi kept tiling; only the bar vanished. The keymap now supervises it: every 15 seconds, if `komorebi-bar.exe` is missing, it is relaunched. `bar missing, restarting` in the log means it happened.

**Every hotkey press is logged** to `%USERPROFILE%\.config\komorebi\ahk-errors.log`. A `fire:` line means the key reached AutoHotkey and the command was sent; silence means Windows ate the combination. That one file turns "this key does nothing" into a two-second diagnosis.

## 13. Getting out

```powershell
komorebic stop            # stop tiling, restore every hidden window
komorebic start --bar     # bring it back
```

`scripts/uninstall.ps1` removes the two program folders, the configs, the keymap, both autostart shortcuts, and restores your `PATH` from the backup taken at install time. It touches nothing else.

## 14. Files

| Path | What |
|---|---|
| `komorebi.json` | four workspaces, 0 px gaps, borders off, scrolling = 2 columns |
| `komorebi.bar.json` | 28 px bar, tray, 12-hour clock, workspaces widget |
| `komorebi.ahk` | the keymap: every binding, the layout toggle, the bar supervisor |
| `applications.json` | per-app rules — the big stock one, plus the Chrome PiP ignore rule |
| `%USERPROFILE%\.config\komorebi\` | logs, PATH backup, uninstall script |

- [ARTICLE.md](./ARTICLE.md) — how all of this was established, with the failed attempts and the evidence
- [SHORTCUTS.md](./SHORTCUTS.md) — every binding in one place
- [docs/traps.md](./docs/traps.md) — symptom → cause → fix, for when something stops working
- [config/](./config) and [scripts/](./scripts) — the files themselves
