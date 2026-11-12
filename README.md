# badge437

Repo path: `steanlab/badge437` (public).

Own firmware and a web control page for the **Hanshow Nebular Pro 437Q-N**: a 4.37" electronic shelf label with a 480 x 176 pixel black / white / red / yellow e-paper panel, a Telink TLSR8258 Bluetooth LE module, an RGB LED and an NFC chip. The firmware replaces the original one and turns the tag into a small picture frame / badge that you control from a phone or a PC.

**Release 0.9a (12 November 2026)**: [`firmware/n437_0.9a.bin`](firmware/n437_0.9a.bin), notes in [`firmware/RELEASE_NOTES.md`](firmware/RELEASE_NOTES.md). Control page: <https://steanlab.github.io/badge437/> (Chrome or Edge, Android or desktop; Web Bluetooth).

Unofficial: not affiliated with Hanshow, Telink, OpenDisplay or OpenEPaperLink. **Flashing replaces the original firmware of your tag and needs a programmer wire; use it at your own risk, no warranty.** Tested so far on **one** tag.

## What it does

| | |
|---|---|
| Pictures | Up to 24 pictures ("slots") are stored in the tag's flash and survive power loss. A picture is 176 x 480 pixels in four colours; the page converts any image (fit, rotation, dithering, brightness / contrast, preview) and uploads it compressed (a flat graphic takes a few hundred bytes, a dithered photo about 90 % of the raw 21 120 bytes) |
| Slideshow | Slides change by timer (1 minute to 18 hours), the tag sleeps in between; a slide also changes when you **touch the tag with a phone (NFC tap = next slide)** |
| Two operating modes | **Standalone** (default): Bluetooth is only on for a window after power-up and after a tap, deep sleep otherwise, to save the battery. **OpenDisplay**: always connectable, works with the OpenDisplay web tool and Home Assistant (direct write of one picture) |
| LED | Short, dim flashes tell the state (window open, linked, slide change, error); can be reduced |
| NFC | The tag carries a text record with version, last panel temperature, slide count and so on, readable by any phone |
| Update over Bluetooth (OTA) | New firmware is uploaded into a second image area from the page, checked, started on trial and **rolled back by the tag itself** if it does not run properly (needs 0.9 or later already running) |
| Safety | The firmware never writes the panel's factory waveform data, the factory record or the radio calibration; the flash write protection of the chip is restored after every write; an interrupted upload leaves no half picture |

## Start

1. Read [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) (Russian: [`docs/USER_GUIDE.ru.md`](docs/USER_GUIDE.ru.md)). It covers the programmer, the **backup of your tag's original flash (required, keep it)**, flashing, the first start, the page, modes, NFC and OTA.
2. Check the file: `sha256sum -c firmware/SHA256SUMS.txt`.
3. First thing after flashing: open the page, connect, and in the card "Panel" set the orientation to **mirrored horizontally** (see the guide, the default of 0.9a shows pictures mirrored).

## Documents

| File | For whom |
|---|---|
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md), [`docs/USER_GUIDE.ru.md`](docs/USER_GUIDE.ru.md) | users: flash, first start, page, modes, LED, NFC, slideshow, OTA, problems |
| [`firmware/RELEASE_NOTES.md`](firmware/RELEASE_NOTES.md) | what is in 0.9a, what was tested on a tag, what is not done, history |
| [`docs/HARDWARE.md`](docs/HARDWARE.md) | **for those who want to write their own firmware**: everything found out about the tag (MCU, pins, flash map and what must never be written, panel, NFC, LED, power, Telink pitfalls) |
| [`docs/PROTOCOL.md`](docs/PROTOCOL.md) | Bluetooth commands of the firmware, OpenDisplay subset, slot and image formats |

## Not done / limits (0.9a)

* **No authentication.** In standalone mode anyone near the tag can connect during an open window (after power-up or a tap) and change pictures, settings and even upload firmware; the window is short and the physical tap or power cycle is the only protection. OpenDisplay encryption is not implemented.
* The battery voltage is not measured yet and the energy consumption was not measured; no battery-life figure is given. The tag's cell is probably a non-rechargeable lithium cell (see the hardware notes): never charge it.
* OTA rollback covers a faulty image that starts running; an image that is broken before its own start code runs, or hangs during its initialisation, needs the programmer. Power loss during an update was only tested in simulation, not on a tag.
* The colours are not calibrated yet (preview and dithering use nominal colours; red and black come out darker than on screen).
* The firmware source code is not published (binary releases only).

## What is published here, and what is not

Published: the page, released firmware binaries with checksums, guides, and the hardware notes that are safe to publish. **Not** published: flash dumps, the panel's waveform data, serial numbers and addresses of tags, the firmware source code, and analysis of the original firmware. If you write your own firmware you must read the data of your own tag from your own backup.

Related projects by the same author: [frame970](https://github.com/steanlab/frame970) (the 9.7" tag), [badge154](https://github.com/steanlab/badge154) (the 1.54" tag).
