import argparse
import json
import sys
from dataclasses import dataclass
from importlib.metadata import version

import tiktoken

__version__ = version("tokencount")
DEFAULT_ENCODING = "o200k_base"


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


def format_number(n: int) -> str:
    return f"{n:,}"


def print_pretty_output(
    sorted_stats: list[FileStats], total_tokens: int, encoding: str
) -> None:
    total_lines = sum(s.lines for s in sorted_stats)
    total_chars = sum(s.chars for s in sorted_stats)

    tok_w = max(len(format_number(total_tokens)), 3)
    line_w = max(len(format_number(total_lines)), 3)
    char_w = max(len(format_number(total_chars)), 3)

    print(file=sys.stderr)
    for s in sorted_stats:
        name = s.name if s.name != "<stdin>" else "stdin"
        print(
            f"  {format_number(s.lines):>{line_w}}L  "
            f"{format_number(s.chars):>{char_w}}C  "
            f"{format_number(s.tokens):>{tok_w}}T  {name}",
            file=sys.stderr,
        )

    if len(sorted_stats) > 1:
        print(
            f"  {'-' * line_w}-  {'-' * char_w}-  {'-' * tok_w}-",
            file=sys.stderr,
        )
        print(
            f"  {format_number(total_lines):>{line_w}}L  "
            f"{format_number(total_chars):>{char_w}}C  "
            f"{format_number(total_tokens):>{tok_w}}T  total ({encoding})",
            file=sys.stderr,
        )
    else:
        print(f"  ({encoding})", file=sys.stderr)
    print(file=sys.stderr)

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
        print(f"tc: unknown encoding: {args.encoding}", file=sys.stderr)
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
                print(f"tc: {filepath}: No such file or directory", file=sys.stderr)
                sys.exit(1)
            except IsADirectoryError:
                print(f"tc: {filepath}: Is a directory", file=sys.stderr)
                sys.exit(1)
    else:
        if sys.stdin.isatty():
            parser.print_help()
            sys.exit(0)
        content = sys.stdin.read()
        stats = FileStats(
            name="<stdin>",
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
