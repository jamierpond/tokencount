#!/usr/bin/env python3
"""
Generate REFERENCE_TEXTS by downloading from Project Gutenberg.

Usage:
    ./count_references.py           # Download all, output to stdout
    ./count_references.py --write   # Write directly to counts.py
    ./count_references.py --table   # Output as table instead
"""

import argparse
import sys
import urllib.request
from pathlib import Path

import tiktoken

ENCODING = "o200k_base"

# (title, author, gutenberg_id)
# None for gutenberg_id means local file in extra/
SOURCES = [
    ("Hop on Pop", "Dr. Seuss", None),  # extra/hw2/hoponpop.txt
    ("Green Eggs and Ham", "Dr. Seuss", None),  # extra/hw2/greeneggsandham.txt
    ("Fox in Socks", "Dr. Seuss", None),  # extra/hw2/foxinsocks.txt
    ("One Fish Two Fish", "Dr. Seuss", None),  # extra/hw2/onefishtwofish.txt
    ("The Cat in the Hat", "Dr. Seuss", None),  # extra/hw2/catinthehat.txt
    ("The Waste Land", "T.S. Eliot", None),  # extra/texts/wasteland.txt
    ("A Modest Proposal", "Jonathan Swift", 1080),
    ("The Yellow Wallpaper", "C.P. Gilman", 1952),
    ("Alice in Wonderland", "Lewis Carroll", 11),
    ("Heart of Darkness", "Joseph Conrad", 219),
    ("A Study in Scarlet", "Arthur Conan Doyle", 244),
    ("Peter Pan", "J.M. Barrie", 16),
    ("The Prince", "Machiavelli", 1232),
    ("Treasure Island", "R.L. Stevenson", 120),
    ("Frankenstein", "Mary Shelley", 84),
    ("Tom Sawyer", "Mark Twain", 74),
    ("Dorian Gray", "Oscar Wilde", 174),
    ("Sherlock Holmes", "Arthur Conan Doyle", 1661),
    ("Wuthering Heights", "Emily Brontë", 768),
    ("Pride and Prejudice", "Jane Austen", 1342),
    ("A Tale of Two Cities", "Charles Dickens", 98),
    ("Dracula", "Bram Stoker", 345),
    ("Great Expectations", "Charles Dickens", 1400),
    ("Jane Eyre", "Charlotte Brontë", 1260),
    ("Crime and Punishment", "Fyodor Dostoevsky", 2554),
    ("Moby Dick", "Herman Melville", 2701),
    ("War and Peace", "Leo Tolstoy", 2600),
]

# Local file mappings for non-Gutenberg sources
LOCAL_FILES = {
    "Hop on Pop": "extra/hw2/hoponpop.txt",
    "Green Eggs and Ham": "extra/hw2/greeneggsandham.txt",
    "Fox in Socks": "extra/hw2/foxinsocks.txt",
    "One Fish Two Fish": "extra/hw2/onefishtwofish.txt",
    "The Cat in the Hat": "extra/hw2/catinthehat.txt",
    "The Waste Land": "extra/texts/wasteland.txt",
}


def fetch_gutenberg(book_id: int) -> str:
    """Fetch plain text from Project Gutenberg."""
    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    print(f"  Fetching {url}...", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8")


def count_tokens(text: str) -> int:
    enc = tiktoken.get_encoding(ENCODING)
    return len(enc.encode(text))


def main() -> None:
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Generate REFERENCE_TEXTS")
    parser.add_argument("--table", action="store_true", help="Output as table")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.parent
    results: list[tuple[str, str, int]] = []

    for title, author, gutenberg_id in SOURCES:
        print(f"Processing: {title}...", file=sys.stderr)
        try:
            if gutenberg_id is None:
                # Local file
                local_path = script_dir / LOCAL_FILES[title]
                text = local_path.read_text(encoding="utf-8")
            else:
                text = fetch_gutenberg(gutenberg_id)

            tokens = count_tokens(text)
            results.append((title, author, tokens))
            print(f"  -> {tokens:,} tokens", file=sys.stderr)
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)

    # Sort by token count
    results.sort(key=lambda x: x[2])

    print(file=sys.stderr)
    if args.table:
        for title, author, tokens in results:
            print(f"{tokens:>12,}  {title} by {author}")
    else:
        print("REFERENCE_TEXTS = [")
        for title, author, tokens in results:
            print(f'    ("{title}", "{author}", {tokens:_}),')
        print("]")


if __name__ == "__main__":
    main()
