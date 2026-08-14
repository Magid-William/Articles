```
hello world;
```
# Intro
In this article I'm going to showcase how i integrated a Chinese generic USB TrackPoint like this one:

![https://randalea.de/~db7/assets/trackpoint.png](https://randalea.de/~db7/assets/trackpoint.png)

With ZMK using a co-processor.

My current setup uses an ATtiny85, but i also used Arduino ProMini 8Mhz 3.3V and it was as good.

Using the ATtiny85 this is the wiring:

![](./Attiny-trackpoint.png)

## Bill of materials

| Component               | Quantity | Note                                                              |
| ----------------------- | -------- | ----------------------------------------------------------------- |
| This generic TrackPoint | 1        |                                                                   |
| ATtiny85                | 1        | Don't get the dev board version it might consume more power       |
| Arduino Uno             | 1        | For programming the ATtiny85, i personally used Arduino Leonardo. |
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

## Step 1: Getting the TrackPoint out

The USB TrackPoint consists of 2 parts:
- The TrackPoint sensor (the smaller PCB)
- A housing PCB that exposes the TrackPoint as a USB.

We only need the TrackPoint sensor here, to do so we'll need to de-solder it.

> Warning: I personally had 2 of these TrackPoints, and in both times i ended up flocking a pin, i eventually recovered them, but this is a very delicate process, don't do them if you were exited for example (i know i was).

<img width="118" height="333" alt="image" src="https://github.com/user-attachments/assets/06aeb2fb-bc92-417d-a4c3-1ac51326be38" />

In order to de-solder it safely, cover the pins with solder and use at least 250C for the solder iron temp, by covering them you would be thermally interfacing with all the pins at once.

One pin that seemed tricky was the GND pin, it's the left most pin, it's somehow soldered using a different solder material than the other pins, it was so tricky and I'm not sure why it's the case, but I'm guessing more temp is better, may be even flux.

The following is the pin mapping:

<img width="300" height="282" alt="600px-T420_pinout" src="https://github.com/user-attachments/assets/3a3dddd8-4f6e-426e-8266-05f6c4a9d94b" />

From left to right, the following is the pin mapping table:

| Pin | Note |
| --- | ---- |
| GND | |
| CLK | |
| DAT | |
| RST | Not connected to anything, ignore it |
| VCC | |
| M1  | |
| M3  | |
| M2  | |

## Step 2: choosing the co-processing

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

### flashing the Pro Mini

