# Notice: third-party parts and trademarks

Repo path: `steanlab/badge437` (public) → `NOTICE.md`.

* **Not affiliated** with Hanshow, Telink, OpenDisplay or OpenEPaperLink. "Hanshow", "Nebular", "Telink", "OpenDisplay" and "OpenEPaperLink" belong to their owners and are used only to name the hardware and the protocol that this project works with.
* **Telink SDK.** The firmware binaries contain code of the Telink TLSR8258 SDK (Telink Semiconductor (Shanghai) Co., Ltd.). That code is **not** covered by the licence of this repository; its terms are Telink's (the SDK files carry a Telink copyright and licence header). The SDK is distributed in public by other projects; we did not receive a separate licence from Telink. **If you intend any commercial use, check the Telink terms yourself**; the licence of this repository does not give you rights to Telink's code.
* **ATC_TLSR_Paper** by Aaron Christophel (atc1441), <https://github.com/atc1441/ATC_TLSR_Paper>: the firmware is built on the build environment and the SDK copy of this project (project layout, build scripts, drivers, start-up code), which carries no licence file; the binaries may contain parts derived from it. Our own firmware sources are not published.
* **OpenDisplay.** The firmware speaks a subset of the OpenDisplay Bluetooth protocol so that its tools work with the tag; the protocol belongs to its authors.
* **Compression.** The picture compression uses the plain LZ4 block format (Yann Collet); the encoder and the decoder are our own code.
* **`tools/nebular_debug_custom.py`** is the flasher of Gerard780 (author of the Hanshow RP2040 bridge, MIT licence), included unchanged; it is not covered by this repository's licence and carries no licence text of its own.
* The page loads no third-party scripts.

No warranty; this file is not legal advice.
