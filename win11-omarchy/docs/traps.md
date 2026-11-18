# When it stops working

Symptom first. The cause is rarely where you are looking, and the hotkey log answers most of it before you open anything else:

```powershell
Get-Content "$env:USERPROFILE\.config\komorebi\ahk-errors.log" -Tail 20
```

A `fire: <command>` line means the key reached AutoHotkey and `komorebic` was called. No line means Windows ate the combination — go to [the reserved-key table](../README.md#11-windows-fights-back) rather than editing the keymap.

| Symptom | Most likely cause | Do this |
|---|---|---|
| A key does nothing, no `fire:` line | Windows owns the combination | `scripts/probe-hotkeys.ps1`, then pick another binding |
| A key does nothing, but `fire:` is logged | `komorebic` ran, komorebi refused | check `komorebic state`, look at the layout/window it targeted |
| `Super+1` both switches workspace **and** activates a taskbar app | AutoHotkey is in `RegisterHotKey` mode | confirm `#UseHook True` is the first lines of `komorebi.ahk` |
| Workspaces switch, but no window ever moves | komorebi manages nothing (windows predate it) | close and reopen the apps; `komorebic state` shows zero containers |
| Windows disappear after a workspace switch and do not come back | an old komorebi instance died while windows were hidden | `komorebic start --bar`, then `komorebic restore-windows` |
| The bar is gone but tiling still works | `komorebi-bar.exe` exited | it self-restarts within 15 s (keymap supervisor); if not, start it by hand |
| Bar shows 10 workspaces again | `komorebi.json` reverted, or you focused a non-existent workspace index | the config defines 4; remove the extra keys from the keymap |
| Scrolling layout shows 3 columns | `layout_defaults` missing or overridden per workspace | `komorebic scrolling-layout-columns 2` |
| A tray icon never appears in the bar | the app does not handle `TaskbarCreated` | nothing to fix in the bar; the native tray is its only home |
| `Ctrl+Alt+L` does nothing and no `fire:` | the combination is being eaten by something else | `scripts/probe-hotkeys.ps1`; try `Super+Y` cycling instead |
| Everything is tiled and you need it to stop | — | `Ctrl+Alt+Shift+X` (pause) or `komorebic stop` (restore and quit) |

## Reading komorebi's own state

```powershell
komorebic state | ConvertFrom-Json |
  % { $_.monitors.elements[0].workspaces.elements } |
  % { "{0}: {1} containers, layout {2}" -f $_.name, $_.containers.elements.Count, $_.layout.Default }
```

Zero containers across every workspace means it is not a layout problem, it is an adoption problem.

## When the config stops loading

```powershell
komorebic check          # parses komorebi.json, komorebi.bar.json, applications.json
komorebic configuration  # where it is actually looking
```

## Starting over without losing the session

```powershell
komorebic stop            # kills tiling, un-hides every window, leaves apps running
komorebic start --bar     # fresh state, same windows, but they will need reopening to tile
```

`--clean-state` additionally ignores the state dump from the previous run; use it when the layout has got itself into a shape you cannot explain.
