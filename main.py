import argparse
import json
import sys
from dataclasses import dataclass
from importlib.metadata import version

import tiktoken
from rich.console import Console
from rich.table import Table
from rich.text import Text

__version__ = version("tokencount")
DEFAULT_ENCODING = "o200k_base"

stderr = Console(stderr=True)

# Pre-computed token counts for reference texts (o200k_base encoding)
REFERENCE_TEXTS = [
    ("Gettysburg Address", 1_938),
    ("A Modest Proposal", 8_619),
    ("The Yellow Wallpaper", 11_821),
    ("Alice in Wonderland", 40_952),
    ("Heart of Darkness", 56_203),
    ("A Study in Scarlet", 61_757),
    ("Peter Pan", 67_181),
    ("The Prince", 70_730),
    ("Treasure Island", 97_642),
    ("Frankenstein", 101_770),
    ("Tom Sawyer", 102_285),
    ("Dorian Gray", 109_503),
    ("Sherlock Holmes", 141_038),
    ("Wuthering Heights", 166_761),
    ("Pride and Prejudice", 174_412),
    ("A Tale of Two Cities", 189_576),
    ("Dracula", 216_384),
    ("Great Expectations", 254_088),
    ("Jane Eyre", 257_652),
    ("Crime and Punishment", 287_138),
    ("Moby Dick", 309_581),
    ("War and Peace", 769_845),
]


def get_reference_comparison(tokens: int) -> str | None:
    """Return a string comparing token count to closest reference text."""
    if tokens <= 0:
        return None

    # Find closest reference
    closest_name = None
    closest_count = None
    min_diff = float("inf")

    for name, count in REFERENCE_TEXTS:
        diff = abs(tokens - count)
        if diff < min_diff:
            min_diff = diff
            closest_name = name
            closest_count = count

    if closest_name and closest_count:
        pct = (tokens / closest_count) * 100
        if pct >= 100:
            return f"{pct:.0f}% of {closest_name}"
        else:
            return f"{pct:.0f}% of {closest_name}"
    return None


def count_tokens(text: str, encoding: str) -> int:
    enc = tiktoken.get_encoding(encoding)
    return len(enc.encode(text))


def count_lines(text: str) -> int:
    if not text:
        return 0
    return text.count("\n") + (1 if not text.endswith("\n") else 0)


def count_chars(text: str) -> int:
    return len(text)


@dataclass
class FileStats:
    name: str
    tokens: int
    lines: int
    chars: int


def format_size(chars: int) -> str:
    if chars >= 1_000_000:
        return f"{chars / 1_000_000:.2f} MB"
    elif chars >= 1_000:
        return f"{chars / 1_000:.2f} KB"
    return f"{chars} B"


def print_pretty_output(
    sorted_stats: list[FileStats], total_tokens: int, encoding: str
) -> None:
    total_lines = sum(s.lines for s in sorted_stats)
    total_chars = sum(s.chars for s in sorted_stats)

    stderr.print()

    if len(sorted_stats) > 1:
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column(justify="right", style="cyan")
        table.add_column(style="dim")

        for s in sorted_stats:
            table.add_row(f"{s.tokens:,}", s.name)

        stderr.print(table)
        stderr.print()

    stderr.print(f"  [dim]{total_lines:,} lines, {format_size(total_chars)}[/dim]")
    stderr.print()

    token_text = Text()
    token_text.append("  ")
    token_text.append(f"{total_tokens:,}", style="bold green")
    token_text.append(" tokens ", style="green")
    token_text.append(f"({encoding})", style="dim")
    stderr.print(token_text)

    # Show reference comparison only for default encoding
    if encoding == DEFAULT_ENCODING:
        comparison = get_reference_comparison(total_tokens)
        if comparison:
            stderr.print(f"  [dim italic]{comparison}[/dim italic]")

    stderr.print()
    print(total_tokens)


def print_json_output(
    sorted_stats: list[FileStats], total_tokens: int, encoding: str
) -> None:
    total_lines = sum(s.lines for s in sorted_stats)
    total_chars = sum(s.chars for s in sorted_stats)
    output = {
        "encoding": encoding,
        "files": [
            {
                "name": s.name,
                "lines": s.lines,
                "chars": s.chars,
                "tokens": s.tokens,
            }
            for s in sorted_stats
        ],
        "total": {
            "lines": total_lines,
            "chars": total_chars,
            "tokens": total_tokens,
        },
    }
    print(json.dumps(output, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Count tokens in files or stdin using tiktoken"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"tc {__version__}",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to count tokens in. If none provided, reads from stdin.",
    )
    parser.add_argument(
        "-e",
        "--encoding",
        default=DEFAULT_ENCODING,
        help=f"Tiktoken encoding to use (default: {DEFAULT_ENCODING})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    args = parser.parse_args()

    try:
        tiktoken.get_encoding(args.encoding)
    except ValueError:
        stderr.print(f"[red]tc: unknown encoding: {args.encoding}[/red]")
        sys.exit(1)

    file_stats: list[FileStats] = []

    if args.files:
        for filepath in args.files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                stats = FileStats(
                    name=filepath,
                    tokens=count_tokens(content, args.encoding),
                    lines=count_lines(content),
                    chars=count_chars(content),
                )
                file_stats.append(stats)
            except FileNotFoundError:
                stderr.print(f"[red]tc: {filepath}: No such file or directory[/red]")
                sys.exit(1)
            except IsADirectoryError:
                stderr.print(f"[red]tc: {filepath}: Is a directory[/red]")
                sys.exit(1)
    else:
        if sys.stdin.isatty():
            parser.print_help()
            sys.exit(0)
        content = sys.stdin.read()
        stats = FileStats(
            name="stdin",
            tokens=count_tokens(content, args.encoding),
            lines=count_lines(content),
            chars=count_chars(content),
        )
        file_stats.append(stats)

    sorted_stats = sorted(file_stats, key=lambda x: x.tokens)
    total_tokens = sum(s.tokens for s in sorted_stats)

    if args.json:
        print_json_output(sorted_stats, total_tokens, args.encoding)
    else:
        print_pretty_output(sorted_stats, total_tokens, args.encoding)


if __name__ == "__main__":
    main()
