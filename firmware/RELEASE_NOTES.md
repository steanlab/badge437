# n437 firmware 0.9a: release notes

Repo path: `steanlab/badge437` (public) → `firmware/RELEASE_NOTES.md`. Release date: 12 November 2026.

| | |
|---|---|
| File | `firmware/n437_0.9a.bin` (100 308 bytes) |
| SHA-256 | `16c97cb3a68a436810220ebe85709e816836555d73a4e0d79e3fdfa0b2070329` (also in `firmware/SHA256SUMS.txt`; check with `sha256sum -c SHA256SUMS.txt`) |
| Version string | `437-0.9a` (boot line `N437 fw 437-0.9a`) |
| Target | Hanshow Nebular Pro 437Q-N (Telink TLSR8258, 512 KiB flash, 4.37" 176 x 480 black / white / red / yellow panel) |
| Header | `KNLT` at bytes 8..11, length field at 0x18 = file length = 100 308 |
| Install | with the programmer the first time ([user guide](../docs/USER_GUIDE.md)), later over Bluetooth (OTA) |
| Page | <https://steanlab.github.io/badge437/> |

## What is in it

* **Pictures from flash slots.** 24 slots, 49 sectors (196 KiB) of 4 KiB; raw, LZ4 or line-XOR + LZ4 format chosen by the page (the smallest wins); a picture is checked (CRC-32, decoded once) before it counts; an interrupted upload leaves nothing.
* **Slideshow**: timer (1 min to 18 h), slide mask, optional clean-up draws (white, or black then white) every n-th slide; deep sleep between slides.
* **NFC**: tap the tag with a phone = next slide; a text record shows version, panel temperature, slide count, free flash.
* **Two modes**: standalone (default; radio only in a window of 120 s after power-up and 60 s after a tap; radio-less timer wake-ups) and OpenDisplay (always connectable; config, firmware version, direct write of one picture; tested with the OpenDisplay web tool).
* **LED signals** (blue flash = window open, green = linked, yellow = slide change, red = error / window over).
* **Update over Bluetooth (OTA)** since 0.8: two image areas A (`0x00000`) and B (`0x20000`), upload into the idle one, checks, "Switch".
* **Trial and rollback** since 0.9: the new image runs on trial; it is confirmed after 5 s of main loop (or on going to deep sleep); at the fourth unconfirmed start the tag restores the previous image from a copy and restarts. 0.9a fixes a mistake of 0.9 (the watchdog was armed too early, good images were rolled back).
* Flash safety: writes only in the data window `0x40000`..`0x76FFF` (and the idle image area during an OTA upload); the chip's block protection (status `2C`) is cleared for one operation and restored afterwards; settings are kept in two alternating sectors so that a power loss never loses them.

## Tested on a tag

Tested by the author on **one** tag (powered from the programmer, no battery) from 11 to 12 November 2026:

| | Result |
|---|---|
| Flash with the programmer, start, formatting of the data area | works |
| Panel: all four colours, 18 s per refresh, slot upload / draw / verify, compressed slots | works; **orientation default needs a setting, see below** |
| Standalone window, link, LED signals, NFC tap, timer slideshow with deep sleep | checked by the author |
| OpenDisplay web tool: config, direct write of a picture | works (the link may drop during the draw and reconnect by itself) |
| OTA A -> B and B -> A, data kept | works (upload of about 100 KB takes about 16 s, restart about 10 s) |
| Trial: good image confirmed, hanging image rolled back (about 50 s) | works (0.9a) |

**Not tested on a tag:** power loss during an OTA upload, commit or rollback (only simulated on a PC with a power loss at every flash operation); a second tag; the battery operation and the current consumption; OpenDisplay from Home Assistant.

## Known issues and limits

1. **Orientation.** The firmware default draws pictures **mirrored horizontally**. After flashing, set the orientation once (page, card "Panel": "mirrored horizontally", or send `4D 02 17 27`); it is stored and survives updates. (The fix of the default is planned for the next release.)
2. **No authentication** (standalone window or OpenDisplay): anyone in range can change the tag while it is connectable. OpenDisplay encryption is not implemented.
3. **No battery measurement** (`v=0`), no energy figures. Do not rely on a battery-life estimate.
4. **Rollback limits:** it covers images that begin to run; a broken start-up code or a hang during initialisation needs the programmer. The step from 0.8 to 0.9 has no rollback.
5. **First start formatting:** the first start after flashing (or after the first OTA from 0.8) erases the data area (about 4 s); slides, name and settings of older versions are lost.
6. Colours are nominal (not calibrated); the panel's red and black are darker than on screen.
7. Only images whose text contains `N437 fw 437-` are accepted by OTA; the OpenDisplay config reports `Firmware 1.0` and the build in the SHA string.

## History (short)

| Version | Change |
|---|---|
| 0.1 / 0.2 | bring-up: pins, panel power, first pictures (not released) |
| 0.3 / 0.4 | slots in flash, upload, orientation and colour table |
| 0.5 | compression, slideshow with deep sleep |
| 0.6 | NFC tap, text record, OpenDisplay direct write |
| 0.7 | standalone / OpenDisplay modes, windows, LED signals |
| 0.8 | OTA over Bluetooth, two image areas |
| 0.9 / 0.9a | trial and rollback; 0.9a: watchdog armed after the initialisation |

## Memory layout (data is not kept across layout changes)

`0x40000` marker, `0x41000` name, `0x42000` / `0x43000` settings, `0x44000`..`0x74FFF` slots, `0x75000` rollback copy, `0x76000` trial journal, `0x77000` unused. Details in [`docs/HARDWARE.md`](../docs/HARDWARE.md).
