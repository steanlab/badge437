# badge437

Repo path: `steanlab/badge437` (public).

Own firmware and a web control page for a **4.37" electronic shelf label on a Telink TLSR8258**: a tag with a 480 x 176 pixel black / white / red / yellow e-paper panel, a Telink TLSR8258 Bluetooth LE module, an RGB LED and an NFC chip. The firmware replaces the original one and turns the tag into a small picture frame / badge that you control from a phone or a PC.

**Release 0.9j (14 November 2026)**: [`firmware/n437_0.9j.bin`](firmware/n437_0.9j.bin) (0.9f, 0.9e, 0.9d and 0.9a stay in the same folder; **update from 0.9f or older if you use a long slideshow interval**, see the notes), notes in [`firmware/RELEASE_NOTES.md`](firmware/RELEASE_NOTES.md). Control page: <https://steanlab.github.io/badge437/> (Chrome or Edge, Android or desktop; Web Bluetooth).

Unofficial: not affiliated with Hanshow, Telink, OpenDisplay or OpenEPaperLink. **Flashing replaces the original firmware of your tag and needs a programmer wire; use it at your own risk, no warranty.** Tested so far on **one** tag.

## Read this first: two stages

A tag comes with the original firmware, and **it cannot be updated over Bluetooth or from the page**. Our firmware gets onto the tag in two stages:

| Stage | How | When |
|---|---|---|
| **1. First installation** | **With a programmer wire (Telink SWS: an RP2040 bridge, one 1 kOhm resistor and five wires to pads on the board; wiring, photo and commands in the guide), once.** You back up the original flash of your tag first, then write `firmware/n437_0.9e.bin`. See the [user guide](docs/USER_GUIDE.md), sections 0 and 1 | once per tag; **there is no way around it**: without a programmer the tag stays original |
| **2. Everything afterwards** | **Over Bluetooth from the page**: pictures, settings and **firmware updates (OTA)**; no wires | every later change; OTA needs firmware 0.9 or later already running on the tag |

So: if you do not have (or do not want to build) a programmer, this project is not for you yet. If you do, do stage 1 once and forget the wire.

## What it does

| | |
|---|---|
| Pictures | Up to 24 pictures ("slots") are stored in the tag's flash and survive power loss. A picture is 176 x 480 pixels in four colours (white, black, dark red, yellow) or, with the page's "8 colours" option, eight (adds orange, ochre, grey, dark grey; needs 0.9d); the page converts any image (fit, rotation, dithering, brightness / contrast, preview) and uploads it compressed (a flat graphic takes a few hundred bytes, a dithered photo about 90 % of the raw 21 120 bytes) |
| Slideshow | Slides change by timer (1 minute to 18 hours), in turn or in random order, set on the page; the same slide is not redrawn; the tag sleeps in between; a slide also changes when you **touch the tag with a phone (NFC tap = next slide)** |
| Two operating modes | **Standalone** (default): Bluetooth is only on for a window after power-up and after a tap, deep sleep otherwise, to save the battery. **OpenDisplay**: always connectable, works with the OpenDisplay web tool and Home Assistant (direct write of one picture) |
| Boot splash | After a power-up or restart the tag shows BADGE437 PROJECT and the firmware version (can be switched off) |
| LED | Short, dim flashes tell the state (window open, linked, slide change, error); can be reduced |
| NFC | The tag carries a text record with version, last panel temperature, slide count and so on, readable by any phone |
| Update over Bluetooth (OTA) | New firmware is uploaded into a second image area from the page, checked, started on trial and **rolled back by the tag itself** if it does not run properly (needs 0.9 or later already running) |
| Safety | The firmware never writes the panel's factory waveform data, the factory record or the radio calibration; the flash write protection of the chip is restored after every write; an interrupted upload leaves no half picture |

## Start

1. Read [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) (Russian: [`docs/USER_GUIDE.ru.md`](docs/USER_GUIDE.ru.md)). It covers the programmer, the **backup of your tag's original flash (required, keep it)**, flashing, the first start, the page, modes, NFC and OTA.
2. Check the file: `sha256sum -c firmware/SHA256SUMS.txt`.
3. After flashing, open the page, connect, and check in the card "Panel" that the orientation is **mirrored horizontally** (the default of 0.9d; a tag that stored another value keeps it, see the guide).

## Documents

| File | For whom |
|---|---|
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md), [`docs/USER_GUIDE.ru.md`](docs/USER_GUIDE.ru.md) | users: flash, first start, page, modes, LED, NFC, slideshow, OTA, problems |
| [`firmware/RELEASE_NOTES.md`](firmware/RELEASE_NOTES.md) | what is in 0.9j, what was tested on a tag, what is not done, history |
| [`docs/HARDWARE.md`](docs/HARDWARE.md) | for those who want to write their own firmware: the tag (MCU, pins, flash map and what must never be written, panel basics, NFC, LED, power, Telink pitfalls); **not** the panel drive recipe |
| [`docs/PROTOCOL.md`](docs/PROTOCOL.md) | Bluetooth commands of the firmware, OpenDisplay subset, basic slot and image formats |

## Not done / limits (0.9j)

* **No authentication.** In standalone mode anyone near the tag can connect during an open window (after power-up or a tap) and change pictures, settings and even upload firmware; the window is short and the physical tap or power cycle is the only protection. OpenDisplay encryption is not implemented.
* The battery voltage is not measured yet and the energy consumption was not measured; no battery-life figure is given. The tag's cell is probably a non-rechargeable lithium cell (see the hardware notes): never charge it.
* OTA rollback covers a faulty image that starts running; an image that is broken before its own start code runs, or hangs during its initialisation, needs the programmer. Power loss during an update was only tested in simulation, not on a tag.
* Colours: the panel's own colours are pale and flat (black about 4.5 : 1 against white, dark red nearly as dark as black); the page dithers against ideal colours, so mid-tones come out lighter than the original. Measured on one tag. A draw takes longer than before (two passes, about 28 s measured).
* The firmware source code is not published (binary releases only).

## What is published here, and what is not

Published: the page, released firmware binaries with checksums, guides, and the hardware notes that are safe to publish. **Not** published: flash dumps, the panel's waveform data and its layout, the panel drive sequence and the colour drive (two passes), the eight-colour slot formats, serial numbers and addresses of tags, the firmware source code, and analysis of the original firmware. If you write your own firmware you must read the data of your own tag from your own backup.

Related projects by the same author: [frame970](https://github.com/steanlab/frame970) (the 9.7" tag), [badge154](https://github.com/steanlab/badge154) (the 1.54" tag).

## Licence

Copyright 2026 steanlab. The page, the firmware binaries and the documents of this repository are free for **personal, non-commercial use**; commercial use needs a written agreement with the author. Details: [`LICENSE.md`](LICENSE.md). Third-party parts and their terms: [`NOTICE.md`](NOTICE.md). Unofficial; no warranty.
