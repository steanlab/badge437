# tools/

Repo path: `steanlab/badge437` (public) → `tools/`.

## `nebular_debug_custom.py`

The command-line flasher used for the first installation (see [`docs/USER_GUIDE.md`](../docs/USER_GUIDE.md) sections 0 and 1; Russian: [`docs/USER_GUIDE.ru.md`](../docs/USER_GUIDE.ru.md)).

* **Author: Gerard780**, the author of the Hanshow RP2040 bridge ([github.com/gerard780/hanshow-rp2040-programmer](https://github.com/gerard780/hanshow-rp2040-programmer), MIT licence). The file is included **unchanged** so that this project can be flashed without hunting for it. It is **not** covered by the licence of this repository (see [`NOTICE.md`](../NOTICE.md)); the file itself carries no licence text, so ask its author for terms beyond using it as described here.
* SHA-256: `d8f17e80237c2b03654f3a4e940c1066ce51ba87b3eb110f7b7e8703d8143ed8`
* Needs Python 3.9 or newer and `pyserial`, `pyusb`, `libusb-package` (`pip install pyserial pyusb libusb-package`). On its first run it downloads four helper modules from the bridge repository at a pinned commit and checks their SHA-256 before use, so the computer needs Internet access once.
* Models: `--model 437` (this tag) and `--model 970`. Without `--apply` it only backs up and plans.
* Run `python3 tools/nebular_debug_custom.py --help` for all options.
