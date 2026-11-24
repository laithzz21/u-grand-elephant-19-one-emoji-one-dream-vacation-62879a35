#!/usr/bin/env python3
"""One Emoji, One Dream Vacation — make.fun entry.

The entry is exactly one emoji: a desert island. No words, no spaces,
no punctuation, no extra characters. A desert island is the dream
vacation in a single picture: white sand, palm shade, turquoise water,
and nowhere to be. Everything else is just the journey there.

This script validates the entry before printing it, prints exactly
that one emoji to stdout, and writes it to the output file so the
entry can be checked by reading it back.
"""

import os
import sys
import unicodedata

# The entry: exactly one emoji — a desert island (U+1F3DD + VS16).
ENTRY = "\U0001F3DD\uFE0F"

# Fallback if ENTRY were ever blanked by mistake: the same island,
# written out plainly so the script can never print an empty entry.
# Validation still runs on whichever value is used.
FALLBACK_ENTRY = "🏝️"

# Characters that do not create a new grapheme: variation selectors,
# skin-tone modifiers, and the zero-width joiner.
_NON_GRAPHEME = frozenset(
    [
        "\uFE0E",  # variation selector-15 (text presentation)
        "\uFE0F",  # variation selector-16 (emoji presentation)
        "\u200D",  # zero-width joiner
        "\U0001F3FB",  # light skin tone
        "\U0001F3FC",  # medium-light skin tone
        "\U0001F3FD",  # medium skin tone
        "\U0001F3FE",  # medium-dark skin tone
        "\U0001F3FF",  # dark skin tone
    ]
)


def grapheme_count(text):
    """Count grapheme clusters, treating VS16 / ZWJ / modifiers as part
    of the emoji they follow instead of as characters of their own."""
    count = 0
    for char in text:
        if char in _NON_GRAPHEME:
            continue
        count += 1
    return count


def is_single_emoji(text):
    """Return True only if text is exactly one emoji and nothing else."""
    if not text:
        return False
    if grapheme_count(text) != 1:
        return False
    if any(char.isspace() for char in text):
        return False
    # Every base character must be a symbol (emoji live in So), not a
    # letter, digit, or punctuation mark.
    for char in text:
        if char in _NON_GRAPHEME:
            continue
        if unicodedata.category(char) != "So":
            return False
    return True


def validate(entry):
    """Raise SystemExit with a message on stderr if the entry is invalid."""
    if not is_single_emoji(entry):
        print(
            "error: entry must be exactly one emoji, got %r" % (entry,),
            file=sys.stderr,
        )
        raise SystemExit(1)
    # Belt and braces: no letters, digits, or punctuation may hide in
    # the entry, and stripping the presentation selector must still
    # leave exactly one base emoji character behind.
    base = "".join(char for char in entry if char not in _NON_GRAPHEME)
    if len(base) != 1:
        print(
            "error: entry must have exactly one base emoji, got %r" % (base,),
            file=sys.stderr,
        )
        raise SystemExit(1)
    if any(char.isalnum() or char in ".,!?;:'\"-" for char in entry):
        print("error: entry must contain no words or punctuation", file=sys.stderr)
        raise SystemExit(1)


def output_path():
    """Resolve where entry.txt goes: $MAKEFUN_OUTPUT, else /output,
    else ./output next to this script."""
    env_path = os.environ.get("MAKEFUN_OUTPUT")
    if env_path:
        return os.path.join(env_path, "entry.txt")
    if os.path.isdir("/output") and os.access("/output", os.W_OK):
        return "/output/entry.txt"
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "output", "entry.txt")


def main():
    # Use the fallback if ENTRY is ever empty; validation then checks
    # whichever value was chosen, so a bad fallback still fails loudly
    # instead of printing something that is not one emoji.
    entry = ENTRY or FALLBACK_ENTRY
    validate(entry)

    # Print exactly the one emoji, nothing else. print() adds the
    # trailing newline; the emoji itself is the whole entry.
    print(entry)

    # Also write the entry to a file and read it back to verify it.
    path = output_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(entry)
        with open(path, "r", encoding="utf-8") as handle:
            written = handle.read()
        if written != entry:
            print(
                "warning: read-back mismatch in %s" % (path,),
                file=sys.stderr,
            )
    except OSError as exc:
        print("warning: could not write %s: %s" % (path, exc), file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
