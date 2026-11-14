# n437 firmware 0.9j: Bluetooth commands and formats

Repo path: `steanlab/badge437` (public) → `docs/PROTOCOL.md`. Companion: `docs/HARDWARE.md`. Firmware: `firmware/n437_0.9j.bin`. Date: 14 November 2026.

For people who write their own page or tool for this firmware, or their own firmware with the same formats. Most of it was exercised on a tag by the control page or the OpenDisplay tool; items marked *not tried* were not.

## 1. Transport

* BLE peripheral, advertising name **`OD-xxxx`** (`xxxx` = last two bytes of the address by default, or the tail set with command `4E`, 1..5 characters). In standalone mode it advertises only inside a window (section 7).
* One GATT service **`0x2446`** with one characteristic **`0x2446`**: write (with or without response) from the client, notifications to the client.
* Two protocols share this characteristic: a message whose first byte is **`0x00`** is **OpenDisplay** (section 5); any other first byte is one of **our commands** (single-byte opcode, section 2). Our commands answer with **text lines** (ASCII, one notification per line; the page matches them by prefix), OpenDisplay commands answer with binary `status cmd data` (`00` = ok, `FF` = refused).
* The firmware asks for a fast connection interval (12..16 units) while an upload runs and a relaxed one (40..56) otherwise; the link timeout is 6 s / 10 s. A long panel refresh does not stop the radio, but some phones drop the link during it.

## 2. Our commands

All numbers below are bytes; `len32`, `crc32`, `seq16`, `every16` are **little endian**.

| Command | Meaning / answer |
|---|---|
| `02` | status: boot counter, wake source, uptime, then `STATE mode= radio= wt= wb= img= tr= tn=` (and a `TRIAL ...` line after an update). `fw` shows the version; the `STATUS` line ends with `wf=1` (the panel data block passes its checksum) or `wf=0` (damaged, the tag will not draw; from 0.9f). Fields: `boots` = deep-sleep wake-ups in a row since the last power-up (8-bit, wraps at 256), `dw=1` = this start is a wake-up from deep sleep, `src` = wake-up status register (bit 1 timer, bit 2 core, bit 3 pad = NFC chip on PC4; bit 7 is set on every start and means nothing), `up` = seconds since this start (a 32-bit timer difference: wraps every 268 s), `v` / `vr` = supply voltage / raw ADC value (**not validated**, do not read it as a voltage), `irq=1` = PC4 (NFC interrupt) is high, `nf` = flags of the NFC chip read at the last pad wake-up (`FFF9 FFF8 FFF7`; 0 = no event), `sr` = deep-sleep entries that were refused (normally 0), `ld` = reason of the last disconnect (255 = none); `irq`, `nf`, `sr` from 0.9j |
| `01 nn` | deep sleep (no retention) for `nn` seconds, then a cold start |
| `04 nn` | after every wake stay connectable 10 s, then deep sleep `nn` s again (`00` stops) |
| `40` | slot list: `slot N: fmt F, B bytes, S sectors, crc=...` per used slot and `slots: U used, F of 49 sectors free, largest run L, max 24 slots` |
| `41 ss` | erase slot `ss` (`FF` = all sectors of the slot area, also what an interrupted upload left) |
| `42 ss len32 crc32 win [fmt]`, `43 seq16 bytes...`, `44` | **upload** of a stored stream into slot `ss`, section 3 (`fmt` 0..5 since 0.9d) |
| `49` | abort a running upload |
| `45 ss` | draw slot `ss` (two passes, about 28 s; refused while another draw runs) |
| `46 ss` | write the built-in test picture into slot `ss` |
| `47 ss` | re-read slot `ss`, check CRC-32 and decode once |
| `48` | report ATT MTU and data length of the link |
| `4A en every16 mask0 poll [clean_n clean_mode [mask1 [mask2]]]` | slideshow: `en` 0/1; `every16` minutes 1..1080; `mask0` = bits of slots 0..7, optional `mask1` / `mask2` (bytes 9 and 10 of the message, after `clean_n clean_mode`) = slots 8..15 / 16..23; `poll` seconds 10..250, unused in standalone; `clean_n` = clean the panel before every n-th slide (0 never); `clean_mode` 1 = white, 2 = black then white. Stored. Answers `SS ...` |
| `4B` | report the slideshow settings and state (`SS ...`) |
| `4C` | draw the next filled slot now |
| `4D mode slot [lut]` | picture orientation at draw time (`mode` 0..3, bit 0 reverse the lines, bit 1 reverse the pixels of a line; default of fresh settings 2 since 0.9d), the slot that takes the OpenDisplay stream (0..23) and the colour table `lut` (default `27`; leave it unless you know why: with the default the four-colour pictures are drawn in two passes). Without arguments: report |
| `4E chars...` | name tail 1..5 printable ASCII characters (name = `OD-` + tail); without characters the default |
| `4F A5` | reboot (about 0.4 s later) |
| `4F 01 n` | radio power index 0..6, stored |
| `4F 02 n` | watchdog on / off (0 / 1), stored; leave it on |
| `4F 03` | `SYS tx= wd= led= v= vl= t= ta= vr= ts= mode= wt= wb= sw=` (`v` battery: 0 = not measured; `sw` = settings sector erase counter) |
| `4F 04 n` | LED mode 0..2 (2 = all events, default; 1 = boot, errors, low battery), stored |
| `4F 05 m` | operating mode 0 standalone / 1 OpenDisplay, stored, the tag restarts |
| `4F 06 t b` | window in seconds after a tap (`t`) and after power-up (`b`), 10..250 each, stored (defaults 60 / 120) |
| `4F 07 A5` | OTA commit (section 6) |
| `4F 08 n` | slide order 0 in turn / 1 random (0.9e), stored; the `SS ...` report ends with `order=n` |
| `4F 09 n` | boot splash 0 off / 1 on (0.9e), stored; `SYS ...` ends with `sp=n` |
| `4F 0A n` | wake from deep sleep by an NFC tap 0 off / 1 on (default, 0.9j), stored; `SYS ...` shows `tw=n`. Off: the tag sleeps in pieces and only a power cut opens a window; taps still work while the tag is awake |
| `34` | abort a running draw (at the next BUSY wait) |
| `2C hh ll [n]`, `2D` | NFC chip memory dump (n <= 128) / rewrite the text record now |
| `30`..`3F`, `10`, `11`, `20`, `21`, `24`..`2B` | diagnostics from the bring-up builds (raw panel access, test patterns, pin probes, LED, NFC probes); not needed by a normal client and **not documented**; they can draw garbage on the panel |

## 3. Slot upload (`42` / `43` / `44`)

The tag stores a **stored stream**: either the raw frame or its compressed form (section 4); `len32` is the length of the stored stream and `crc32` its CRC-32 (zlib / IEEE 802.3, init and final XOR `FFFFFFFF`).

1. Client: `42 ss len32 crc32 win fmt`: `win` = chunks per acknowledgement (1..32, default 8), `fmt` = 0 raw (then `len32` must be 21120), 1 LZ, 2 line-XOR + LZ (default 0 when omitted); since 0.9d also 3, 4, 5 (the formats of the eight-colour mode, not documented here; the page makes them). Older firmware refuses 3..5.
2. Tag: `UP READY chunk=C win=W mtu=M rx=R fmt=F sect=N`: `C` = payload bytes per chunk (MTU - 3 - 3), `W` = the window, `N` = sectors the slot needs. Replacing a slot erases the old one first, so an interrupted replacement leaves the slot empty. A refusal is `UP FAIL ...` or `slot N: no room for K sectors (free F, largest run L)`.
3. Client: chunks `43 seq16 data` (`data` up to `C` bytes), `seq16` starting at 0 and **consecutive** (a gap or repeat ends the upload with `UP FAIL seq X expected Y`). After every `W` chunks and after the last one the tag answers **`UP ACK n`** (`n` = bytes received); a client may write without response and wait for `UP ACK` only (the page's default is with acknowledgement, "without" is faster).
4. Client: `44`. Tag: verifies the CRC-32, decodes the stream once (compressed formats must decode to the full frame) and writes the slot header **last**: `UP OK slot N crc=XXXXXXXX`, or `UP FAIL why`. `49` aborts.

The slot area is erased and written in whole 4 KiB sectors, first fit, up to 24 slots; a slot is a run of sectors whose first 256 bytes are the header:

| Offset | Meaning |
|---|---|
| 0..3 | `S437` |
| 4 | layout version, 2 |
| 5 | format: 0 raw frame (21 120 bytes), 1 LZ4 block, 2 LZ4 block of the line-XORed frame, 3..5 eight-colour formats (not documented) |
| 6 | slot number 0..23 |
| 7 | number of sectors of the run (= ceil((256 + length) / 4096), at most 11) |
| 8..11 | stored length (LE) |
| 12..15 | CRC-32 of the stored stream |
| 16..19 | serial |

The directory is rebuilt from the headers at start (the run of a valid header is skipped, so data that merely looks like a header is not taken for one).

## 4. Frame and compression

Frame: 480 lines x 44 bytes (176 pixels, 4 per byte, first pixel in bits 7..6), **OpenDisplay colour codes: black 0, white 1, yellow 2, red 3**. The panel codes, line order and pixel order are applied **when drawing** (`4D`), so they can change without uploading again; the page sends the picture in natural order and the tag reverses the pixels of each line at draw time when `mode` bit 1 is set (needed on this panel, see `docs/USER_GUIDE.md`).

Formats 1 and 2 use the **plain LZ4 block format** (token, literals, 16-bit offset, match length, **no trailing empty token**) with **offsets up to 2048**, so the decoder needs a 2 KiB history and one 44-byte line and runs while the line goes to the panel. Format 2 first XORs every line with the line above (line 0 unchanged), decoding XORs back on the fly. Line reversal (`mode` bit 0) is not applied to compressed slots (the lines are decoded in order). Measured sizes: white frame 87 bytes, flat logo 117, text-like 22 %, noisy dithered gradient 92 %.

**Eight-colour formats (3, 4, 5, since 0.9d).** They hold two pictures for the two drive passes; the layout is not documented here (the page produces them). With the default colour table `lut` = `27` the four-colour formats (0..2) are drawn in two passes as well, which gives a real black.

## 5. OpenDisplay subset

Messages start with `00` and a command byte; the replies are `status cmd data`.

| Message | Answer |
|---|---|
| `00 40` | configuration: 176 x 480, four colours (black, white, red, yellow), rotation 0, no encryption; packets 1, 2, 4 and 32 are answered |
| `00 43` | firmware version (major 1, minor 0, length-prefixed build string `n437-437-0.9j`) |
| `00 44` | manufacturer data record (company id + 14 bytes) |
| `00 50` | authenticate: answers **status `03` (no encryption configured)** |
| `00 70`, `00 71` ..., `00 72` | direct write: start, data chunks (230 bytes each in the tool we tried), end. **Uncompressed 21 120 bytes only** (a size field for compressed data is refused). The stream goes into the slot set by `4D` (default 23) and is drawn when it ends; `00 73` follows when the refresh is over |
| `00 0F` | reboot, no reply |

Tried with the OpenDisplay web tool (opendisplay.org Toolbox): config read, picture write with its dithering, refresh notification. *Not tried:* Home Assistant, the other OpenDisplay clients, encryption (not implemented).

## 6. Firmware image upload and commit (OTA)

Same `42` / `43` / `44` protocol with **slot number `F0`**, `fmt` 0, `len32` 16 KiB..124 KiB: the image goes into the area that is not running (A `0x00000`, B `0x20000`), with the flag byte at offset 8 left blank. After `44` the tag checks CRC-32, a read-back of the written area, the header (`KNLT` at 8..11, the length field at `0x18` equals `len32`) and the identity (the text `N437 fw 437-` somewhere in the image) and answers **`OTA STAGED 437-x.y`** or `OTA FAIL ...`. Uploads are refused while a trial is open.

**`4F 07 A5`** commits: the first sector of the running image is copied to `0x75000`, an "armed" entry is appended to the journal (`0x76000`), the new image's flag byte `0x4B` is written, then the old image's flag is cleared (`4B` -> `00`), then the tag restarts (`OTA DONE`). The new image runs **on trial**: its first action is to count the start in the journal; it is confirmed after 5 s of main loop or before a deep sleep. At the 4th unconfirmed start (3 tries) it restores the previous image's first sector from the copy and restarts. `STATE ... tr=` 0 idle / confirmed, 1 on trial, 2 rolled back, 3 rollback failed; `tn=` unconfirmed starts counted; the line `TRIAL 1=<reset source>/<stage> 2=.. 3=..` shows for each unconfirmed start the reset-source register and the last stage reached (2 settings loaded, 3 initialisation done, 4 main loop entered).

## 7. Operating modes and windows

* `4F 05 0` standalone (default): radio only in a window of `wb` seconds after power-up / reset (default 120) and `wt` seconds after a tap or after a link closes (default 60); while a link or upload runs the window stays open. Outside windows the tag is in deep sleep (pieces of at most 250 s); a timer wake-up runs without the radio and draws a due slide. A NFC tap (PC4) wakes it.
* `4F 05 1` OpenDisplay: always advertising and connectable.
* The LED shows a window: a 20 ms blue flash every 5 s while it is open and nobody is linked.

## 8. Settings storage

32-byte records in two flash sectors used alternately (`0x42000`, `0x43000`), sequence number plus wear counter, check byte; a torn record is ignored and the newest valid one wins, so a power loss never loses the settings. Stored: slideshow, orientation, colour table, OpenDisplay slot, radio power, watchdog, LED mode, operating mode and windows, name (separate log at `0x41000`). The format marker (`0x40000`) changes when the layout changes; a different marker makes the first start erase the data area.
