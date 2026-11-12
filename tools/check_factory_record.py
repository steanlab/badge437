#!/usr/bin/env python3
"""Check the factory record of a Nebular 437Q-N flash backup.

Usage:  python3 tools/check_factory_record.py nebular-debug-*/before-1.bin

Read-only. The record (92 bytes at flash address 0x7E000) is the same on every tag of a variant;
it holds no serial number or address, so printing differing bytes is safe.
Exit code: 0 = a 437Q-N record (known or a new variant), 1 = not a 437Q-N record, 2 = unusable file.
Covered by the licence of this repository (steanlab/badge437)."""
import sys

OFF, LEN, FLASH = 0x7E000, 92, 0x80000

# Revision A: the record the stock flasher script accepts (4 of our 5 tags).
A = bytes.fromhex(
    "61d70c0c210301000000000000020b000e00b000e001b501750018100000000000000000"
    "000000000000000087040a2b611040001000000f000f00000000ee020a00f21d8a230000"
    "0000000000000000000000000000000000000000")
# Revision B: the same record with bytes +00 = 9C, +01 = 2F and +46 = 03 (1 of our 5 tags).
B = bytes({0: 0x9C, 1: 0x2F, 46: 0x03}.get(i, b) for i, b in enumerate(A))
assert len(A) == LEN and len(B) == LEN


def is_437(rec):
    """Panel 176 x 480, diagonal 437 at +0x12..+0x17 and model code 2B at +0x2F."""
    return rec[0x12:0x18] == bytes.fromhex("b000e001b501") and rec[0x2F] == 0x2B


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    data = open(sys.argv[1], "rb").read()
    if len(data) != FLASH:
        print("This is not a full 512 KiB flash backup (%d bytes)." % len(data))
        return 2
    rec = data[OFF:OFF + LEN]
    if rec == A:
        print("factory record: revision A (known). The stock script accepts it.")
        return 0
    if is_437(rec):
        print("factory record: a 437Q-N record that the stock script refuses.")
        if rec == B:
            print("It is revision B (known): bytes +00, +01 and +46 differ from A; flashes and draws normally.")
        else:
            diff = [i for i in range(LEN) if rec[i] != A[i]]
            print("It is a new variant: %d byte(s) differ from revision A:" % len(diff))
            for i in diff:
                print("  offset +%02d: revision A has %02x, this tag has %02x" % (i, A[i], rec[i]))
            print("Please open an issue with this output so that it can be listed.")
        print("Next step: python3 tools/make_tolerant_script.py tools/nebular_debug_custom.py")
        print("and use the new tools/nebular_debug_tolerant.py in place of nebular_debug_custom.py.")
        return 0
    print("factory record: NOT a 437Q-N record (panel size, diagonal or model code differ).")
    print("Do not flash. Open an issue and paste this output.")
    print("  size/diagonal at +0x12..+0x17: %s   model code at +0x2F: %02x (437Q-N: 2b)"
          % (rec[0x12:0x18].hex(" "), rec[0x2F]))
    return 1


if __name__ == "__main__":
    sys.exit(main())
