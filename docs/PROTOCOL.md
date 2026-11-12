# n437 firmware 0.9d: Bluetooth commands and formats

Repo path: `steanlab/badge437` (public) → `docs/PROTOCOL.md`. Companion: `docs/HARDWARE.md`. Firmware: `firmware/n437_0.9d.bin`. Date: 12 November 2026.

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
| `02` | status: boot counter, wake source, uptime, then `STATE mode= radio= wt= wb= img= tr= tn=` (and a `TRIAL ...` line after an update). `fw` shows the version |
| `01 nn` | deep sleep (no retention) for `nn` seconds, then a cold start |
| `04 nn` | after every wake stay connectable 10 s, then deep sleep `nn` s again (`00` stops) |
| `40` | slot list: `slot N: fmt F, B bytes, S sectors, crc=...` per used slot and `slots: U used, F of 49 sectors free, largest run L, max 24 slots` |
| `41 ss` | erase slot `ss` (`FF` = all sectors of the slot area, also what an interrupted upload left) |
| `42 ss len32 crc32 win [fmt]`, `43 seq16 bytes...`, `44` | **upload** of a stored stream into slot `ss`, section 3 (`fmt` 0..5 since 0.9d) |
| `49` | abort a running upload |
| `45 ss` | draw slot `ss` (two passes, estimated 23 s, section 4; refused while another draw runs) |
| `46 ss` | write the built-in test picture into slot `ss` |
| `47 ss` | re-read slot `ss`, check CRC-32 and decode once |
| `48` | report ATT MTU and data length of the link |
| `4A en every16 mask0 poll [clean_n clean_mode [mask1 [mask2]]]` | slideshow: `en` 0/1; `every16` minutes 1..1080; `mask0` = bits of slots 0..7, optional `mask1` / `mask2` (bytes 9 and 10 of the message, after `clean_n clean_mode`) = slots 8..15 / 16..23; `poll` seconds 10..250, unused in standalone; `clean_n` = clean the panel before every n-th slide (0 never); `clean_mode` 1 = white, 2 = black then white. Stored. Answers `SS ...` |
| `4B` | report the slideshow settings and state (`SS ...`) |
| `4C` | draw the next filled slot now |
| `4D mode slot [lut]` | picture orientation at draw time (`mode` 0..3, bit 0 reverse the lines, bit 1 reverse the pixels of a line; default of fresh settings 2 since 0.9d), the slot that takes the OpenDisplay stream (0..23) and the colour table `lut` (bits `2i+1..2i` = panel code of OpenDisplay colour `i`; default `0x27`). **With `lut` = `27` the four-colour formats are drawn in two passes with fixed tables (section 4); any other value draws one pass with that table.** Stored. Answers `OD mode=.. slot=.. lut=..` |
| `4E chars...` | name tail 1..5 printable ASCII characters (name = `OD-` + tail); without characters the default |
| `4F A5` | reboot (about 0.4 s later) |
| `4F 01 n` | radio power index 0..6, stored |
| `4F 02 n` | watchdog on / off (0 / 1), stored; leave it on |
| `4F 03` | `SYS tx= wd= led= v= vl= t= ta= vr= ts= mode= wt= wb= sw=` (`v` battery: 0 = not measured; `sw` = settings sector erase counter) |
| `4F 04 n` | LED mode 0..2 (2 = all events, default; 1 = boot, errors, low battery), stored |
| `4F 05 m` | operating mode 0 standalone / 1 OpenDisplay, stored, the tag restarts |
| `4F 06 t b` | window in seconds after a tap (`t`) and after power-up (`b`), 10..250 each, stored (defaults 60 / 120) |
| `4F 07 A5` | OTA commit (section 6) |
| `34` | abort a running draw (at the next BUSY wait) |
| `2C hh ll [n]`, `2D` | NFC chip memory dump (n <= 128) / rewrite the text record now |
| `30`..`3F`, `10`, `11`, `20`, `21`, `24`..`2B` | diagnostics from the bring-up builds (raw panel access, test patterns, pin probes, LED, NFC probes); **`30` .. `3F` draw with raw panel codes** and are not needed by a normal client. `30 pp mm [rr]`: one pass `pp` (0 long record, 1 short record) with pattern `mm` (0 four bands of the codes 0..3, 1..4 whole-screen fill with code 0..3, 5 marker), `rr` (0..7) forces the waveform record of that temperature range |

## 3. Slot upload (`42` / `43` / `44`)

The tag stores a **stored stream**: either the raw frame or its compressed form (section 4); `len32` is the length of the stored stream and `crc32` its CRC-32 (zlib / IEEE 802.3, init and final XOR `FFFFFFFF`).

1. Client: `42 ss len32 crc32 win fmt`: `win` = chunks per acknowledgement (1..32, default 8), `fmt` = 0 raw (then `len32` must be 21120), 1 LZ, 2 line-XOR + LZ (default 0 when omitted); since 0.9d also 3 raw two planes (then `len32` must be 42240), 4 LZ two planes, 5 line-XOR + LZ two planes (section 4). Older firmware refuses 3..5.
2. Tag: `UP READY chunk=C win=W mtu=M rx=R fmt=F sect=N`: `C` = payload bytes per chunk (MTU - 3 - 3), `W` = the window, `N` = sectors the slot needs. Replacing a slot erases the old one first, so an interrupted replacement leaves the slot empty. A refusal is `UP FAIL ...` or `slot N: no room for K sectors (free F, largest run L)`.
3. Client: chunks `43 seq16 data` (`data` up to `C` bytes), `seq16` starting at 0 and **consecutive** (a gap or repeat ends the upload with `UP FAIL seq X expected Y`). After every `W` chunks and after the last one the tag answers **`UP ACK n`** (`n` = bytes received); a client may write without response and wait for `UP ACK` only (the page's default is with acknowledgement, "without" is faster).
4. Client: `44`. Tag: verifies the CRC-32, decodes the stream once (formats 1, 2 must produce exactly 480 lines, formats 4, 5 exactly 960) and writes the slot header **last**: `UP OK slot N crc=XXXXXXXX`, or `UP FAIL why`. `49` aborts.

The slot area is erased and written in whole 4 KiB sectors, first fit, up to 24 slots; a slot is a run of sectors whose first 256 bytes are the header:

| Offset | Meaning |
|---|---|
| 0..3 | `S437` |
| 4 | layout version, 2 |
| 5 | format: 0 raw frame (21 120 bytes), 1 LZ4 block, 2 LZ4 block of the line-XORed frame, 3 raw two planes (42 240 bytes), 4 LZ4 block of the two planes, 5 LZ4 block of the line-XORed planes |
| 6 | slot number 0..23 |
| 7 | number of sectors of the run (= ceil((256 + length) / 4096), at most 11) |
| 8..11 | stored length (LE) |
| 12..15 | CRC-32 of the stored stream |
| 16..19 | serial |

The directory is rebuilt from the headers at start (the run of a valid header is skipped, so data that merely looks like a header is not taken for one).

## 4. Frame and compression

Frame: 480 lines x 44 bytes (176 pixels, 4 per byte, first pixel in bits 7..6), **OpenDisplay colour codes: black 0, white 1, yellow 2, red 3**. The panel codes, line order and pixel order are applied **when drawing** (`4D`), so they can change without uploading again; the page sends the picture in natural order and the tag reverses the pixels of each line at draw time when `mode` bit 1 is set (needed on this panel, see `docs/USER_GUIDE.md`).

Formats 1 and 2 use the **plain LZ4 block format** (token, literals, 16-bit offset, match length, **no trailing empty token**) with **offsets up to 2048**, so the decoder needs a 2 KiB history and one 44-byte line and runs while the line goes to the panel. Format 2 first XORs every line with the line above (line 0 unchanged), decoding XORs back on the fly. Line reversal (`mode` bit 0) is not applied to compressed slots (the lines are decoded in order). Measured sizes: white frame 87 bytes, flat logo 117, text-like 22 %, noisy dithered gradient 92 %.

**Two planes (formats 3, 4, 5, since 0.9d).** The stored stream is **960 lines** of 44 bytes: lines 0..479 are **plane 0**, lines 480..959 **plane 1**. Both hold **panel codes** (2 bits per pixel, the same pixel packing), **not** OpenDisplay codes: the colour table `lut` is not used. The tag draws in two passes: pass 0 sends plane 0 with the long waveform record, then (about 4 s after the panel was powered down) pass 1 sends plane 1 with the short record (`docs/HARDWARE.md` section 7a). Format 5 XORs every line with the line above **within its plane** (line 0 and line 480 are unchanged). Orientation (`4D mode`) applies to both planes; line reversal is not applied to compressed slots. Pixel codes per colour (pass 0 / pass 1): white 1 / 1, yellow 2 / 1, orange 0 / 1, dark red 3 / 1, black 1 / 0, grey 1 / 2, dark grey 1 / 3 (the grey and black values were measured only over white; pass 1 code 1 changes nothing).

**Four-colour slots (formats 0..2) in 0.9d.** With the default `lut` = `27` they are drawn in two passes as well: the colour table of pass 0 is `0xE5` (black and white 1, yellow 2, red 3) and of pass 1 `0x54` (black 0, others 1); pass 1 is skipped for a solid fill that is not black. Panel code 0 (orange) is not used by the four-colour formats.

## 5. OpenDisplay subset

Messages start with `00` and a command byte; the replies are `status cmd data`.

| Message | Answer |
|---|---|
| `00 40` | configuration: 176 x 480, four colours (black, white, red, yellow), rotation 0, no encryption; packets 1, 2, 4 and 32 are answered |
| `00 43` | firmware version (major 1, minor 0, length-prefixed build string `n437-437-0.9d`) |
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
