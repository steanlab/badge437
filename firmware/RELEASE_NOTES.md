# n437 firmware 0.9k: release notes

Repo path: `steanlab/badge437` (public) → `firmware/RELEASE_NOTES.md`. Release date: 14 November 2026. The previous releases, 0.9j (`firmware/n437_0.9j.bin`), 0.9f, 0.9e, 0.9d and 0.9a, stay in the repository.

| | |
|---|---|
| File | `firmware/n437_0.9k.bin` (103440 bytes) |
| SHA-256 | `c5ef90bbc62f3d56a2a4b19f09a9fa39a98fb69e05349a38195c288075e83254` (also in `firmware/SHA256SUMS.txt`; check with `sha256sum -c SHA256SUMS.txt`) |
| Version string | `437-0.9k` (boot line `N437 fw 437-0.9k`) |
| Target | 4.37" tag on a Telink TLSR8258 (512 KiB flash, 176 x 480 black / white / red / yellow panel) |
| Install | with the programmer the first time ([user guide](../docs/USER_GUIDE.md)), later over Bluetooth (OTA) from 0.9 or later; the memory layout is unchanged, pictures and settings are kept |
| Page | <https://steanlab.github.io/badge437/> (offers the update by itself when the tag runs an older version) |

## What is new in 0.9k

* **The link is closed after 5 minutes of silence.** In the standalone mode a client that stays connected and sends no command used to keep the tag awake for ever (the window does not end while a link is up). Now the tag closes the link after 300 s without a write (log line `IDLE: no command for 300 s, link closed`); not during an upload or a pin test; OpenDisplay mode is not touched. The page also disconnects after 5 minutes without user action.
* Tested on one tag by the owner (14 November 2026). Everything from 0.9j stays.

## What is new in 0.9j (earlier release) (fixes; update if the tag runs the slideshow by itself)

* **The tag did not go to sleep with a long slideshow interval.** 0.9f and earlier slept in pieces of up to 250 s. The wake-up time handed to the chip's sleep call is a 32-bit tick count; 250 s is further ahead than the chip's library accepts, so the sleep was **silently refused** and the tag stayed awake. Seen on tags with a battery and an interval of 1080 minutes: a slide change, then a weak blue flash every 5 s, red flashes, again and again, and a battery drained at the awake current. Pieces are now **120 s**. Found with a log of the uptime and the new `sr=` counter: the tag had not restarted in 21 minutes. (The limit is inferred from the behaviour: the library is closed.)
* **The connectable window opened again after 268 s.** The "window is over" test compared a 32-bit timer difference that wraps every 268 s; a tag that stayed awake got a fresh window (blue flashes) every 4 min 28 s. The end of a window is now remembered.
* **A refused sleep is handled**: counted (`sr=` in `STATUS`), retried with the timer alone, the interval counter takes the piece back, one red flash per idle period instead of one per second.
* **A PC4 wake-up counts as a tap only when the NFC chip reports an event** (flags `nf=` in `STATUS`); otherwise it is a quiet timer piece.
* **New setting `4F 0A n`**: wake from deep sleep by a tap on / off (default on). Taps still work while the tag is awake.
* **`STATUS` is complete**: the log line was cut at 100 characters (the tail `ld=`, `wf=` was lost on long lines); the buffer is 160 now. New fields `vr` (raw supply ADC, **not validated**), `irq`, `nf`, `sr` ([protocol](../docs/PROTOCOL.md)).
* Tested on **one** tag with its stock battery (13 to 14 November 2026): it sleeps without any LED signal (20 minutes, then more than a day), a tap wakes it (`src=0x8c`, `nf` not zero), the slide changes and the window opens; `sr=0` after more than 1000 quiet wake-ups. Battery life and the current were **not measured**. Not tested: power loss during an update, other tags.
* Not solved: the battery voltage is still not measured (`v=0`; `vr` is a raw ADC number, not a voltage), so the low-battery signal never appears.

## What is new in 0.9f (earlier release)

* **Panel data check reported.** The `STATUS` line now ends with `wf=1` or `wf=0`: whether the waveform block at `0x78000` passes its checksum. The page shows a red notice when it does not (uploads still work; drawing does not). Nothing else changed; 0.9e features stay. The 0.9f file was built and the page was tested in a browser simulation; the new flag has not yet been seen on a tag.

## What is new since 0.9d (0.9e)

* **Boot splash.** After a power-up or restart the tag draws a black picture with **BADGE437 PROJECT** in big white letters and the firmware version under it (two passes, about 28 s). A restart after an update shows the new version. It can be switched off (card "Operating mode" or `4F 09 00`). With the slideshow on, the first slide follows 2 minutes after the splash.
* **Slide order.** The slideshow can go in turn or in random order (random never repeats the slide that is on the panel). Setting `4F 08 n` or the new slideshow card of the page.
* **No redraw of the same slide.** If the next slide is the one already on the panel and unchanged (a single slide, or a tap with one slide), the panel is not redrawn: no 28 s and no energy for nothing.
* **Page:** a **first-start wizard** (connect, firmware version, orientation, first picture, first draw, slideshow; each step is checked from the tag's answers; can be hidden), a **slideshow card** (switch, interval in minutes or hours, order, slides, clean-up of the panel, "next slide now"), thumbnails of the uploaded slides in the list, a counter while a slide is drawn, a warning for intervals under 5 minutes, remembered picture settings, eight colours with ochre, better tone mapping of greys.
* Tested on a tag (12 November 2026): update from 0.9d over Bluetooth, the splash appears; draw time of a two-pass picture about 28 s; slideshow with both slide formats changes by a tap.

## What is new since 0.9a

* **Two-pass drawing: a real black.** One drive pass draws all four colours, but black comes out dark maroon (contrast about 3.8 : 1 against white, a red tint). 0.9d draws a picture in two passes: black is now neutral and about 4.5 : 1 against white. A draw takes longer than the 18 s of 0.9a: about **28 s** measured (18 s + pause + a short second pass of 2 s). The drive details are not published.
* **Red is the panel's dark red.** The 0.9a colour table drew "red" as an orange-brown; 0.9d draws the panel's dark red. The colour table setting `lut` keeps its default `27`; with that default the firmware draws in two passes, any other value draws one pass as 0.9a did ([`docs/PROTOCOL.md`](../docs/PROTOCOL.md)).
* **Eight colours** (page: "colours" = 8): white, yellow, orange, ochre, dark red, black, grey, dark grey. New slot formats 3, 4, 5 hold the pictures of the two passes (made by the page; not documented). The four-colour formats 0, 1, 2 and OpenDisplay work as before.
* **Default orientation** of fresh settings is now "mirrored horizontally" (`mode 2`), which is the right one for this panel. Tags that already store `mode 0` keep it until you set it ([user guide](../docs/USER_GUIDE.md) section 2).
* The temperature range of the drive was forced to other values in a test build and the colours looked the same; the draw time changes (14 to 27 s).
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
| A photo from the page in the eight-colour mode (Floyd-Steinberg, 26 KB; 0.9d) | drawn; orange, ochre, greys, dark red, yellow and black visible; the author judged it good by eye |
| Other temperature ranges forced (test build 0.9bt) | the colours looked the same; refresh 27 s / 18 s / 18 s / 14 s |

**Tested on a tag since:** four-colour LZ picture drawn in two passes, slideshow change by NFC tap with both formats (12 Nov 2026, author's report). **Not tested on a tag:** OpenDisplay writes with 0.9d; clean-up draws with two passes; battery and current (no instrument).

## Known issues and limits

1. **Orientation of older settings.** A tag that stores `mode 0` (for example one flashed with 0.9a and never set) draws mirrored; set "mirrored horizontally" once (page, card "Panel", or `4D 02 17 27`).
2. **Colours are what the panel gives.** Photographed in daylight, relative to the panel white: black 0.23 to 0.30, dark red 0.28 to 0.32 (red / green 1.6), yellow 0.73 (red / green 1.4), white 1; the panel is pale and flat compared with a screen, and dark red and black are nearly equally light. The page dithers against ideal screen colours, so mid-tones come out lighter than the original (no tone mapping yet). Measured on one tag only.
3. **No authentication** (standalone window or OpenDisplay): anyone in range can change the tag while it is connectable. OpenDisplay encryption is not implemented.
4. **No battery measurement** (`v=0`), no energy figures; a two-pass draw takes longer and certainly uses more energy than one pass. Do not rely on a battery-life estimate.
5. **Rollback limits:** it covers images that begin to run; a broken start-up code or a hang during initialisation needs the programmer. The step from 0.8 to 0.9 has no rollback.
6. **First start formatting:** the first start after flashing erases the data area (about 4 s); settings of older versions are lost then. An OTA update from 0.9 or later keeps them.
7. Only images whose text contains `N437 fw 437-` are accepted by OTA; the OpenDisplay config reports `Firmware 1.0` and the build in the SHA string.
8. The eight-colour mode needs this firmware; an older firmware refuses the new formats (`UP FAIL bad length or format`).

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
| 0.9d | eight colours, two-plane slot formats, default orientation |
| 0.9e | boot splash, slide order, no redraw of the same slide |
| 0.9f | waveform block state in `STATUS` (`wf=`), notice on the page |
| 0.9j | fixes: deep sleep pieces of 120 s (250 s was refused), end of the window remembered, `4F 0A`, complete `STATUS` (0.9g to 0.9i were test builds, not released) |
| 0.9k | the link is closed after 300 s without a command (standalone mode) (this release) |

## Memory layout (data is not kept across layout changes)

`0x40000` marker, `0x41000` name, `0x42000` / `0x43000` settings, `0x44000`..`0x74FFF` slots, `0x75000` rollback copy, `0x76000` trial journal, `0x77000` unused. Unchanged since 0.9. Details in [`docs/HARDWARE.md`](../docs/HARDWARE.md).
