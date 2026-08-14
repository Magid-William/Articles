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

## Step 2:
