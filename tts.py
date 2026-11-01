#!/usr/bin/env python3
"""Text-to-speech only tool.

Usage:
    python tts.py --text "Xin chao" --output hello.mp3
    python tts.py --file script.txt --voice vi-VN-NamMinhNeural --rate +10% --output out.mp3
    python tts.py --list-voices

Requires: pip install edge-tts
No API key needed. Uses Microsoft Edge TTS voices (online).
"""
import argparse
import asyncio
import re
import sys

from voices import ALL_VOICES, EDGE_VOICES

DEFAULT_VOICE = "vi-VN-HoaiMyNeural"
VOICES = {voice: voice for group in ALL_VOICES.values() for voice in group}


def split_text(text, max_chars=600):
    # Light default: smaller chunks use less RAM and recover better on failure.
    """Split long text into sentence chunks so no request is too long."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 > max_chars and current:
            chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip() if current else sentence
    if current:
        chunks.append(current)
    return chunks


async def _speak(text, voice, rate, pitch, volume, output):
    import edge_tts

    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
    await communicate.save(output)


CHUNK_CHARS = 600

async def synthesize(text, voice, rate, pitch, volume, output, chunk_chars=None):
    if voice.startswith("vieneu:") or voice.startswith("omnivoice:"):
        raise RuntimeError(
            f"Giong {voice} can goi tai nguyen HaizFlow (VieNeu/OmniVoice model + SDK), "
            "khong chay duoc chi bang pip. Hay chon giong Edge de chay ngay, "
            "hoac chi duong dan goi tai nguyen HaizFlow tren may Windows cua ban."
        )
    chunks = split_text(text, max_chars=chunk_chars or CHUNK_CHARS)
    if not chunks:
        raise ValueError("Text rong, khong co gi de doc.")
    if len(chunks) == 1:
        await _speak(chunks[0], voice, rate, pitch, volume, output)
        return
    # Long text: synthesize each chunk, then join with ffmpeg if available,
    # otherwise keep the first chunk and warn in the caller.
    import subprocess
    import tempfile
    from pathlib import Path

    tmpdir = Path(tempfile.mkdtemp(prefix="tts_"))
    parts = []
    for i, chunk in enumerate(chunks):
        part = tmpdir / f"part{i:03d}.mp3"
        await _speak(chunk, voice, rate, pitch, volume, str(part))
        parts.append(str(part))
    concat = tmpdir / "list.txt"
    concat.write_text("".join(f"file '{p}'\n" for p in parts), encoding="utf-8")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", output],
        check=True,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Text-to-speech only tool")
    parser.add_argument("--text", help="Text can doc truc tiep")
    parser.add_argument("--file", help="File .txt chua text can doc")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"Giong doc (mac dinh: {DEFAULT_VOICE})")
    parser.add_argument("--rate", default="+0%", help="Toc do, vi du: -20%%, +0%%, +30%%")
    parser.add_argument("--pitch", default="+0Hz", help="Cao do, vi du: -10Hz, +0Hz, +10Hz")
    parser.add_argument("--volume", default="+0%", help="Am luong, vi du: -20%%, +0%%, +20%%")
    parser.add_argument("--output", default="output.mp3", help="File mp3 dau ra")
    parser.add_argument("--mode", default="light", choices=["light", "balanced", "quality"],
                        help="light: chunk nho, it RAM. balanced: chunk 900. quality: chunk 1200.")
    parser.add_argument("--list-voices", action="store_true", help="Liet ke giong goi y")
    args = parser.parse_args(argv)

    if args.list_voices:
        for provider, voices in ALL_VOICES.items():
            print(f"[{provider}] ({len(voices)} giong)")
            for voice in voices:
                print(f"  {voice}")
        return 0

    if args.file:
        text = open(args.file, encoding="utf-8").read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    # Edge TTS is imported lazily inside synthesize, so --help and the GUI
    # start fast on a weak machine with no heavy model loaded.
    asyncio.run(synthesize(text, args.voice, args.rate, args.pitch, args.volume, args.output))
    print(f"Done: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
