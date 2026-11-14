# tools/

Repo path: `steanlab/badge437` (public) → `tools/`.

## `nebular_debug_custom.py`

The command-line flasher used for the first installation (see [`docs/USER_GUIDE.md`](../docs/USER_GUIDE.md) sections 0 and 1; Russian: [`docs/USER_GUIDE.ru.md`](../docs/USER_GUIDE.ru.md)).

* **Author: Gerard780**, the author of the RP2040 bridge ([github.com/gerard780/hanshow-rp2040-programmer](https://github.com/gerard780/hanshow-rp2040-programmer), MIT licence). The file is included **unchanged** so that this project can be flashed without hunting for it. It is **not** covered by the licence of this repository (see [`NOTICE.md`](../NOTICE.md)); the file itself carries no licence text, so ask its author for terms beyond using it as described here.
* SHA-256: `d8f17e80237c2b03654f3a4e940c1066ce51ba87b3eb110f7b7e8703d8143ed8`
* Needs Python 3.9 or newer and `pyserial`, `pyusb`, `libusb-package` (`pip install pyserial pyusb libusb-package`). On its first run it downloads four helper modules from the bridge repository at a pinned commit and checks their SHA-256 before use, so the computer needs Internet access once.
* Models: `--model 437` (this tag) and `--model 970`. Without `--apply` it only backs up and plans.
* Run `python3 tools/nebular_debug_custom.py --help` for all options.

## `check_waveform.py`

Checks the panel data block of a tag in a full 512 KiB flash backup (CRC16 of the block at `0x78000`). Run it on the backup before flashing: `python3 tools/check_waveform.py nebular-debug-*/before-1.bin`. It prints only OK / BAD, never the block. See `docs/USER_GUIDE.md` section 1 and section 8. Covered by the licence of this repository.

## `check_factory_record.py`

Reads the factory record (92 bytes at `0x7E000`) of a full flash backup and says: `revision A` (the one the stock flasher accepts), `a 437 record that the stock script refuses` (revision B, seen on 1 of 5 tags, or a new variant; the output lists the differing bytes, no serial number or address) or `NOT a 437 record` (do not flash). Read-only: `python3 tools/check_factory_record.py nebular-debug-*/before-1.bin`. Covered by the licence of this repository.

## `make_tolerant_script.py`

Writes `tools/nebular_debug_tolerant.py`, a local copy of `nebular_debug_custom.py` whose factory-record check also accepts any record that says 437 tag (panel 176 x 480, diagonal 437, model code `2B`); one check changed, everything else untouched, the original file is not modified, `--model 970` is unaffected. Use it after `check_factory_record.py`, in place of the original in the dry run and the flash. Do not redistribute the copy (the original is Gerard780's work). Covered by the licence of this repository.

## `make_donor_script.py`

Writes `tools/nebular_debug_donor.py`, a local copy of the flasher (the original or the tolerant copy) with two additions: it accepts the flash chip id `681013` (some tags have a different flash chip than `eb6013`; the copy prints the id it read) and, when the environment variable `WF_DONOR` names a good full backup of **another** 437 tag, it writes that tag's panel-data block (`0x78000`..`0x7AFFF`) together with the firmware. Use it for a tag whose block is damaged (`docs/USER_GUIDE.md` section 8). Dry run first, then `--apply`; the original is not modified. Do not redistribute the copy. Covered by the licence of this repository.
