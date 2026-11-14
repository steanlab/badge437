#!/usr/bin/env python3
"""Make a local copy of the flasher script that can (1) accept the flash chip id 68 10 13 and (2) write a panel-data block from another tag.

Usage:  python3 tools/make_donor_script.py tools/nebular_debug_custom.py        (or tools/nebular_debug_tolerant.py)
Writes tools/nebular_debug_donor.py next to it; the source file is not changed.

(1) Some 437 tags carry a flash chip whose JEDEC id is 681013 instead of eb6013 (the stock flasher: "Flash does not match --model 437").
    The copy accepts both ids and prints the id it read ("flash id read: ..."). Its other checks (two identical full backups, protection
    status, whole-flash verification and rollback) stay; a chip that reads unreliably is still refused ("The two full backups differ").
    It also prints how many bytes differ when the two backups differ.
(2) A tag whose waveform block was damaged (see docs/USER_GUIDE.md section 8) cannot draw. Give the copy a good full backup of ANOTHER 437 tag in
    the environment variable WF_DONOR and it writes that tag's 12 KiB block (0x78000..0x7AFFF) together with the firmware:
        WF_DONOR=nebular-debug-.../before-1.bin python3 tools/nebular_debug_donor.py --model 437 --custom-firmware n437_0.9k.bin --no-questions --seconds 5 [--apply]
    The donor block must pass its own CRC16 (check_waveform.py says OK) and the firmware must not reach 0x78000. Without WF_DONOR nothing
    extra is written. To allow the writes the copy raises the address limit of the flasher's flash backend at run time (the backend file is not
    modified); only the sectors of the plan are written, the whole flash is verified afterwards and a failed write is rolled back from the backup.
Pick the donor whose block differs least from your tag's (the intact parts of the damaged block help: compare, do not guess). The colours of a block taken from
another tag can differ a little; the first tag repaired this way (2026-11-14) draws again.
Do not redistribute the copy: nebular_debug_custom.py is Gerard780's work (see NOTICE.md).
This helper is covered by the licence of this repository (steanlab/badge437)."""
import pathlib
import re
import sys

if len(sys.argv) != 2:
    sys.exit(__doc__)
src = pathlib.Path(sys.argv[1])
dst = src.with_name("nebular_debug_donor.py")
s = src.read_text()


def once(old, new):
    global s
    if s.count(old) != 1:
        sys.exit("anchor not found exactly once, nothing written: " + old[:70])
    s = s.replace(old, new)


pat = re.compile(r'^(\s*)require\(flash\.spi\(\[0x9f\], 3\) == bytes\.fromhex\(profile\["jedec"\]\), "Flash does not match --model " \+ model\)$', re.M)
if len(pat.findall(s)) != 1:
    sys.exit("flash id check not found exactly once, nothing written")
s = pat.sub(lambda m: m.group(1) + '_j = flash.spi([0x9f], 3); require(_j in (bytes.fromhex(profile["jedec"]), bytes.fromhex("681013")), '
            '"Flash does not match --model " + model + ": read " + _j.hex()); print("flash id read:", _j.hex())', s)
once('require(before == second, "The two full backups differ; writes refused")',
     '_d = [i for i in range(len(before)) if before[i] != second[i]] if len(before) == len(second) else []; '
     'print("backups differ: %d bytes; first offsets: %s" % (len(_d), [hex(x) for x in _d[:12]])) if _d else None; '
     'require(before == second, "The two full backups differ; writes refused")')
once("    import benchmark_readback as bench\n",
     "    import benchmark_readback as bench\n    import flash_backend as _fb\n    _fb.APPLICATION_LIMIT = 0x7b000  # tools/make_donor_script.py: allow the panel-data block\n")
once("    expected = padded + before[len(padded):]\n", '''    expected = padded + before[len(padded):]
    wf_sectors = []
    _donor = os.environ.get("WF_DONOR")
    if _donor:
        _d = open(_donor, "rb").read()
        require(len(_d) == 0x80000 and model == "437", "WF_DONOR must be a 512 KiB full backup (437)")
        _b = _d[0x78000:0x7b000]
        _c = 0x1D0F
        for _x in _b[2:]:
            _c ^= _x << 8
            for _ in range(8):
                _c = ((_c << 1) ^ 0x1021) & 0xFFFF if _c & 0x8000 else (_c << 1) & 0xFFFF
        require(_c == _b[0] | _b[1] << 8, "Donor panel-data block fails its CRC16")
        require(len(padded) <= 0x78000, "Firmware overlaps the panel-data block")
        expected = expected[:0x78000] + _b + expected[0x7b000:]
        wf_sectors = [0x78000, 0x79000, 0x7a000]
        print("panel-data donor block: CRC16 %04X from %s" % (_c, _donor))
''')
once("for offset in list(range(SECTOR, len(padded), SECTOR)) + [0]\n", "for offset in list(range(SECTOR, len(padded), SECTOR)) + wf_sectors + [0]\n")
if not re.search(r"^import os$", s, re.M):
    sys.exit("no 'import os' in the script, nothing written")
dst.write_text(s)
print("written", dst)
