# How this was built

Notes from one evening spent turning Windows 11 into something with Omarchy's muscle memory. Not a tutorial — the tutorial is [README.md](./README.md). This is the reasoning, the dead ends, and the measurements, so that the next person does not spend the same evening on the same walls.

Tested on Windows 11 build 26200, komorebi 0.1.41, AutoHotkey 2.0.31, one 2560×1440 display.

## The shape of the problem

Omarchy is Arch + Hyprland + waybar + a curated keymap. On Windows the equivalents are not one program but four:

| Need | Omarchy | Windows answer |
|---|---|---|
| tile and hide windows | Hyprland | komorebi |
| command channel | `hyprctl` | `komorebic` |
| keypress → command | Hyprland's own bindings | AutoHotkey (or whkd) |
| status bar | waybar | `komorebi-bar` |

The one piece with no clean equivalent is the keyboard, and it turns out to be 80% of the work.

## Why not whkd

komorebi's documented companion is `whkd`, and it is a reasonable little daemon. It cannot do `Super+1`. Its dependency `win-hotkeys` is a wrapper over `RegisterHotKey`, and Windows already owns `Win+1…9` for taskbar slots. You can measure that:

```
Win+1 … Win+9   RegisterHotKey → 1409 (ERROR_HOTKEY_ALREADY_REGISTERED)
Alt+1 … Alt+9   RegisterHotKey → free
```

`Win+Alt+<letter>` is worse: it *registers* successfully, then never arrives, because the shell and the Xbox Game Bar handle that family before anything user-level sees it. That is not a documented promise anywhere; it is what the keyboard probe showed after a binding silently did nothing.

komorebi's own docs point at AutoHotkey for exactly this case, so that is the path taken.

## The double-fire, and `#UseHook`

First attempt with AutoHotkey v2 did this: `Super+1` switched komorebi's workspace *and* Explorer activated the first taskbar item. Both, every time. The hotkey log recorded the press, so AutoHotkey was working.

The cause is AutoHotkey's default hotkey implementation: `RegisterHotKey`. Registering a combination does not stop the other handler; it adds one. To consume the keystroke you need the low-level keyboard hook:

```ahk
#UseHook True
```

You can prove which mode is active: with the hook, the combination is *free* to register — AutoHotkey no longer holds it, it intercepts it instead. `Ctrl+Alt+Shift+X` returned 1409 while the old script ran, and free after the change.

Two smaller fixes came out of the same investigation:

- `Run` instead of `RunWait` in the key handler. `RunWait` blocks the hotkey thread for the ~200 ms `komorebic` takes; nothing good comes of holding a hotkey handler open.
- `Win+Alt` bindings were all abandoned. `Ctrl+Alt` is free across the board, is never claimed by the shell, and is what the substitutions use now.

## Making the layout toggle a real toggle

Omarchy's `Super+L` cycles dwindle → scrolling → floating on one key. `Win+L` is the lock screen and cannot be intercepted, so the equivalent went to `Super+Y` (cycle) and `Ctrl+Alt+L` (scrolling toggle).

The toggle needed state. komorebi has no "toggle between these two layouts", but it can report its own state:

```
$ komorebic query focused-workspace-layout
VerticalStack
```

So the keymap remembers what you were in, asks before switching, and returns you there:

```ahk
ToggleScrolling() {
    cur := QueryLayout()              ; reads the file komorebic wrote
    if (cur = "Scrolling")
        Komo("change-layout " LayoutBeforeScrolling)
    else {
        LayoutBeforeScrolling := StrLower(RegExReplace(cur, "([a-z0-9])([A-Z])", "$1-$2"))
        Komo("scrolling-layout-columns 2")
        Komo("change-layout scrolling")
    }
}
```

The `RegExReplace` turns komorebi's display names (`UltrawideVerticalStack`) back into CLI arguments (`ultrawide-vertical-stack`). The query costs one `cmd /c komorebic query … > temp` round trip, about 30 ms, which is invisible on a keypress.

## Scrolling shows three columns, Omarchy shows two

komorebi's `Scrolling` layout defaults to three visible columns. That is a layout option, not a different layout:

```
komorebic scrolling-layout-columns 2
```

Per workspace at runtime, and permanently through the static config (0.1.41 added `layout_defaults`, keyed by layout name, applied as a fallback when a workspace has no options of its own):

```json
"layout_defaults": {
  "Scrolling": { "layout_options": { "columns": 2 } }
}
```

## The adoption wall

The first hour of "it does not work" was really this: komorebi managed **zero** windows. Not a misconfiguration — the two windows on screen predated the window manager.

komorebi tiles windows that appear while it runs. Windows that existed before it are invisible to it, and there is no API to adopt one:

- `komorebic manage` — "force komorebi to manage the focused window" — acts on *komorebi's* focused window, which for an unmanaged window does not exist. No-op.
- `komorebic force-focus` clicks the window at the cursor to sync that focus, then `manage`. Still nothing.
- Restarting with `--clean-state` re-reads the config and manages nothing.
- Restarting without it restores the previous dump, which contains no such windows.

Proof that it is adoption and not a broken install: a freshly opened Chromium window (`msedge --app=about:blank`) landed in a container within seconds. Same engine, same config, new window.

Practical rule, and the one in the README: **close and reopen anything that was open before you started komorebi.** After a reboot this problem disappears, because komorebi starts at logon before your apps do.

## Floating hides, unmanaged does not

This is the most useful thing learned, and it is not written down anywhere obvious.

A floated window (`Super+T`) still belongs to its workspace, so switching workspaces hides it. An **unmanaged** window is invisible to komorebi, therefore never hidden, therefore present on every workspace — which is exactly what Omarchy's popped window does with `Super+O`.

So the PiP recipe is to make Chrome's picture-in-picture window unmanaged:

```
komorebic ignore-rule title "Picture in picture"
```

Rules apply to windows created after them, so the current PiP has to be closed and reopened. For persistence, the same rule goes into `applications.json` under `Google Chrome`. Chrome's PiP window uses the same class as normal Chrome windows (`Chrome_WidgetWin_1`), so the rule has to match on title, not class.

Verified with a decoy: an empty Notepad renamed to `Picture in picture` was refused by komorebi, while a normally titled one was tiled.

## The tray widget's blind spot

komorebi-bar 0.1.41 added a `Systray` widget. On Windows 11 it cannot read the existing tray — its log says `Retrieved 0 icons from system tray`, because `TrayNotifyWnd` is no longer where that code looks. It falls back to broadcasting `TaskbarCreated`, the message the shell sends to announce a taskbar restart, and collects whatever applications re-register their icons in response.

Consequence: any app that does not handle `TaskbarCreated` will never appear. My own air-quality app never showed, while PowerToys, Everything, Keyman, Windows Security and the keyboard battery widget all did. Run the bar once with `RUST_LOG=info` to see exactly what it receives:

```
Icon modified or added: IconEventData { tooltip: Some("zmk-battery-center"), is_visible: true, ... }
```

## The bar died once

Mid-session, without warning: `komorebi-bar` disappeared. Its log stopped mid-line, there was no panic message, and Windows had no application-error record. The timing matched closing a terminal window, and the newly added systray widget tracks tray-icon owner windows — a window being destroyed is precisely its weak spot. komorebi itself was untouched, still the same PID, still tiling.

Rather than hope, the keymap now supervises it:

```ahk
SetTimer(WatchBar, 15000)
WatchBar() {
    if !ProcessExist("komorebi-bar.exe")
        Run('"' . BAR . '"', , "Hide")
}
```

It has already earned its keep: `bar missing, restarting` appeared in the log and the bar came back without a human.

## Installing without administrator rights

`winget` would install the MSI, which prompts for UAC — useless on an unattended machine, and avoidable. Everything here is user-scope: the release ZIP unpacked into `%LOCALAPPDATA%\Programs`, a portable AutoHotkey zip next to it, two entries in the *user* `PATH`, and two shortcuts in `shell:startup`. The release archive is verified against the published `checksums.txt` first.

The two things that genuinely need admin are left as opt-in: `LongPathsEnabled`, and an elevated scheduled task if you want komorebi to tile windows belonging to administrator apps. Running unelevated means windows of elevated processes stay unmanaged — a small price for a setup that installs itself.

## What I would do differently

- Start with one workspace and one key, verify the model ("does this window move?") before writing 46 bindings.
- Never trust a synthetic keypress to test a hotkey layer. `Send("#1")` never reached the hook; `Send("^!+x")` did. The first made a working binding look broken for twenty minutes.
- Read `komorebic state` before believing anything. It reports what komorebi *thinks*, which is not always what you see; the bar's layout label and `query focused-workspace-layout` were the more reliable pair.
- Keep the hotkey log from the first minute. It converts "this key does nothing" into "Windows ate it" versus "komorebic ignored it".

## Upstream notes

- komorebi's licence allows personal forks and forbids redistribution and commercial use. Nothing here redistributes it: the scripts download the official release.
- A real fix for `Super+digit` in whkd would be swapping its `win-hotkeys` backend for a `WH_KEYBOARD_LL` hook — a few hundred lines, and the only reason the GitHub Actions build route in [the earlier discussion] was ever on the table. AutoHotkey's `#UseHook` makes it unnecessary.
- The bar's systray enumeration is worth an upstream issue: reading `TrayNotifyWnd` returns nothing on current Windows 11.
