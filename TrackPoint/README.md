```
hello world;
```
# Intro
In this article I'm going to showcase how i integrated a Chinese generic USB TrackPoint like this one:

![https://randalea.de/~db7/assets/trackpoint.png](https://randalea.de/~db7/assets/trackpoint.png)

With ZMK using a co-processor.

## Features

- Mouse movement, similar to `layer-toggle` the from `infusidkim`, by interacting with the TrackPoint, you automatically switch to the `tp_layer` layer, where the mouse keys are present, and after ex: 500ms you automatically go back to default layer.
- Scrolling, by holding a button with `&lt 5 J` (<key>J</key> for Colemak-DH, you may want to use <key>Y</key> if on QWERTY) we move to the `scroll_layer` you'd be able to scroll vertically and horizontally using the TrackPoint.
- Volume control, same as the scrolling i simply hold k and use the nub to control the volume.
- Deep sleep, this is native to ZMK, i simply encourage it as it will save on battery life, personally i make it 15 minutes.
- Power curve for controlling the mouse movement (personally i prefer it).


My current setup uses an ATtiny85, but i also used Arduino Pro Mini 8Mhz 3.3V and it was as good.

Using the ATtiny85 this is the wiring:

![](./Attiny-trackpoint.png)

## Bill of materials

| Component               | Quantity | Note                                                              |
| ----------------------- | -------- | ----------------------------------------------------------------- |
| This generic TrackPoint | 1        |                                                                   |
| ATtiny85                | 1        | Don't get the dev board version it might consume more power       |
| 8 Pin IC Base IC Socket 4+4 Pin | 2 | you need at least 2 as you will move the ATtiny from one board to flash to another |
| Arduino Uno             | 1        | For programming the ATtiny85, i personally used **Arduino Leonardo**  |
| 1K ohm resistor         | 1        | Only for the RST pin if you want to use it (i don't)              |
| 4.7K ohm resistor       | 2        | For the I2C pullup                                                |
| 100nf capacitor         | 1        |                                                                   |

Tools:
- Dotted breadboard (a breadboard with copper dots not lines)
- Wire
- Solder
- Solder iron
- Multimeter
- Tweezers
- Optional: Extra nrf52 board dedicated for testing
- LLM coding agent if you need more features

# The process

# Step 1: Getting the TrackPoint out

The USB TrackPoint consists of 2 parts:
- The TrackPoint sensor (the smaller PCB)
- A housing PCB that exposes the TrackPoint as a USB.

We only need the TrackPoint sensor here, to do so we'll need to de-solder it.

> Warning: I personally had 2 of these TrackPoints, and in both times i ended up flocking 2~3 pins, i eventually recovered them, but this is a very delicate process, don't do them if you were exited for example (i know i was).

<img width="118" height="333" alt="image" src="https://github.com/user-attachments/assets/06aeb2fb-bc92-417d-a4c3-1ac51326be38" />

In order to de-solder it safely, cover the pins with flux and extra solder and use at least 250C for the solder iron temp, by covering them you would be thermally interfacing with all the pins at once.

One pin that seemed tricky was the GND pin, it's the left most pin, it's somehow soldered using a different solder material than the other pins, it was so tricky and I'm not sure why it's the case, but I'm guessing more temp is better, may be even flux.

The following is the pin mapping:

<img width="300" height="282" alt="600px-T420_pinout" src="https://github.com/user-attachments/assets/3a3dddd8-4f6e-426e-8266-05f6c4a9d94b" />

From left to right, the following is the pin mapping table:

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

# Step 2: choosing the co-processing

## Option A: Arduino Pro Mini:

I had an Arduino Pro Mini laying around, i never used it before, not sure why i have bought it in the first place.
It ended up being a really good fit, but not right away, the Pro Mini had 2 things that consumes power in idle:
- The Power regulator (in red)
- The LED (in orange)

<img width="324" height="603" alt="image" src="https://github.com/user-attachments/assets/e335690b-8658-4126-82c5-9f5a59557286" />

By de-soldering them you'll get a very solid choice for a co-processor.
I did use the Pro Mini for a week and it + the TrackPoint used to consume like 3~4% a day on a 1050mha battery (BL-5B Nokia replacement battery).

Here's a diagram:

<img width="1991" height="789" alt="image" src="https://github.com/user-attachments/assets/f4d626fe-8d12-42b0-a0d6-f5bd54fffdf7" />

| TrackPoint | Pro Mini | Nice!Nano clone | Note                  |
| ---------- | -------- | --------------- | --------------------- |
| CLK        | D7       | -               |                       |
| DAT        | D2       | -               |                       |
| -          | A4       | P0.17           | Via 4.7k ohm resistor |
| -          | A5       | P0.20           | Via 4.7k ohm resistor |

### Flashing the Pro Mini

Using another Arduino, you can flash the Pro Mini, either using Arduino ISP, or via USB passthrough.
Honestly this is where you'll need to consult with your favorite LLM.

For me it was a dedicated CH340G AVR programmer (wont work with ATtiny85), it worked fine with no issues flashing the Pro Mini.
Here's an example of the connection:

| Pro Mini | CH340G |
| -------- | ------ |
| TX       | RX     |
| RX       | TX     |
| GND      | GND    |
| VCC      | VCC    |

### Resources

- [Pro Mini sketch](https://github.com/Magid-William/promini-trackpoint/blob/master/trackpoint-i2c-slave/trackpoint-i2c-slave.ino) for reading the PS/2 from the TrackPoint and interfacing using I2C 
- [Pre-build hex](https://github.com/Magid-William/promini-trackpoint/releases/tag/Exp60) that you could use them to flash the Pro Mini

## Option B: ATtiny85

I thought the Pro Mini consuming more power, So i asked an LLM and it suggested an ATtiny, i was able to source ATtiny85 locally.

Honestly the ATtiny85 felt like a downgrade, I'd stick with the Pro Mini if id had to choose all over again, but in case you prefer it too or have a similar form factor to the ATtiny85 then follow along.

Here's a diagram again:

![](./Attiny-trackpoint.png)

| TrackPoint | ATtiny85 physical pins | Nice!Nano clone | Note    |
| ---------- | -------- | --------------- | --------------------- |
| -          | 1        | -               | Leave RST float       |
| CLK        | 2        | -               |                       |
| DAT        | 3        | -               |                       |
| GND        | 4        | GND             |                       |
| -          | 5        | P0.20           | Via 4.7k ohm resistor |
| -          | 6        | P0.06           | MOT                   |
| -          | 7        | P0.17           | Via 4.7k ohm resistor |
| VCC        | 8        | VCC             |                       |
| -          | 4 -> 8   | -               | Via 100nf capacitor   |

There seem to be difference between the ATtiny85 and the Pro Mini, that required the ATtiny85 to have MOT line, this is better than doing blind 10ms polling, the MOT made a huge difference on how the ATtiny85 smooth reading.

### Flashing the ATtiny85

This is where another Arduino (not the dedicated CH340G) like Arduino Uno or the Arduino Leonardo which is the one i used, could be used to flash the ATtiny.

But regardless I'm sure the wiring are identical (although i only tested with Leonardo), you would typically connect pins from the ICSP to the ATtiny

From the Arduino IDE before you connect the ATtiny, flash an Arduino ISP sketch to the Uno/Leonardo, you should find it in the Example in the Arduino IDE.

This is why the 8 Pin IC Base IC Socket 4+4 Pin are important, as you will move the ATtiny to flash, then back to the Nice!nano for interfacing.

<img width="1031" height="658" alt="image" src="https://github.com/user-attachments/assets/6f10453f-b3d9-4d23-b00d-0fb82c1d7bb7" />

| Uno/Leonardo      | ATtiny85 Pin | Function    |
|-------------------|--------------|-------------|
| Digital Pin 10    | Pin 1        | RESET (PB5) |
| ICSP Pin 6 (GND)  | Pin 4        | GND         |
| ICSP Pin 4 (MOSI) | Pin 5        | PB0         |
| ICSP Pin 1 (MISO) | Pin 6        | PB1         |
| ICSP Pin 3 (SCK)  | Pin 7        | PB2         |
| ICSP Pin 2 (5V)   | Pin 8        | VCC         |

### Resources

- [The ATtiny85 sketch](https://github.com/Magid-William/attiny85-trackpoint/blob/main/trackpoint-i2c-slave-attiny85/trackpoint-i2c-slave-attiny85.ino) for reading the PS/2 from the TrackPoint and interfacing using I2C
- [Pre-builds hex](https://github.com/Magid-William/attiny85-trackpoint/releases/tag/EXP64) ready to be flashed

# Step 3: The ZMK side

- [Here's the driver](https://github.com/Magid-William/zmk-trackpoint-driver) it holds integration instructions.
- [Shield example](https://github.com/Magid-William/zmk-trackpoint-shield)
- [My personal shield](https://github.com/Magid-William/zmk-config-dabaseV_0-2), it uses a dongle

# My dev workflow

<details>
	
<summary>
	The following is Agentic coding workflow, for inspiration only.
</summary>


I used an LLM coding agent for every thing software in this project, this is my first project i start using OpenCode with DeepSeek V4 flash, 

Basically i define every feature/problem/reproduction/bugfix as an experiment, i start by saying 

```
Read @Experiments.md
```

It reads the compact `Experiments.md` and says it's ready to work on x, i ignore the suggestion and say

```
In this experiment i want to do Y, and only focus on Y so i could prove that Y is better than X, blah blah blah.
Ask me questions before the final plan
```

It then gives me a plan or ask me clarifying questions

After you approve the plan, it will create an `.md` file for this experiment with the plan, it has hypothesis, method, conclusion will be updated later.

I made sure to make it clear in the `AGENTS.md` that i preferer a closed loop, where the agent:
- Make changes
- Commit them
- Waits until the Github action finishes, iterate if it failed.
- Programmatically enters bootloader without you physically press the reset button twice
- Flashes the new firmware
- Open the serial monitor and read the logs to confirm it's changes are reflected

For example, instead of asking if the TrackPoint is working by moving it physically, ask it to create a synthetic movement in the Pro Mini side, this way you don't have to touch the TrackPoint.

When you are happy with the result ask it:
```
conclude this experiment
```

It will then write it's conclusion in the experiment dedicated `.md` file and update the `Experiments.md`, and commit any uncommitted changes.

Although i now think this last part need more refining to include adding the scripts that worked for it, as some models will keep on retrying many scripts to flash the Pro Mini, where it didn't before, ughhh such's LLM coding life.

But that's basically it, i start an experiment, then 5 hours later (could be 5 could be 10 could be 15 mins, it depends) if i got what i want i; conclude it, if i got no where, i say something like:

```
Erase this Experiment completely, locally and from Github
```

I did this only 3~4 times, unless there is something important for example going SPI was important but proved to be pain, so i simply call it failed, so it learn from it and not waste time re exploring failed paths.

It only took 60 experiments for about 2 months 🫥, but hey we are here and I'm using it right now; Yay!! 🎊

By "it" i mean the coding agent of course 🤖🐋.

[Here's the repo with the AGENTS.md and all](https://github.com/Magid-William/trackpoint-knowledge)

</details>

# Step 5: use it

<img width="1600" height="1124" alt="image" src="https://github.com/user-attachments/assets/405c1641-c9d2-41ea-a336-00711cb01071" />

I found a random screw driver cap to work great as a "rim cap", i used baking powder and super glue to fill the gap and be able to attach it to the TrackPoint, no cracks so far, it turned out fine.

# Other resources and Special thanks

- [@db7](https://github.com/db7)
	- [Cheap and Dirty Logic Analyzer with Teensy](https://randalea.de/~db7/teensy-logic-analyzer.html)
	- [Crunching a PS/2 Mouse Decoder](https://randalea.de/~db7/crunch-ps2-decoder.html)
  
- [@alonswartz](https://github.com/alonswartz)
	- [Guide: How to integrate a TrackPoint in a mechanical keyboard](https://github.com/alonswartz/TrackPoint)
	
- [@infusedkim](https://github.com/infused-kim)
	- [kb_zmk_ps2_mouse_TrackPoint_driver](https://github.com/infused-kim/kb_zmk_ps2_mouse_TrackPoint_driver)
	- [kb_zmk_ps2_mouse_TrackPoint_driver-zmk_config](https://github.com/infused-kim/kb_zmk_ps2_mouse_TrackPoint_driver-zmk_config)

- [@Ahmed-M-Osman1](https://github.com/Ahmed-M-Osman1)
	- [His i2c trackpad example](https://github.com/Ahmed-M-Osman1/zmk-driver-azoteq)
	
- [@badjeff](https://github.com/badjeff)
	- [All his github repos were valiable](https://github.com/badjeff)
