#!/usr/bin/env python3
"""Check the waveform block of a Hanshow Nebular Pro 437Q-N in a full flash backup (512 KiB).

Repo path: steanlab/badge437 (public) -> tools/check_waveform.py.  Licence: see ../LICENSE.md.

The panel data of the tag sits in the flash at 0x78000..0x7AFFF (12 KiB). Its first two bytes hold a CRC16 (poly 0x1021, init 0x1D0F, MSB first)
of the remaining bytes, little endian. The firmware of this project refuses to draw when the check fails; other firmwares (for example builds
based on ATC_BLE_OEPL) may have overwritten part of the block. Run this on the backup you made BEFORE flashing:

    python3 tools/check_waveform.py backup.bin [more.bin ...]

Exit status 0 = block valid in every file, 1 = a block is bad, 2 = a file is not a 512 KiB backup.
Prints only the check result; it does not print or copy the block.
"""
import sys

BASE, LEN = 0x78000, 0x3000


def crc16(data):
    crc = 0x1D0F
    for x in data:
        crc ^= x << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def main(files):
    if not files:
        print(__doc__)
        return 2
    status = 0
    for f in files:
        d = open(f, "rb").read()
        if len(d) != 0x80000:
            print(f"{f}: {len(d)} bytes, not a 512 KiB backup of the whole flash")
            status = max(status, 2)
            continue
        blk = d[BASE:BASE + LEN]
        stored, calc = blk[0] | blk[1] << 8, crc16(blk[2:])
        if stored == calc:
            print(f"{f}: waveform block OK (CRC16 {calc:04X})")
        else:
            parts = ["blank" if blk[i:i + 0x400] == b"\xff" * 0x400 else "data" for i in range(0, LEN, 0x400)]
            print(f"{f}: waveform block BAD (stored {stored:04X}, calculated {calc:04X}); 1 KiB parts from 0x78000: {' '.join(parts)}")
            print("  Do not rely on this tag: the firmware cannot draw. See docs/USER_GUIDE.md section 8 (damaged waveform block).")
            status = max(status, 1)
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
