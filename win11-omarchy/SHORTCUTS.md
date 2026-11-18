# Shortcuts

`Super` is the Windows key. Everything below is live in [config/komorebi.ahk](./config/komorebi.ahk); 46 bindings, nothing else.

Why some rows have an `Alt` or `Ctrl+Alt` twin: [README §11](./README.md#11-windows-fights-back). Short version — Windows owns `Win+digit` and swallows `Win+Alt`, so those two families are duplicated onto combinations it does not touch.

## Workspaces (four: `1`–`4`)

| Keys | Action |
|---|---|
| `Super+1` … `Super+4` | go to workspace 1–4 |
| `Alt+1` … `Alt+4` | same, Windows-key-free duplicate |
| `Super+Shift+1` … `4` | move focused window there, follow it |
| `Alt+Shift+1` … `4` | same, Windows-key-free duplicate |
| `Ctrl+Alt+Shift+1` … `4` | move focused window there, stay put |
| `Super+Tab` | next workspace |
| `Super+Shift+Tab` | previous workspace |
| `Super+Ctrl+Tab` | last workspace |

## Navigation

| Keys | Action |
|---|---|
| `Super+←` `↑` `→` `↓` | focus the window in that direction |
| `Super+Shift+←` `↑` `→` `↓` | swap the focused window in that direction |

## Layouts

| Keys | Action |
|---|---|
| `Super+J` | stack vertically (`vertical-stack`) |
| `Super+Shift+J` | side by side (`bsp`) |
| `Super+Y` | next layout |
| `Super+Shift+Y` | previous layout |
| `Ctrl+Alt+L` | toggle scrolling (2 columns) ↔ the layout you came from |
| `Ctrl+Alt+B` | bsp |
| `Ctrl+Alt+V` | vertical-stack |
| `Ctrl+Alt+H` | horizontal-stack |
| `Ctrl+Alt+G` | grid |

## Window state

| Keys | Action |
|---|---|
| `Super+Q` | close |
| `Super+T` | toggle floating / tiled |
| `Super+F` | fullscreen (monocle) |
| `Ctrl+Alt+F` | full width / maximise, bar stays visible |
| `Ctrl+Alt+Shift+F` | send `F11` to the window (in-app fullscreen) |
| `Ctrl+Alt+M` | minimise |

## Groups (komorebi stacks)

| Keys | Action |
|---|---|
| `Ctrl+Alt+Shift+G` | stack every window on the workspace |
| `Ctrl+Alt+Shift+U` | unstack |
| `Ctrl+Alt+Shift+←` / `→` | previous / next window in the stack |

## Applications

| Keys | Action |
|---|---|
| `Ctrl+Alt+Enter` | Windows Terminal |
| `Ctrl+Alt+Shift+Enter` | default browser |
| `Super+Shift+F` | File Explorer |
| `Ctrl+Alt+T` | Task Manager |
| `` Super+` `` | quake console (`wt -w _quake`) |

## System

| Keys | Action |
|---|---|
| `Ctrl+Alt+Shift+X` | pause / resume tiling |

## Commands worth knowing

```bash
komorebic focus-workspaces 0             # workspace 1
komorebic move-to-workspace 1            # send window to workspace 2, follow
komorebic send-to-workspace 1            # send it, stay
komorebic change-layout scrolling        # Ctrl+Alt+L
komorebic scrolling-layout-columns 2     # two visible columns
komorebic cycle-layout next              # Super+Y
komorebic stack-all / unstack-all        # Ctrl+Alt+Shift+G / U
komorebic ignore-rule title "Picture in picture"   # make PiP sticky
komorebic toggle-pause                   # Ctrl+Alt+Shift+X
komorebic state                          # full JSON state
komorebic query focused-workspace-layout # what layout am I in
komorebic stop / start --bar             # off / on
```

## Not bound on purpose

| Combination | Reason |
|---|---|
| `Win+Space` | Windows keyboard-layout switch |
| `Win+L` | lock screen, uninterceptable |
| `Win+W`, `Win+M`, `Win+Tab`, `Win+F` | Widgets, minimise-all, Task View, Feedback Hub |
| `Super` + mouse drag | no modifier-drag in komorebi; use window borders |
| `Super+O` (Omarchy pop) | see the PiP ignore rule instead |
