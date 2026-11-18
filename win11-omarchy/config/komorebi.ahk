#Requires AutoHotkey v2.0
#SingleInstance Force
#UseHook True
; ===========================================================================
;  win11-omarchy keymap
;  komorebi + AutoHotkey v2, Omarchy's navigation ported to Windows 11
;  Full list of bindings: ../SHORTCUTS.md
; ===========================================================================
;
;  Three rules this file lives by, all learned the hard way:
;
;  1. #UseHook True is load-bearing. Without it AutoHotkey implements hotkeys
;     with RegisterHotKey, which ADDS a handler instead of consuming the key,
;     so Win+1 fires komorebi AND Explorer's taskbar slot.
;     Win+digit, Win+Shift+digit are Explorer's (RegisterHotKey error 1409).
;  2. No Win+Alt+<anything> bindings. The shell and Xbox Game Bar swallow that
;     family before the keyboard hook sees it. Ctrl+Alt is the substitute.
;  3. Run, not RunWait, in the handler: nothing good comes of blocking the
;     hotkey thread for the 200 ms komorebic takes.
;
;  Digit keys stop at 4 because komorebi.json defines four workspaces.
;  Focusing a non-existent index would recreate it and re-clutter the bar.

; ---- point these at your install ------------------------------------------
;  scripts/install.ps1 unpacks komorebi into %LOCALAPPDATA%\Programs\komorebi-<version>
KM     := EnvGet("LOCALAPPDATA") . "\Programs\komorebi-0.1.41"
KC     := KM . "\komorebic.exe"
BAR    := KM . "\komorebi-bar.exe"
ERRLOG := EnvGet("USERPROFILE") . "\.config\komorebi\ahk-errors.log"

Komo(cmd) {
    global KC, ERRLOG
    FileAppend(FormatTime() . "  fire: " . cmd . "`n", ERRLOG)
    try {
        Run('"' . KC . '" ' . cmd, , "Hide")
    } catch as e {
        FileAppend(FormatTime() . "  ERROR " . cmd . "  ->  " . e.Message . "`n", ERRLOG)
    }
}

; ------------------------------------------------------- layout toggle state
; Remember what we were in before going to Scrolling, so the key toggles back
; to it rather than always to BSP.
LayoutBeforeScrolling := "bsp"

QueryLayout() {
    global KC, ERRLOG
    tmp := A_Temp . "\komorebi-layout.txt"
    cmd := A_ComSpec . ' /c ""' . KC . '" query focused-workspace-layout > "' . tmp . '""'
    try {
        RunWait(cmd, , "Hide")
        return Trim(FileRead(tmp))
    } catch as e {
        FileAppend(FormatTime() . "  ERROR query layout  ->  " . e.Message . "`n", ERRLOG)
        return ""
    }
}

ToggleScrolling() {
    global LayoutBeforeScrolling
    cur := QueryLayout()
    if (cur = "") {
        Komo("change-layout scrolling")
        return
    }
    if (cur = "Scrolling") {
        Komo("change-layout " LayoutBeforeScrolling)
    } else {
        ; "UltrawideVerticalStack" -> "ultrawide-vertical-stack", "Bsp" -> "bsp"
        LayoutBeforeScrolling := StrLower(RegExReplace(cur, "([a-z0-9])([A-Z])", "$1-$2"))
        ; Omarchy's scrolling shows two columns, komorebi defaults to three
        Komo("scrolling-layout-columns 2")
        Komo("change-layout scrolling")
    }
}

; ------------------------------------------------- keep the status bar alive
; komorebi-bar has no supervisor and can exit quietly (it did once when a
; terminal window closed - the systray widget tracks tray-icon owner windows).
SetTimer(WatchBar, 15000)

WatchBar() {
    global BAR, ERRLOG
    if !ProcessExist("komorebi-bar.exe") {
        FileAppend(FormatTime() . "  bar missing, restarting`n", ERRLOG)
        try Run('"' . BAR . '"', , "Hide")
    }
}

; ================================================================ workspaces
#1::Komo("focus-workspaces 0")
#2::Komo("focus-workspaces 1")
#3::Komo("focus-workspaces 2")
#4::Komo("focus-workspaces 3")

; Windows-key-free duplicates
!1::Komo("focus-workspaces 0")
!2::Komo("focus-workspaces 1")
!3::Komo("focus-workspaces 2")
!4::Komo("focus-workspaces 3")

; move the focused window there and follow it
#+1::Komo("move-to-workspace 0")
#+2::Komo("move-to-workspace 1")
#+3::Komo("move-to-workspace 2")
#+4::Komo("move-to-workspace 3")
!+1::Komo("move-to-workspace 0")
!+2::Komo("move-to-workspace 1")
!+3::Komo("move-to-workspace 2")
!+4::Komo("move-to-workspace 3")

; move it there and stay put (Omarchy's Super+Shift+Alt+N)
^!+1::Komo("send-to-workspace 0")
^!+2::Komo("send-to-workspace 1")
^!+3::Komo("send-to-workspace 2")
^!+4::Komo("send-to-workspace 3")

#Tab::Komo("cycle-workspace next")
#+Tab::Komo("cycle-workspace previous")
#^Tab::Komo("focus-last-workspace")

; ================================================================ navigation
#Left::Komo("focus left")
#Right::Komo("focus right")
#Up::Komo("focus up")
#Down::Komo("focus down")

#+Left::Komo("move left")
#+Right::Komo("move right")
#+Up::Komo("move up")
#+Down::Komo("move down")

; =================================================================== layouts
#j::Komo("change-layout vertical-stack")   ; Omarchy Super+J: stack them
#+j::Komo("change-layout bsp")             ; and back to side by side
#y::Komo("cycle-layout next")              ; Omarchy Super+L cycles (Win+L is the lock)
#+y::Komo("cycle-layout previous")
^!l::ToggleScrolling()                     ; scrolling <-> the layout you came from
^!b::Komo("change-layout bsp")
^!v::Komo("change-layout vertical-stack")
^!h::Komo("change-layout horizontal-stack")
^!g::Komo("change-layout grid")

; ============================================================ window states
#t::Komo("toggle-float")
#q::Komo("close")
#f::Komo("toggle-monocle")                 ; fullscreen
^!f::Komo("toggle-maximize")               ; full width, bar stays
^!m::Komo("minimize")
^!+f::Send("{F11}")                        ; in-window fullscreen

; ================================================================== stacking
^!+g::Komo("stack-all")                    ; Omarchy Super+G grouping
^!+u::Komo("unstack-all")
^!+Left::Komo("cycle-stack previous")      ; Omarchy Super+Ctrl+Arrow in a group
^!+Right::Komo("cycle-stack next")

; ============================================================ applications
^!Enter::Run("wt.exe")                     ; terminal
^!+Enter::Run("https://www.google.com")    ; browser
#+f::Run("explorer.exe")                   ; files
^!t::Run("taskmgr.exe")                    ; activity monitor
#`::Run("wt.exe -w _quake")                ; quake console

; =========================================================== escape hatches
^!+x::Komo("toggle-pause")
