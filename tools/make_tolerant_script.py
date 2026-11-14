#!/usr/bin/env python3
"""Make a local copy of the flasher script that accepts any 437 tag factory record.

Usage:  python3 tools/make_tolerant_script.py tools/nebular_debug_custom.py
Writes tools/nebular_debug_tolerant.py next to it; the original file is not changed.

Why: the flasher compares the 92-byte factory record of the tag (flash 0x7E000) byte for byte with
one known record and refuses ("Factory record does not match this 437Q-N revision; no writes")
every other. Some 437 tags have a slightly different record (see docs/HARDWARE.md, "Record
revisions"); the firmware of this project does not read the record, and such a tag flashes and
draws like any other. The copy accepts the known record OR any record that says "437 tag":
panel 176 x 480, diagonal 437 (bytes +0x12..+0x17 = B0 00 E0 01 B5 01) and model code 2B at +0x2F.
That is what the record is for (telling the models apart); for --model 970 nothing changes.
Every other check of the flasher (flash id, protection status, whole-flash verification,
rollback) is untouched. Run tools/check_factory_record.py first.
Do not redistribute the copy: nebular_debug_custom.py is Gerard780's work (see NOTICE.md).
This helper is covered by the licence of this repository (steanlab/badge437)."""
import pathlib
import sys

OLD = 'require(before[offset:offset + 92] == profile["product"],'
NEW = ('require(before[offset:offset + 92] == profile["product"] '
       'or (model == "437" and is_437_record(before[offset:offset + 92])),')
ADD = '''
def is_437_record(rec):
    """Tolerant rule added by tools/make_tolerant_script.py: the record says 437 tag."""
    return (len(rec) == 92 and rec[0x12:0x18] == bytes.fromhex("b000e001b501")
            and rec[0x2F] == 0x2B)

'''


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    src = pathlib.Path(sys.argv[1])
    text = src.read_text()
    if text.count(OLD) != 1 or text.count("\nMODELS = {") != 1:
        print("This is not the expected version of the script; nothing written.")
        return 1
    out = src.with_name("nebular_debug_tolerant.py")
    out.write_text(text.replace(OLD, NEW).replace("\nMODELS = {", ADD + "\nMODELS = {", 1))
    print("written", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
