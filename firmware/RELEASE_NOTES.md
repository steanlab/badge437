# n437 firmware 0.9d: release notes

Repo path: `steanlab/badge437` (public) → `firmware/RELEASE_NOTES.md`. Release date: 12 November 2026. The previous release, 0.9a (`firmware/n437_0.9a.bin`), stays in the repository.

| | |
|---|---|
| File | `firmware/n437_0.9d.bin` (101 072 bytes) |
| SHA-256 | `d5320443634c0eb60b8a943ea9d88376d800a0f6447aaf66d52caf52bf6611eb` (also in `firmware/SHA256SUMS.txt`; check with `sha256sum -c SHA256SUMS.txt`) |
| Version string | `437-0.9d` (boot line `N437 fw 437-0.9d`) |
| Target | Hanshow Nebular Pro 437Q-N (Telink TLSR8258, 512 KiB flash, 4.37" 176 x 480 black / white / red / yellow panel) |
| Header | `KNLT` at bytes 8..11, length field at 0x18 = file length = 101 072 |
| Install | with the programmer the first time ([user guide](../docs/USER_GUIDE.md)), later over Bluetooth (OTA) from 0.9 or later; the memory layout is unchanged, pictures and settings are kept |
| Page | <https://steanlab.github.io/badge437/> (new page with the "colours" selector) |

## What is new since 0.9a

* **Two-pass drawing: a real black.** One long pass draws all four colours, but black comes out dark maroon (contrast about 3.8 : 1 against white, a red tint). 0.9d adds the second, **short pass** (the short waveform record of the same temperature range, after a 4 s pause) that adds the black: black is now neutral and about 4.5 : 1 against white. A draw takes longer than the 18 s of 0.9a: estimated about **23 s** (18 s + 4 s pause + a short second refresh; **not timed yet**). Details in [`docs/HARDWARE.md`](../docs/HARDWARE.md) section 7a.
* **Red is the panel's dark red.** The 0.9a colour table drew "red" with panel code 0, which is an orange-brown; 0.9d draws it with panel code 3 (dark red). The colour table setting `lut` keeps its default `27`; with that default the firmware draws in two passes with fixed tables, any other value draws one pass with that table as 0.9a did ([`docs/PROTOCOL.md`](../docs/PROTOCOL.md)).
* **Seven colours** (page: "colours" = 7): white, yellow, orange, dark red, black, grey, dark grey. New slot formats 3, 4, 5 hold two planes of panel codes, one per pass (PROTOCOL.md sections 3 and 4). The four-colour formats 0, 1, 2 and OpenDisplay work as before.
* **Default orientation** of fresh settings is now "mirrored horizontally" (`mode 2`), which is the right one for this panel. Tags that already store `mode 0` keep it until you set it ([user guide](../docs/USER_GUIDE.md) section 2).
* Diagnostic command `30 pp mm rr`: `rr` (0..7) forces the waveform record of that temperature range. The author drew the four colour bands with ranges 4, 5, 6 and 7 and saw no difference in the colours; the refresh takes 27 s with range 4 and 14 s with range 7 (18 s at room temperature with the range chosen by the sensor).
* Page: colour selector (4 / 7), brightness and contrast on separate rows, format names for the new formats.

## What is in it (since earlier versions)

* **Pictures from flash slots.** 24 slots, 49 sectors (196 KiB) of 4 KiB; raw, LZ4 or line-XOR + LZ4 format chosen by the page (the smallest wins); a picture is checked (CRC-32, decoded once) before it counts; an interrupted upload leaves nothing. A seven-colour picture is up to 42 240 bytes (11 sectors), a typical photo 20 to 30 KB, so only a few of them fit.
* **Slideshow**: timer (1 min to 18 h), slide mask, optional clean-up draws (white, or black then white) every n-th slide; deep sleep between slides.
* **NFC**: tap the tag with a phone = next slide; a text record shows version, panel temperature, slide count, free flash.
* **Two modes**: standalone (default; radio only in a window of 120 s after power-up and 60 s after a tap; radio-less timer wake-ups) and OpenDisplay (always connectable; config, firmware version, direct write of one picture; tested with the OpenDisplay web tool).
* **LED signals** (blue flash = window open, green = linked, yellow = slide change, red = error / window over).
* **Update over Bluetooth (OTA)** with **trial and rollback**: upload into the idle image area (A `0x00000`, B `0x20000`), checks, "Switch"; the new image runs on trial and is confirmed after 5 s of main loop (or on going to deep sleep); at the fourth unconfirmed start the tag restores the previous image.
* Flash safety: writes only in the data window `0x40000`..`0x76FFF` (and the idle image area during an OTA upload); the chip's block protection (status `2C`) is cleared for one operation and restored afterwards; settings are kept in two alternating sectors so that a power loss never loses them.

## Tested on a tag

Tested by the author on the **same one tag** (powered from the programmer, no battery) on 12 November 2026, in daylight with a phone camera (raw photos, white paper in the frame):

| | Result |
|---|---|
| OTA from 0.9a through test builds up to 0.9d, pictures kept | works |
| Second pass alone over a white fill (`30 00 02`, then `30 01 00`; 0.9a) | black, grey and dark grey bands over white: black 0.21, dark grey 0.36, grey 0.65 of the white's luminance |
| Built-in picture (`46 00`, `45 00`) in two passes (0.9c) | neutral black, white, yellow, dark red as intended; black about 4.4 : 1 against white in a large block |
| A seven-colour photo from the page (Floyd-Steinberg, slot 6, 26 KB LZ plane format; 0.9d) | drawn; orange, greys, dark red, yellow and black visible; the author judged it good by eye |
| Waveform ranges 4 to 7 forced by `30 00 00 rr` (0.9bt) | the colours looked the same; refresh 27 s / 18 s / 18 s / 14 s |

**Not tested on a tag:** four-colour pictures from the page (formats 1, 2) drawn with the two-pass path of 0.9d; slideshow, NFC tap and clean-up draws with two passes; OpenDisplay writes with 0.9d; the grey levels over anything but white (the page never puts them there); power loss during an OTA upload, commit or rollback (simulated on a PC only); a second tag; battery operation and current consumption; OpenDisplay from Home Assistant.

## Known issues and limits

1. **Orientation of older settings.** A tag that stores `mode 0` (for example one flashed with 0.9a and never set) draws mirrored; set "mirrored horizontally" once (page, card "Panel", or `4D 02 17 27`).
2. **Colours are what the panel gives.** Photographed in daylight, relative to the panel white: black 0.23 to 0.30, dark red 0.28 to 0.32 (red / green 1.6), yellow 0.73 (red / green 1.4), white 1; the panel is pale and flat compared with a screen, and dark red and black are nearly equally light. The page dithers against ideal screen colours, so mid-tones come out lighter than the original (no tone mapping yet). Measured on one tag only.
3. **No authentication** (standalone window or OpenDisplay): anyone in range can change the tag while it is connectable. OpenDisplay encryption is not implemented.
4. **No battery measurement** (`v=0`), no energy figures; a two-pass draw takes longer and certainly uses more energy than one pass. Do not rely on a battery-life estimate.
5. **Rollback limits:** it covers images that begin to run; a broken start-up code or a hang during initialisation needs the programmer. The step from 0.8 to 0.9 has no rollback.
6. **First start formatting:** the first start after flashing erases the data area (about 4 s); settings of older versions are lost then. An OTA update from 0.9 or later keeps them.
7. Only images whose text contains `N437 fw 437-` are accepted by OTA; the OpenDisplay config reports `Firmware 1.0` and the build in the SHA string.
8. The seven-colour mode needs this firmware; an older firmware refuses the new formats (`UP FAIL bad length or format`).

## History (short)

| Version | Change |
|---|---|
| 0.1 / 0.2 | bring-up: pins, panel power, first pictures (not released) |
| 0.3 / 0.4 | slots in flash, upload, orientation and colour table |
| 0.5 | compression, slideshow with deep sleep |
| 0.6 | NFC tap, text record, OpenDisplay direct write |
| 0.7 | standalone / OpenDisplay modes, windows, LED signals |
| 0.8 | OTA over Bluetooth, two image areas |
| 0.9 / 0.9a | trial and rollback; 0.9a: watchdog armed after the initialisation (released) |
| 0.9b / 0.9c | two-pass drawing, dark red as red (test builds, not released) |
| 0.9d | seven colours, two-plane slot formats, default orientation (this release) |

## Memory layout (data is not kept across layout changes)

`0x40000` marker, `0x41000` name, `0x42000` / `0x43000` settings, `0x44000`..`0x74FFF` slots, `0x75000` rollback copy, `0x76000` trial journal, `0x77000` unused. Unchanged since 0.9. Details in [`docs/HARDWARE.md`](../docs/HARDWARE.md).
