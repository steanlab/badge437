# Hanshow Nebular Pro 437Q-N: hardware reference for firmware authors

Repo path: `steanlab/badge437` (public) → `docs/HARDWARE.md`. Companion: `docs/PROTOCOL.md` (the commands and formats of our firmware). Date: 12 November 2026.

This is what was found out while writing the firmware, written for someone who wants to write their own. **Every fact has a label:**

* **[verified]**: checked by our own firmware running on a 437Q-N (one tag, powered from the programmer);
* **[photo]**: read from the markings and photographs of the board;
* **[data]**: read from the data of the tags we have (flash backups of three tags);
* **[assumed]**: taken from the sister tags (154QN, 970Q-N), not checked here.

What is deliberately **not** in this document: contents of any flash backup, the panel waveform data and its layout, the panel command sequence and the drive of the colours, serial numbers, addresses, and the analysis of the original firmware. **Your own tag's waveform data is in your own backup; you need it, and nobody else's will do** (see section 5). Make the backup before you write anything (section 2).

## 1. The tag

| Item | Value |
|---|---|
| Product | Hanshow Nebular Pro 437Q-N, a 4.37" electronic shelf label [photo] |
| Board marking | `HSEL4Q_04_37M_32`, date code `YW2403` [photo] |
| MCU module | marking `HS9118`, **Telink TLSR8258** (TC32 core, 2.4 GHz BLE), 24 MHz system clock, **512 KiB internal flash** (JEDEC id `EB 60 13` as the programmer script knows it) [photo][verified] |
| Panel | 4.37" e-paper, **480 x 176 pixels**, four colours black / white / red / yellow, controller family marked `S437` in the factory data; 26-pin FPC marked `P437040-MF1-A-M`; the panel scans 176 columns by 480 rows [photo][data] |
| LED | one RGB LED [verified] |
| NFC | FM11NT083V-class chip, I2C, NFC Forum Type 2 memory, antenna loop around the board edge [verified] |
| Battery | pouch cell marked `CF332544 750mAh Hanshow 3.0V`; the prefix and rating point to a **non-rechargeable lithium (Li-CFx) cell**: not confirmed, treat it as not rechargeable and never charge it [photo][assumed] |
| Debug / programming pads (MCU side) | `NRST TX RX SWS VCC GND`, plus battery `+` / `-` [photo] |
| Panel test pads (connector side) | labelled with the panel signals: `GDR VSH2 RST CS SDA VDD VGH VGL` and `RESE BUSY DC CK VBAT VSH1 VSL VCOM`; the SPI-like lines can be watched with a logic analyser without soldering to the FPC [photo] |

## 2. Programming, backup and flash protection

* The programming interface is the Telink single-wire **SWS** (pads `NRST`, `TX`, `RX`, `SWS`, `VCC`, `GND` in one row on the MCU side; `TX` / `RX` are not needed for flashing). The Hanshow RP2040 bridge (Gerard780, v1.6) with the flasher [`tools/nebular_debug_custom.py`](../tools/README.md) (`--model 437`) worked on Ubuntu with a Raspberry Pi Pico build [verified]; wiring and pad photo in [USER_GUIDE.md](USER_GUIDE.md) section 0. The programmer's 3.3 V powers the tag; no battery is needed [verified].
* **Back up the whole 512 KiB first.** The script does it automatically before any write. The backup is the only copy of your tag's factory data. Treat it as private.
* **Flash block protection.** The stock firmware leaves the chip's block protection set: status register value `0x2C` (high byte `00`), so erase and write in the upper half of the flash do nothing until the protection is cleared. The programmer clears it for the time of the write and restores it. Our firmware does the same from the tag's own code: it writes the **16-bit status register** (mask `0x407C`) only if the status reads exactly `2C 00` or `2C 38`, and puts the original value back after every erase / write [verified]. If your firmware leaves the protection cleared, the programmer script will refuse the tag next time (it only accepts `2C`); restore it.
* **Code that runs while the flash is busy must be in RAM.** A status-register write makes the flash chip busy, and instruction fetch from the same flash then fails: the MCU hangs until the watchdog resets it. The status write and the wait for its end must execute from RAM [verified: this was a real bug, 0.3 hung on it].

## 3. Pins

| Function | Pin | Label |
|---|---|---|
| Panel RESET | PD4 | [verified] |
| Panel CS | PD2 | [verified] |
| Panel clock | PD7 | [verified] |
| Panel data (SDA, bit-banged, also read back for the temperature) | PB6 | [verified] |
| Panel DC | PB7 | [verified] |
| Panel BUSY | PA1 | [verified]; **high = idle** |
| Panel power enable | PB5 | [verified]; **low = panel powered**; the pin is released (input with pull-up) when off |
| LED red / green / blue | PB4 / PD3 / PA7 | [verified]; **active low** |
| NFC I2C SDA / SCL / chip-select / IRQ | PC0 / PC1 / PC6 / PC4 | [verified]; IRQ active low, used as the deep-sleep wake-up |
| UART TX (the pad `TX`) | PB1 | [verified]; log text at 115200 8N1 |
| UART RX (the pad `RX`) | PA0 | [photo][assumed] |
| Battery voltage (ADC) | PB3 | [assumed]; **not verified**, our firmware does not measure the battery yet |

## 4. Flash map

Addresses are flash addresses; the Telink boot ROM starts from address 0. The stock firmware keeps its application at the bottom of the flash and its own data higher up; our firmware's first start **erases every non-blank sector of `0x40000`..`0x76FFF`** (what the stock firmware keeps there is in your backup). Layout of 0.9a:

| Range | Use in our firmware 0.9j |
|---|---|
| `0x00000`..`0x1FFFF` | **image A** (128 KiB; the programmer writes here; 0.9j is 103 224 bytes) |
| `0x20000`..`0x3FFFF` | **image B** (OTA target while A runs, and the other way round) |
| `0x40000` | format marker (`N437FMT5`) |
| `0x41000` | device name log |
| `0x42000`, `0x43000` | settings (two sectors used alternately, 32-byte records) |
| `0x44000`..`0x74FFF` | slot area: 49 sectors, up to 24 pictures |
| `0x75000` | rollback copy (first sector of the retired image) |
| `0x76000` | OTA trial journal |
| `0x77000` | unused (SDK pairing store address, pairing is off) |
| **`0x78000`..`0x7BFFF`** | **panel waveform block (factory data of your panel): NEVER WRITE**; checked by CRC before every draw |
| `0x7D000` | serial strings of the tag: never write |
| **`0x7E000`** | **factory record: NEVER WRITE** |
| **`0x7F000`** | **SDK sector (radio MAC address and calibration): NEVER WRITE** |

Rules our firmware follows, and you should too: write only inside a window that you define (ours: `0x40000`..`0x76FFF`, plus the idle image area during an OTA upload); everything else is dropped. The SDK has two writers of its own (the OTA timeout and the pairing store): point the pairing store (`CFG_ADR_PEER`) at an unused sector, or switch pairing off.

**Factory record (`0x7E000`).** It identifies the model: the panel geometry as two 16-bit values (`176` and `480`) at offsets `+0x12` and `+0x14` and the **model code `0x2B`** at `+0x2F` identify a 437Q-N. Read it to refuse other tags; do not write it.

**Record revisions seen [5 tags].** The 92 bytes are identical on every tag of a variant (no serial number in them). Revision A (4 tags): the record the stock flasher accepts. **Revision B (1 tag): bytes `+0x00`, `+0x01` and `+0x2E` differ** (`61 D7` / `0A` in A, `9C 2F` / `03` in B); the panel size, the diagonal and the model code are the same. The first two bytes look like a checksum of the rest (we did not find the formula), the meaning of `+0x2E` is unknown. The waveform block of the revision B tag is intact and has a different CRC than the revision A tags, so a different panel lot is possible. **Our firmware does not read this record: the revision B tag was flashed with 0.9f and draws exactly like the others.** The stock flasher compares the record byte for byte and refuses B; [`tools/check_factory_record.py`](../tools/check_factory_record.py) tells the variant and [`tools/make_tolerant_script.py`](../tools/make_tolerant_script.py) makes a local copy of the flasher that accepts any record saying 437Q-N (size, diagonal and model code as above).

## 5. The panel waveform block (`0x78000`)

The stock firmware does not contain the drive waveforms of the panel; it reads them from a block of factory data in the tag's flash, **per panel lot**. The block is calibration data of your panel; **we do not publish any waveform data or its internal layout**. A firmware needs the block of the tag it runs on, which is in **your own backup** (section 2); nobody else's will do.

* **Location and size:** `0x78000`, `0x3000` bytes (12 KiB; the range up to `0x7BFFF` is kept free). **Never write or erase it.**
* **Check it before every draw** (it carries a checksum in its first bytes) and **refuse to draw if the check fails**: one tag we saw had a damaged part of it and drew garbage.
* **It can be damaged by other firmware [verified on 2 of our 4 tags].** Two of our tags had the sector `0x79000` (the middle 4 KiB of the block) erased and rewritten with a few bytes before our firmware was ever flashed; both had run builds based on ATC_BLE_OEPL, which keep their settings in that sector. The stock tags we dumped (2) were intact. Check your backup with [`tools/check_waveform.py`](../tools/check_waveform.py) before flashing (the first two bytes of the block are a CRC16 of the rest). Firmware 0.9f also reports the state in the `STATUS` line (`wf=1` / `wf=0`).

## 6. Panel temperature

The panel has a temperature sensor read through the data line: `CMD 41 00`, `CMD 40`, wait until BUSY goes high (about 12 ms), then read **two bytes**: the integer part in degrees C and the fraction in 1/256 (`17 80` = 23.5 C) [verified]. The reading is **too high right after a refresh and sometimes after a power-up**; our firmware ignores a value more than 8 C above the last good reading (younger than 30 minutes) and, if the reading is not usable, power-cycles the panel (2, 5, 10 s) and reads again. Draw only between -10 and +50 C.

## 7. Drawing the panel

The panel controller is driven bit-banged over its own SPI-like bus with the waveform records of the block above, in the order the stock firmware uses. **We do not publish the command sequence.** If you write your own firmware, derive it from the stock code in your own backup. A draw takes about 18 s per pass at room temperature. Do not start a draw if the waveform check failed or the temperature is out of range; a wrong picture does no harm, the next draw replaces it. Do not refresh more often than needed: the panel is not meant for fast updates.

## 7a. Colours

The panel shows white, yellow, orange, dark red, black and two greys. The colours come from **two drive passes** over the same picture (about 28 s in total, measured); a single pass cannot give a real black (it comes out dark maroon). Measured on one tag from raw phone photos in daylight, relative to the panel white: black about 0.21 of the white's luminance (contrast about 4.5 : 1), dark grey 0.36, grey 0.65, yellow 0.73, orange about 0.43, dark red about 0.30. **Blue and green cannot be shown** (no way to get blue above red); green can only be suggested as olive by mixing yellow with a dark colour. The page uses eight colours (white, black, dark red, yellow, orange, ochre, grey, dark grey) and dithers against them. The drive details are not published.

## 8. Picture format

A frame is **480 lines of 44 bytes**: 176 pixels, **2 bits per pixel, four pixels per byte, the first pixel in bits 7..6**; 21 120 bytes. Line 0 is at the top when the flex cable is at the top of the picture. With the pixels of a line sent in their natural order the picture appeared **mirrored left to right** (flex cable at the top); reversing the pixels inside every line (our setting `mode` bit 1) corrects it [verified].

## 9. NFC

* Chip at I2C 7-bit address **`0x57`** (8-bit `0xAE`), with a chip-select line on PC6 (PC6 must be driven for the chip to answer) and an active-low IRQ on PC4 [verified].
* Memory is the NFC Forum **Type 2** layout: capability container `E1 10 6D 00` at `0x000C` (NDEF, 872 bytes, read / write), NDEF TLV from `0x0010` [verified]. A phone reads an NDEF text record without the MCU running.
* The field of a phone toggles PC4 and sets flag registers (`FFF7`..`FFF9`); a touch gives several events a second or so apart. Our rule: a **tap** is the first event after 5 s without events. PC4 low also wakes the MCU from deep sleep (`cpu_set_gpio_wakeup`, low level; the pull-up must survive the sleep) [verified].
* The phone's field does **not** power the MCU: what the phone reads is the text record as it was written last (we rewrite it, changed bytes only, after slide changes and when a link closes).
* We do not write the chip's configuration cells.

## 10. LED, UART, power

* **LED** pins are active low, three independent GPIOs. Our signals are 20 to 80 ms flashes; the LED is bright, keep it short.
* **UART**: TX only, PB1, 115200 8N1 at the 24 MHz system clock; our firmware prints text lines (boot, status, upload progress). It is silent in a radio-less timer wake-up.
* **Power**: the tag runs from the programmer's 3.3 V without the battery [verified]. A tag with its stock cell showed about **3.1 V** on the `VBAT` pad at idle [verified]. The current of a refresh and of the sleep modes was **not measured**; do not assume numbers.
* The panel supplies (VGH, VGL, VSH1, VSH2, VSL, VCOM, VDD) are made by the panel's own circuit [photo].

## 11. Telink TLSR8258 pitfalls we met

1. **Only variables in the `RAM` (retention) section survive a BLE retention sleep.** `.bss` is zeroed after a wake-up from deep retention; state that must live across sleeps must be marked. A directory rebuilt only in the cold-start path was lost in 0.5 [verified bug].
2. **The 32-bit system timer wraps after about 268 s** (16 MHz tick). Anything that counts longer must add elapsed time before each sleep.
3. **Analog registers `0x35`..`0x39` keep their value through deep sleep**; we use them as scratch (marks, elapsed time). `analog_read(0x44)` is the wake-up source: `0x8e` at power-up, `0x82` after a software **or** watchdog reset (they cannot be told apart).
4. **Watchdog: arm it after the SDK initialisation.** The SDK changes the timer registers during start-up; a watchdog armed at the very beginning of `main()` reset good images repeatedly [verified bug, 0.9].
5. **Flash status writes and waits from RAM** (section 2).
6. **One binary in two areas.** The boot ROM starts the image whose flag byte at offset 8 (the `K` of `KNLT`) is `0x4B`; the SDK option `USE_SET_BOOT=1` makes the start-up code copy the ROM's boot selection to register `0x80063e` so the same binary can run from `0x00000` or `0x20000`. On our tag the register reads `00` when image A runs and `81` when image B runs. A flag byte can only be cleared by writing (bits go 1 -> 0); setting it again needs an erase of its sector.
7. **Image header:** `KNLT` at bytes 8..11, the image length as u32 at `0x18`. The build must be cut to that length.
8. The ADC battery reading, radio calibration and MAC live in the SDK sector `0x7F000`: never write it.
9. **SDK pairing store** and **OTA timeout** both write flash behind your back (section 4).

## 12. What is not known

* Current consumption in any mode; the battery chemistry (inferred only); the battery voltage thresholds of this cell.
* Contents and purpose of the panel's own 6144-byte data block (read with `CMD 92`); it is not needed for drawing.
* How the panel's colours behave over temperature (looked the same to the eye at 21 C across the records we tried); no measurements at other temperatures.
* Partial refresh.
* The behaviour on other panel lots than the one we have.

Corrections are welcome: open an issue with what you measured and how.
