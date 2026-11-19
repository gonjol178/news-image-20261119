"""make.fun news-image-20261119 entry: "The World in One Day".

The entry is one image, entry.png beside this file: a newspaper front
page summing up the world news of Thursday 19 November 2026
(build_frontpage.py is the renderer that composed it from the three
editorial panels in assets/ -- the Shenzhen trilateral, the ICJ's
Myanmar genocide ruling and the Kerch Bridge strike -- with every
headline set in type by the renderer so no text can garble). This
program copies that image to <output>/entry.png.

The output directory is $MAKEFUN_OUTPUT_DIR when set, else /output.
The image is a fixed file, so the program runs twice and writes
identical bytes: no randomness, no clock, no input, no network.

Before writing, the program checks the image is whole, the way the
gate requires: for a PNG, the signature, every chunk's length and CRC,
and a final IEND with nothing after it; for a JPEG, the SOI marker
through the EOI marker. A damaged image raises instead of being copied
into a 0 score.
"""

import os
import struct
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def check_png(data: bytes) -> None:
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG")
    pos = len(PNG_SIGNATURE)
    while True:
        if pos + 8 > len(data):
            raise ValueError("truncated PNG: chunk header runs past the end")
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        tag = data[pos + 4:pos + 8]
        end = pos + 8 + length + 4
        if end > len(data):
            raise ValueError("truncated PNG: chunk body runs past the end")
        stored_crc = struct.unpack(">I", data[pos + 8 + length:end])[0]
        if zlib.crc32(data[pos + 4:pos + 8 + length]) & 0xFFFFFFFF != stored_crc:
            raise ValueError(f"bad CRC in chunk {tag!r}")
        pos = end
        if tag == b"IEND":
            break
    if pos != len(data):
        raise ValueError("trailing bytes after IEND")


def check_jpeg(data: bytes) -> None:
    if len(data) < 4 or data[:2] != b"\xff\xd8" or data[-2:] != b"\xff\xd9":
        raise ValueError("not a whole JPEG: needs SOI first and EOI last")


def check_whole_image(data: bytes) -> None:
    if data.startswith(PNG_SIGNATURE):
        check_png(data)
    elif data[:2] == b"\xff\xd8":
        check_jpeg(data)
    else:
        raise ValueError("entry image is neither PNG nor JPEG")


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    with open(src, "rb") as f:
        data = f.read()
    check_whole_image(data)
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
