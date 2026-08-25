# Guide: Integrating common USB TrackPoint with ZMK using a coprocessor

## Intro

In this article I'm going to showcase how I integrated a Chinese generic USB TrackPoint like this one:

![Generic USB TrackPoint module](https://randalea.de/~db7/assets/trackpoint.png)

With ZMK, using a co-processor.

> [!WARNING]
> **Don't buy this module** — unless you already own one and want to reuse it in a wireless build, or you have no other way to source a TrackPoint. it has it's quirks and every now and then will move on it's own, For common TrackPoints with documented pinouts, see [alonswartz's pinout collection](https://github.com/alonswartz/trackpoint/tree/master/pinouts).

## Features

- **Mouse movement** — similar to the `layer-toggle` from `infused-kim`: by interacting with the TrackPoint you automatically switch to the `tp_layer` layer (where the mouse keys live), and after ~2 s of inactivity you automatically return to the default layer.
- **Scrolling** — hold a key to switch to the `scroll_layer` and scroll vertically and horizontally with the nub. For me it's `J` on Colemak-DH (you'd probably use `Y` on QWERTY).
- **Volume control** — same idea: hold `K` and use the nub to control the volume.
- **Deep sleep** — native to ZMK; I encourage it as it saves battery. Personally I set it to 15 minutes.
- **Power curve** — for controlling the smoothness of the mouse movement (I prefer it).

## Known issues

> [!CAUTION]
> Occasionally the cursor drifts in a random direction for about 1 second, then returns to normal. It happens roughly once a day, and I haven't found the cause yet.

Steps for repro:
- Let's say you are scrolling down slowly, keep scrolling for a good 5 minutes.
- During the 5 minutes you will sense resistance.
- lift your finger, and notice the mouse moving in a direction for 1sec or less then stops.

After some googling, i saw many people having the same drift issue, here's the most notable:
- [Maybe it's the heat](https://forums.tomsguide.com/threads/my-cursor-is-drifting-across-the-screen-again-and-sometimes-becomes-completely-unresponsive.352134/?order=vote_score), in my +38c weather vs on an AC set to 26c, there is merits to this.
- [UHK had the same issue](https://github.com/UltimateHackingKeyboard/firmware/issues/382) worth studying.

## How it works

The TrackPoint natively speaks PS/2, which the nRF52840 is not friendly with (and it would drain battery decoding it). So a small AVR co-processor sits in between:

- The co-processor reads X/Y movement from the TrackPoint over PS/2.
- It exposes the data as an I2C slave at address `0x42`.
- ZMK's [`trackpoint-i2c` driver](https://github.com/Magid-William/attiny85-trackpoint) reads that I2C slave — triggered by the MOT data-ready line, not blind polling — and feeds the pointer into ZMK.

This article walks through de-soldering the TrackPoint, wiring either an [Arduino Pro Mini](#option-a-arduino-pro-mini) or an [ATtiny85](#option-b-attiny85) as the co-processor, and getting it working in ZMK.

## Table of Contents

- [Intro](#intro)
- [Features](#features)
- [Known issues](#known-issues)
- [How it works](#how-it-works)
- [Bill of Materials](#bill-of-materials)
- [Step 1: Getting the TrackPoint out](#step-1-getting-the-trackpoint-out)
- [Step 2: Choosing a co-processor](#step-2-choosing-a-co-processor)
    - [Option A: Arduino Pro Mini](#option-a-arduino-pro-mini)
        - [Flashing the Pro Mini](#flashing-the-pro-mini)
        - [Resources (Pro Mini)](#resources-pro-mini)
    - [Option B: ATtiny85](#option-b-attiny85)
        - [Flashing the ATtiny85](#flashing-the-attiny85)
        - [Resources (ATtiny85)](#resources-attiny85)
- [Step 3: The ZMK side](#step-3-the-zmk-side)
    - [My dev workflow](#my-dev-workflow)
- [Step 4: Using it](#step-4-using-it)
- [Other Resources and Special Thanks](#other-resources-and-special-thanks)

## Bill of Materials

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

## Step 1: Getting the TrackPoint out

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

## Step 2: Choosing a co-processor

### Option A: Arduino Pro Mini

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

#### Flashing the Pro Mini

You can flash the Pro Mini using another Arduino (Arduino ISP or USB passthrough). Honestly, this is where you'll want to consult your favorite LLM.

For me it was a dedicated `CH340G` AVR programmer (which won't work with the ATtiny85), and it flashed the Pro Mini with no issues. Here's an example of the connection:

| Pro Mini | CH340G |
| -------- | ------ |
| TX       | RX     |
| RX       | TX     |
| GND      | GND    |
| VCC      | VCC    |

#### Resources (Pro Mini)

- [Pro Mini sketch](https://github.com/Magid-William/promini-trackpoint/blob/master/trackpoint-i2c-slave/trackpoint-i2c-slave.ino) for reading PS/2 from the TrackPoint and interfacing over I2C
- [Prebuilt hex](https://github.com/Magid-William/promini-trackpoint/releases/tag/Exp60) you can flash directly to the Pro Mini

### Option B: ATtiny85

I thought the Pro Mini consumed too much power, so I asked an LLM and it suggested an ATtiny. I was able to source an ATtiny85 locally.

Honestly, the ATtiny85 felt like a downgrade and I'd stick with the Pro Mini if I had to choose all over again. But if you prefer it, or have a form factor more like the ATtiny85, follow along.

### Why I'd pick the Pro Mini over the ATtiny85

The ATtiny85 works, but it's tight on every axis:

**Where the ATtiny85 wins:** size (DIP-8 fits anywhere) and power (~0.5 mA vs ~2–4 mA active) — though the trackpoint dominates the budget either way.

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

The ATtiny85 setup differs from the Pro Mini in that it needs a `MOT` line. That's better than blind 10 ms polling — the `MOT` line made a huge difference to the smoothness of the ATtiny85's readings.

#### Flashing the ATtiny85

This is where another Arduino comes in — not the dedicated `CH340G` — like an Arduino Uno or the Leonardo I used, to flash the ATtiny. The wiring should be identical between them (I only tested with the Leonardo): typically you connect pins from the `ICSP` header to the ATtiny.

From the Arduino IDE, before connecting the ATtiny, flash an Arduino ISP sketch to the Uno/Leonardo — you'll find it in the Examples menu of the Arduino IDE.

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

#### Resources (ATtiny85)

- [The ATtiny85 sketch](https://github.com/Magid-William/attiny85-trackpoint/blob/main/trackpoint-i2c-slave-attiny85/trackpoint-i2c-slave-attiny85.ino) for reading PS/2 from the TrackPoint and interfacing over I2C
- [Prebuilt hex](https://github.com/Magid-William/attiny85-trackpoint/releases/tag/EXP64) ready to be flashed

## Step 3: The ZMK side

- [Here's the driver](https://github.com/Magid-William/zmk-trackpoint-driver) — it holds the integration instructions.
- [Shield example](https://github.com/Magid-William/zmk-trackpoint-shield)
- [My personal shield](https://github.com/Magid-William/zmk-config-dabaseV_0-2), which uses a dongle

### My dev workflow

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

After I approve the plan, it creates an `.md` file for the experiment with the plan — hypothesis, method, and a conclusion that gets updated later.

I made sure to make it clear in the `AGENTS.md` that I prefer a closed loop, where the agent:

- Makes changes
- Commits them
- Waits until the GitHub Action finishes, iterating if it failed
- Programmatically enters the bootloader without you physically pressing reset twice
- Flashes the new firmware
- Opens the serial monitor and reads the logs to confirm its changes are reflected

For example, instead of asking if the TrackPoint works by moving it physically, ask it to create a synthetic movement on the Pro Mini side — this way you don't have to touch the TrackPoint.

When you're happy with the result, ask it:

```
conclude this experiment
```

It writes the conclusion in the experiment's dedicated `.md` file, updates `Experiments.md`, and commits any uncommitted changes.

Although I now think this last part needs more refining — like including the scripts that worked for it, since some models keep retrying many scripts to flash the Pro Mini where they didn't before. Ugh, such is LLM coding life.

But that's basically it: I start an experiment, then 5 hours later (could be 5 minutes, could be 10, could be 15 — it depends) if I got what I want I conclude it. If I got nowhere, I say something like:

```
Erase this Experiment completely, locally and from Github
```

I did this only 3–4 times, unless there was something important — going SPI was important but proved to be a pain, so I simply called it failed, so it learns from it and doesn't waste time re-exploring failed paths.

It only took 60 experiments over about 2 months 🫥, but hey, we're here and I'm using it right now. Yay!! 🎊

[Here's the repo with the AGENTS.md and all](https://github.com/Magid-William/trackpoint-knowledge)

</details>

## Step 4: Using it

<img width="1600" alt="The finished keyboard with the TrackPoint" src="https://github.com/user-attachments/assets/405c1641-c9d2-41ea-a336-00711cb01071" />

I found a random screwdriver cap works great as a "rim cap": I used baking powder and super glue to fill the gap so I could attach it to the TrackPoint. No cracks so far, and it turned out fine.

And that's it — flash the firmware, pair the keyboard, and the nub now drives your cursor.

## Other Resources and Special Thanks

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
