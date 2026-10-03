"""Lightweight CLI helpers; importing these never loads model weights."""
import argparse
import hashlib
from pathlib import Path


def str2bool(value):
    if isinstance(value, bool):
        return value
    normalized = value.lower()
    if normalized in {"true", "1", "yes", "y", "t"}:
        return True
    if normalized in {"false", "0", "no", "n", "f"}:
        return False
    raise argparse.ArgumentTypeError("expected true/false or 1/0")


def audio_identity(path):
    """Keep the full stem and disambiguate equal filenames from different dirs."""
    path = Path(path)
    digest = hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest()[:12]
    return f"{path.stem[:80]}_{digest}"
