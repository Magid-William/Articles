# Guide: Integrating a common USB TrackPoint with ZMK

## 1.0.0 Intro

In this article I'm going to showcase how I integrated a Chinese generic USB TrackPoint like this one:

![Generic USB TrackPoint module](https://randalea.de/~db7/assets/trackpoint.png)

With ZMK.

> [!WARNING]
> **Don't buy this module**, unless you already own one and want to reuse it in a wireless build, or you have no other way to source a TrackPoint. it has it's quirks and every now and then will move on it's own, For common TrackPoints with documented pinouts, see [alonswartz's pinout collection](https://github.com/alonswartz/trackpoint/tree/master/pinouts) or [Deskthority's list](https://deskthority.net/wiki/TrackPoint_Hardware).

## Table of Contents

- [1.0.0 Intro](#100-intro)
- [1.1 Features](#11-features)
- [1.2 How it works](#12-how-it-works)
- [1.3 Step 1: Getting the TrackPoint out](#13-step-1-getting-the-trackpoint-out)
- [2.0.0 Step 2: Choosing the approach](#200-step-2-choosing-the-approach)
    - [2.1 Software only](#21-software-only)
        - [2.1.1 Wiring](#211-wiring)
        - [2.1.2 The ZMK side](#212-the-zmk-side)
        - [2.1.3 Power curve](#213-power-curve)
        - [2.1.4 Flashing & verifying](#214-flashing-verifying)
        - [2.1.5 Known issues](#215-known-issues)
        - [2.1.6 Resources](#216-resources)
    - [2.2 Co-processor](#22-co-processor)
        - [2.2.1 Bill of Materials](#221-bill-of-materials)
        - [2.2.2 Arduino Pro Mini](#222-arduino-pro-mini)
        - [2.2.3 ATtiny85](#223-attiny85)
        - [2.2.4 The ZMK side](#224-the-zmk-side)
        - [2.2.5 Known issues](#225-known-issues)
    - [2.3 24-bit ADC (coming soon)](#23-24-bit-adc-coming-soon)
        - [2.3.1 Concept](#231-concept)
        - [2.3.2 Status](#232-status)
        - [2.3.3 Known issues](#233-known-issues)
- [3.0.0 Step 3: Using it](#300-step-3-using-it)
    - [3.1 My dev workflow](#31-my-dev-workflow)
- [3.2 Other Resources and Special Thanks](#32-other-resources-and-special-thanks)

## 1.1 Features

- **Mouse movement**, similar to the `layer-toggle` from `infused-kim`: by interacting with the TrackPoint you automatically switch to the `tp_layer` layer (where the mouse keys live), and after ~2 s of inactivity you automatically return to the default layer.
- **Scrolling**, hold a key to switch to the `scroll_layer` and scroll vertically and horizontally with the nub. For me it's `J` on Colemak-DH (you'd probably use `Y` on QWERTY).
- **Volume control**, same idea: hold `K` and use the nub to control the volume.
- **Deep sleep**, native to ZMK; I encourage it as it saves battery. Personally I set it to 15 minutes.
- **Power curve**, for controlling the smoothness of the mouse movement (I prefer it).

## 1.2 How it works

The TrackPoint natively speaks PS/2, which the nRF52840 is not friendly with (and it would drain battery decoding it). There are three ways to get around that, from simplest to most involved:

- **Software only** — run the PS/2 decoder directly on the nice_nano. The trackpoint is wired straight to the MCU and decoded on the same chip running ZMK. Simplest, no extra hardware.
- **A co-processor** — a small AVR (Arduino Pro Mini or ATtiny85) reads the TrackPoint over PS/2 and exposes the data over I2C to ZMK. The approach I'd already documented on this page.
- **A 24-bit ADC** — read the TrackPoint's analog output directly with a high-resolution ADC, bypassing the digital PS/2 stream entirely (coming soon).

All three power the same ZMK features above. Pick your approach below.

## 1.3 Step 1: Getting the TrackPoint out

Regardless of approach, you first need to free the TrackPoint sensor from its USB housing.

The USB TrackPoint consists of 2 parts:

- The TrackPoint sensor (the smaller PCB)
- A housing PCB that exposes the TrackPoint as USB

We only need the TrackPoint sensor, so we'll de-solder it.

> [!WARNING]
> I personally had 2 of these TrackPoints, and both times I ended up damaging 2–3 pins. I eventually recovered them, but this is a very delicate process. Don't do it if you're excited (I know I was).

<img width="118" alt="De-soldered TrackPoint sensor" src="https://github.com/user-attachments/assets/06aeb2fb-bc92-417d-a4c3-1ac51326be38" />

To de-solder it safely, cover the pins with flux and extra solder and use at least `250 °C` on the iron. By covering the pins you thermally interface with all of them at once.

One pin that seemed tricky was the `GND` pin, the leftmost one. It seems to be soldered with a different solder material than the rest, and I'm not sure why. I'm guessing more temperature helps, maybe even more flux.

Here's the pin mapping:

<img width="300" alt="ThinkPad T420 TrackPoint pinout" src="https://github.com/user-attachments/assets/3a3dddd8-4f6e-426e-8266-05f6c4a9d94b" />

> [Source](https://deskthority.net/wiki/TrackPoint_Hardware)

From left to right:

| Pin | Note |
| --- | ---- |
| GND |      |
| CLK |      |
| DAT |      |
| RST | Not connected to anything, ignore it |
| VCC |      |
| M1  |      |
| M3  |      |
| M2  |      |

---

## 2.0.0 Step 2: Choosing the approach

| | **A: Software only** | **B: Co-processor** | **C: 24-bit ADC** |
|---|---|---|---|
| **Complexity** | Lowest — just firmware | Medium — extra chip + wiring | Highest — analog conditioning |
| **Extra hardware** | None | AVR (Pro Mini or ATtiny85) + sockets/programmer | ADC (TBD) |
| **Power** | Best (no extra MCU) | 2nd (AVR draws mA) | TBD |
| **Drift** | Intermittent ~1 s, shared since it's the PS/2 decode path | Same as A | Expected: none (no PS/2 decode) |
| **Status** | Shipping (Exp68–75) | Shipping | Under development |

My take: if you have a nice_nano with two free GPIOs, **Software only** is the easiest path to a working nub. **Co-processor** is the way to go if your board can't spare the pins alongside split/BLE duties, or you want the smallest, lowest-power sensor at the point of the nub. **24-bit ADC** is experimental and the one I'm most excited about, because it should finally kill the drift.

Each approach below has its own wiring, flashing, ZMK steps, and known issues.

### 2.1 Software only

The simplest approach: wire the TrackPoint's PS/2 lines directly to the nice_nano and decode them right on the chip running ZMK, no co-processor.

This uses the [`zmk-ps2-trackpoint-driver`](https://github.com/Magid-William/zmk-ps2-trackpoint-driver) (a fork of `badjeff`'s PS/2 driver) plus the [`zmk-config-ps2-test`](https://github.com/Magid-William/zmk-config-ps2-test) bench config.

#### 2.1.1 Wiring

This particular TrackPoint streams 3-byte PS/2 packets on power-up and **rejects every host command**, so the driver runs in a *never-send-commands* mode and just listens. Wire it directly to the nice_nano:

| TrackPoint | Nice!Nano | Note |
| ---------- | --------- | ---- |
| CLK | P0.06 | Via internal pull-up on the driver (GPIO backend) |
| DAT | P0.08 | Via internal pull-up on the driver (GPIO backend) |
| VCC | VCC (EXT_POWER P0.13 rail) | So deep sleep cuts the TrackPoint's power too |
| GND | GND | |
| RST | - | Leave float |

> **Why the `gpio-ps2` backend?** This TrackPoint has a jittery RC clock. The driver's other backend (`uart-ps2`) samples at a fixed rate and can't follow it, producing decode glitches. The `gpio-ps2` backend samples DAT on real CLK falling edges — the same mechanism the AVR decoder used — and is jitter-immune.

#### 2.1.2 The ZMK side

Point ZMK's `west.yml` at the two repos above, enable the direct-PS/2 options in your board config, and add the device node:

```ini
# board.conf
CONFIG_ZMK_EXT_POWER=y
CONFIG_INPUT_MOUSE_PS2_NO_HOST_COMMANDS=y     # this TP rejects all host commands
CONFIG_PS2_GPIO_NO_RESEND=y                   # suppress 0xFE resend writes
CONFIG_INPUT_THREAD_STACK_SIZE=4096           # stable split-role builds (see known issues)
```

The driver's README has the full reference. The key flags for this module, all opt-in (Exp75 made them default = stock):

| Option | What it does for this TrackPoint |
|--------|----------------------------|
| `NO_HOST_COMMANDS` | skip the handshake self-test/reset/config; just listen to the power-up stream (int8 decode) |
| `PS2_GPIO_NO_RESEND` | never write `0xFE` resends to a command-rejecting TP |
| `PS2_GPIO_TIMING_SCL_CYCLE_MAX` | tolerate the TP's clock pausing mid-byte (`8000` works) |
| pull-ups (GPIO/UART) | the PS/2 lines need pull-ups (patched into the driver) |
| `POWER_CURVE` | on-device Smoothness curve, see below |

Also note the **axis are rotated** vs a normal keycap — push up reports as left. Fix it in ZMK config (not the driver) with a swap-only transform (`zmk,input-processor-transform`, `INPUT_TRANSFORM_XY_SWAP`).

#### 2.1.3 Power curve

The on-device Power curve gives the same "slow nudge crawls, fast flick accelerates" feel it previously had on the co-processor — now baked straight into the driver. Start with the verified tuning:

```dts
tpoint0 {
    curve-sens = <128>;      /* 0.5x  — loudness */
    curve-rate = <18>;       /* 0.070 — curve shape */
    curve-exponent = <256>;  /* 1.0 */
    curve-start = <77>;      /* 0.30  — slow-speed precision */
};
```

#### 2.1.4 Flashing & verifying

Build via GitHub Actions using `zmk-config-ps2-test` as a starting point, then flash the firmware to the nice_nano (see `AGENTS.md` in the knowledge repo for the headless bootloader entry + USB-logging recipe). Touch the nub and the cursor should move in all four directions naturally.

#### 2.1.5 Known issues

The cursor occasionally drifts in a random direction for about a second, then returns to normal. It happens roughly once a day, and I haven't found the cause yet. This is the **same underlying issue as the Co-processor** (2.2) — it lives in the digital PS/2 decode path, not in any one implementation. Since both solutions share it, the details live here and 2.2 references them.

Steps for repro:
- Let's say you are scrolling down slowly, keep scrolling for a good 5 minutes.
- During the 5 minutes you will sense resistance.
- lift your finger, and notice the mouse moving in a direction for 1sec or less then stops.

These also point to possible causes:
- [Maybe it's the heat](https://forums.tomsguide.com/threads/my-cursor-is-drifting-across-the-screen-again-and-sometimes-becomes-completely-unresponsive.352134/?order=vote_score), in my +38c weather vs on an AC set to 26c, there is merits to this.
- [UHK had the same issue](https://github.com/UltimateHackingKeyboard/firmware/issues/382) worth studying.

#### 2.1.6 Resources

- [Driver: `zmk-ps2-trackpoint-driver`](https://github.com/Magid-William/zmk-ps2-trackpoint-driver)
- [Config: `zmk-config-ps2-test`](https://github.com/Magid-William/zmk-config-ps2-test)

### 2.2 Co-processor

The approach I originally documented on this page: a small AVR sits between the TrackPoint and ZMK.

- The co-processor reads X/Y movement from the TrackPoint over PS/2.
- It exposes the data as an I2C slave at address `0x42`.
- ZMK's [`trackpoint-i2c` driver](https://github.com/Magid-William/attiny85-trackpoint) reads that I2C slave, triggered by the MOT data-ready line, not blind polling, and feeds the pointer into ZMK.

Wire either an [Arduino Pro Mini](#222-arduino-pro-mini) or an [ATtiny85](#223-attiny85) as the co-processor.

#### 2.2.1 Bill of Materials

| Component                          | Quantity | Note                                                                                  |
| ---------------------------------- | -------- | ------------------------------------------------------------------------------------- |
| Generic USB TrackPoint             | 1        |                                                                                       |
| ATtiny85                           | 1        | Don't get the dev board version, it might consume more power                           |
| 8-pin IC socket (4+4 pin)          | 2        | You need at least 2, as you'll move the ATtiny between boards (programmer and keyboard) |
| Arduino Uno                        | 1        | For programming the ATtiny85; I personally used an **Arduino Leonardo**                |
| 1K ohm resistor                    | 1        | Only for the RST pin, if you want to use it (I don't)                                  |
| 4.7K ohm resistor                  | 2        | For the I2C pullups                                                                   |
| 100nF capacitor                    | 1        |                                                                                       |

Tools:

- Dotted breadboard (a breadboard with copper dots, not lines)
- Wire
- Solder
- Solder iron
- Multimeter
- Tweezers
- Optional: an extra nRF52 board dedicated to testing
- An LLM coding agent, if you need more features

#### 2.2.2 Arduino Pro Mini

I had an Arduino Pro Mini lying around that I'd never used and wasn't sure why I bought. It ended up being a really good fit, but not right away: the Pro Mini has 2 things that consume power in idle:

- The power regulator (in red)
- The LED (in orange)

<img width="324" alt="Pro Mini: power regulator and LED highlighted" src="https://github.com/user-attachments/assets/e335690b-8658-4126-82c5-9f5a59557286" />

De-solder them and you get a very solid co-processor (it's okay to break the led with a plier). 
I used the Pro Mini for a week and it + the TrackPoint consumed about 3–4% per day on a 1050 mAh battery (BL-5B Nokia replacement battery) compared to 1% per day for the left side with the same battery.

Here's a diagram:

<img width="2203" alt="Wiring diagram: TrackPoint, Pro Mini, Nice!Nano" src="https://github.com/user-attachments/assets/352e6fcd-f611-4064-8c86-8c77cc49735f" />


| TrackPoint | Pro Mini | Nice!Nano clone | Note                  |
| ---------- | -------- | --------------- | --------------------- |
| CLK        | D7       | -               |                       |
| DAT        | D3       | -               |                       |
| -          | A4       | P0.17           | Via 4.7K ohm resistor, connected to VCC |
| -          | A5       | P0.20           | Via 4.7K ohm resistor, connected to VCC |

##### 2.2.2.1 Flashing the Pro Mini

You can flash the Pro Mini using another Arduino (Arduino ISP or USB passthrough). Honestly, this is where you'll want to consult your favorite LLM.

For me it was a dedicated `CH340G` AVR programmer (which won't work with the ATtiny85), and it flashed the Pro Mini with no issues. Here's an example of the connection:

| Pro Mini | CH340G |
| -------- | ------ |
| TX       | RX     |
| RX       | TX     |
| GND      | GND    |
| VCC      | VCC    |

##### 2.2.2.2 Resources (Pro Mini)

- [Pro Mini sketch](https://github.com/Magid-William/promini-trackpoint/blob/master/trackpoint-i2c-slave/trackpoint-i2c-slave.ino) for reading PS/2 from the TrackPoint and interfacing over I2C
- [Prebuilt hex](https://github.com/Magid-William/promini-trackpoint/releases/tag/Exp60) you can flash directly to the Pro Mini

#### 2.2.3 ATtiny85

I thought the Pro Mini consumed too much power, so I asked an LLM and it suggested an ATtiny. I was able to source an ATtiny85 locally.

Honestly, the ATtiny85 felt like a downgrade and I'd stick with the Pro Mini if I had to choose all over again. But if you prefer it, or have a form factor more like the ATtiny85, follow along.

##### 2.2.3.1 Why I'd pick the Pro Mini over the ATtiny85

The ATtiny85 works, but it's tight on every axis:

**Where the ATtiny85 wins:** size (DIP-8 fits anywhere) and power (~0.5 mA vs ~2–4 mA active), though the trackpoint dominates the budget either way.

Bottom line: footprint/battery → ATtiny85; headroom, debugging, flashing → Pro Mini.

Here's the diagram again:

<img width="2392" alt="Wiring diagram: TrackPoint, ATtiny85, Nice!Nano" src="https://github.com/user-attachments/assets/6e15e552-2714-4715-9216-7201326e7f31" />

| TrackPoint | ATtiny85 physical pins | Nice!Nano clone | Note                  |
| ---------- | -------- | --------------- | --------------------- |
| -          | 1        | -               | Leave RST float       |
| CLK        | 2        | -               |                       |
| DAT        | 3        | -               |                       |
| GND        | 4        | GND             |                       |
| -          | 5        | P0.17           | Via 4.7K ohm resistor, connected to VCC |
| -          | 6        | P0.06           | MOT                   |
| -          | 7        | P0.20           | Via 4.7K ohm resistor, connected to VCC |
| VCC        | 8        | VCC             |                       |
| -          | 4 -> 8   | -               | Via 100nF capacitor   |

The ATtiny85 setup differs from the Pro Mini in that it needs a `MOT` line. That's better than blind 10 ms polling, the `MOT` line made a huge difference to the smoothness of the ATtiny85's readings.

##### 2.2.3.2 Flashing the ATtiny85

This is where another Arduino comes in, not the dedicated `CH340G`j like an Arduino Uno or the Leonardo I used, to flash the ATtiny. The wiring should be identical between them (I only tested with the Leonardo): typically you connect pins from the `ICSP` header to the ATtiny.

From the Arduino IDE, before connecting the ATtiny, flash an Arduino ISP sketch to the Uno/Leonardo, you'll find it in the Examples menu of the Arduino IDE.

This is why the two 8-pin IC sockets (4+4 pin) matter: you move the ATtiny between the programmer and the Nice!Nano keyboard for interfacing.

<img width="500" alt="Arduino Uno ICSP pinout for ISP flashing" src="https://github.com/user-attachments/assets/6f10453f-b3d9-4d23-b00d-0fb82c1d7bb7" />

| Uno/Leonardo      | ATtiny85 Pin | Function    |
|-------------------|--------------|-------------|
| Digital Pin 10    | Pin 1        | RESET (PB5) |
| ICSP Pin 6 (GND)  | Pin 4        | GND         |
| ICSP Pin 4 (MOSI) | Pin 5        | PB0         |
| ICSP Pin 1 (MISO) | Pin 6        | PB1         |
| ICSP Pin 3 (SCK)  | Pin 7        | PB2         |
| ICSP Pin 2 (5V)   | Pin 8        | VCC         |

Here's a closer look at the PCB:

<img width="500" alt="ATtiny85 co-processor PCB close-up" src="https://github.com/user-attachments/assets/6a731176-9168-46b1-b146-4c34443a1b36" />

<details>

<summary>More images</summary>

<img width="500" alt="ATtiny85 build photo" src="https://github.com/user-attachments/assets/a9bf8494-f7bb-4df0-a4b7-265fede32249" />

<img width="500" alt="ATtiny85 build photo" src="https://github.com/user-attachments/assets/7f64b1bc-6f19-4976-9b83-ddfc1ad8cc03" />

<img width="500" alt="ATtiny85 build photo" src="https://github.com/user-attachments/assets/7b9b5acc-8f1f-4fff-9adc-ecee06d5c1e7" />

</details>

##### 2.2.3.3 Resources (ATtiny85)

- [The ATtiny85 sketch](https://github.com/Magid-William/attiny85-trackpoint/blob/main/trackpoint-i2c-slave-attiny85/trackpoint-i2c-slave-attiny85.ino) for reading PS/2 from the TrackPoint and interfacing over I2C
- [Prebuilt hex](https://github.com/Magid-William/attiny85-trackpoint/releases/tag/EXP64) ready to be flashed

#### 2.2.4 The ZMK side

- [Here's the driver](https://github.com/Magid-William/zmk-trackpoint-driver), it holds the integration instructions.
- [Shield example](https://github.com/Magid-William/zmk-trackpoint-shield)
- [My personal shield](https://github.com/Magid-William/zmk-config-dabaseV_0-2), which uses a dongle

#### 2.2.5 Known issues

The cursor occasionally drifts in a random direction for about a second, then returns to normal — the **same shared issue as Software only** (2.1). See [2.1.5's Known issues](#215-known-issues) for reproduction steps and suspected causes.

---

### 2.3 24-bit ADC (coming soon)

> [!NOTE]
> This solution is under development — the content below is a preview of the direction, not a finished guide.

#### 2.3.1 Concept

Instead of decoding the TrackPoint's digital PS/2 stream (where the drift lives), read its analog output directly with a **24-bit ADC**. Because there's no PS/2 clock sampling and no byte/baseline decode to glitch, this has the **potential to eliminate the drift entirely** — the one open issue that Software only and the Co-processor still share.

#### 2.3.2 Status

Under development. Wiring, parts, and the ZMK integration are being worked out and will be added here.

#### 2.3.3 Known issues

Expected: none of the PS/2 drift. Open items will be listed here as they're discovered.

---

## 3.0.0 Step 3: Using it

<img width="1600" alt="The finished keyboard with the TrackPoint" src="https://github.com/user-attachments/assets/405c1641-c9d2-41ea-a336-00711cb01071" />

I found a random screwdriver cap works great as a "rim cap": I used baking powder and super glue to fill the gap so I could attach it to the TrackPoint. No cracks so far, and it turned out fine.

And that's it, flash the firmware, pair the keyboard, and the nub now drives your cursor.

### 3.1 My dev workflow

<details>

<summary>
	The following is an agentic coding workflow, for inspiration only.
</summary>

I used an LLM coding agent for everything software in this project; this is my first project using OpenCode with DeepSeek V4 flash.

Basically I define every feature/problem/reproduction/bugfix as an experiment, starting with:

```
Read @Experiments.md
```

It reads the compact `Experiments.md` and says it's ready to work on X. I ignore the suggestion and say:

```
In this experiment I want to do Y, and only focus on Y so I could prove that Y is better than X, blah blah blah.
Ask me questions before the final plan
```

It then gives me a plan or asks me clarifying questions.

After I approve the plan, it creates an `.md` file for the experiment with the plan, hypothesis, method, and a conclusion that gets updated later.

I made sure to make it clear in the `AGENTS.md` that I prefer a closed loop, where the agent:

- Makes changes
- Commits them
- Waits until the GitHub Action finishes, iterating if it failed
- Programmatically enters the bootloader without you physically pressing reset twice
- Flashes the new firmware
- Opens the serial monitor and reads the logs to confirm its changes are reflected

For example, instead of asking if the TrackPoint works by moving it physically, ask it to create a synthetic movement on the Pro Mini side, this way you don't have to touch the TrackPoint.

When you're happy with the result, ask it:

```
conclude this experiment
```

It writes the conclusion in the experiment's dedicated `.md` file, updates `Experiments.md`, and commits any uncommitted changes.

Although I now think this last part needs more refining, like including the scripts that worked for it, since some models keep retrying many scripts to flash the Pro Mini where they didn't before. Ugh, such is LLM coding life.

But that's basically it: I start an experiment, then 5 hours later (could be 5 minutes, could be 10, could be 15, it depends) if I got what I want I conclude it. If I got nowhere, I say something like:

```
Erase this Experiment completely, locally and from Github
```

I did this only 3–4 times, unless there was something important, going SPI was important but proved to be a pain, so I simply called it failed, so it learns from it and doesn't waste time re-exploring failed paths.

It only took 60 experiments over about 2 months 🫥, but hey, we're here and I'm using it right now. Yay!! 🎊

[Here's the repo with the AGENTS.md and all](https://github.com/Magid-William/trackpoint-knowledge)

</details>

## 3.2 Other Resources and Special Thanks

- [@db7](https://github.com/db7)
	- [Cheap and Dirty Logic Analyzer with Teensy](https://randalea.de/~db7/teensy-logic-analyzer.html)
	- [Crunching a PS/2 Mouse Decoder](https://randalea.de/~db7/crunch-ps2-decoder.html)

- [@alonswartz](https://github.com/alonswartz)
	- [Guide: How to integrate a TrackPoint in a mechanical keyboard](https://github.com/alonswartz/TrackPoint)
	- [Common TrackPoint pinouts](https://github.com/alonswartz/trackpoint/tree/master/pinouts)

- [@infused-kim](https://github.com/infused-kim)
	- [kb_zmk_ps2_mouse_TrackPoint_driver](https://github.com/infused-kim/kb_zmk_ps2_mouse_TrackPoint_driver)
	- [kb_zmk_ps2_mouse_TrackPoint_driver-zmk_config](https://github.com/infused-kim/kb_zmk_ps2_mouse_TrackPoint_driver-zmk_config)

- [@Ahmed-M-Osman1](https://github.com/Ahmed-M-Osman1)
	- [His i2c trackpad example](https://github.com/Ahmed-M-Osman1/zmk-driver-azoteq)

- [@badjeff](https://github.com/badjeff)
	- [All of his GitHub repos were valuable](https://github.com/badjeff)