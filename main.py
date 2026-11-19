"""News-image entry for make.fun: copy the front page to the output folder.

The repository holds the finished front page as ``entry.png`` (a 1024x1024
PNG summing up Thursday 19 November 2026). This script is the entrypoint:
it sanity-checks the file, then copies it to ``$MAKEFUN_OUTPUT_DIR`` (or
``/output`` when the variable is unset).

Checks performed before any copy:
  * the file is a whole PNG (signature, per-chunk CRCs, IEND last, nothing
    after IEND) or a whole JPEG (SOI first, EOI last);
  * for a PNG, the IHDR dimensions are at most 1024 on each side;
  * the file is at most 1 MiB.

The program is deterministic: fixed input, no clock, no randomness, no
network, so two runs write identical bytes. A broken image raises instead
of producing a zero-scoring output.
"""

import os
import shutil
import struct
import sys
import zlib
from pathlib import Path

MAX_BYTES = 1_048_576
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class BadImage(ValueError):
    """Raised when the entry image fails a wholeness check."""


def _u32be(buf, off):
    return struct.unpack_from(">I", buf, off)[0]


def validate_png(blob):
    """Walk every PNG chunk, checking lengths, CRCs and the IEND trailer."""
    if not blob.startswith(PNG_MAGIC):
        raise BadImage("missing PNG signature")
    width = height = None
    pos = len(PNG_MAGIC)
    while True:
        if pos + 8 > len(blob):
            raise BadImage("chunk header runs past end of file")
        size = _u32be(blob, pos)
        tag = bytes(blob[pos + 4:pos + 8])
        body_end = pos + 8 + size
        if body_end + 4 > len(blob):
            raise BadImage("chunk body runs past end of file")
        expect = zlib.crc32(bytes(blob[pos + 4:body_end])) & 0xFFFFFFFF
        if _u32be(blob, body_end) != expect:
            raise BadImage("CRC mismatch in chunk %r" % tag)
        if tag == b"IHDR":
            width = _u32be(blob, pos + 8)
            height = _u32be(blob, pos + 12)
        pos = body_end + 4
        if tag == b"IEND":
            break
    if pos != len(blob):
        raise BadImage("trailing bytes after IEND")
    if width is None or height is None:
        raise BadImage("PNG has no IHDR chunk")
    if width > MAX_SIDE or height > MAX_SIDE:
        raise BadImage("image is %dx%d, over the 1024 limit" % (width, height))


def validate_jpeg(blob):
    """A whole JPEG starts with SOI and ends with EOI, nothing else."""
    if len(blob) < 4 or blob[:2] != b"\xff\xd8" or blob[-2:] != b"\xff\xd9":
        raise BadImage("not a whole JPEG: needs SOI first and EOI last")


def validate_image(blob):
    """Dispatch on magic bytes and enforce the 1 MiB size cap."""
    if len(blob) > MAX_BYTES:
        raise BadImage("image is %d bytes, over the 1 MiB limit" % len(blob))
    if blob.startswith(PNG_MAGIC):
        validate_png(blob)
    elif blob[:2] == b"\xff\xd8":
        validate_jpeg(blob)
    else:
        raise BadImage("entry image is neither PNG nor JPEG")


def run():
    here = Path(__file__).resolve().parent
    blob = (here / "entry.png").read_bytes()
    validate_image(blob)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(here / "entry.png", target)
    print("wrote %s (%d bytes)" % (target, len(blob)))
    return 0


if __name__ == "__main__":
    sys.exit(run())
