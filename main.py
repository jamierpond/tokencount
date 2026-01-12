import argparse
import json
import sys

import tiktoken

DEFAULT_ENCODING = "o200k_base"


def count_tokens(text: str, encoding: str) -> int:
    enc = tiktoken.get_encoding(encoding)
    return len(enc.encode(text))


def count_lines(text: str) -> int:
    return text.count("\n") + (1 if text and not text.endswith("\n") else 0)


def count_chars(text: str) -> int:
    return len(text)


class FileStats:
    def __init__(self, name: str, tokens: int, lines: int, chars: int):
        self.name = name
        self.tokens = tokens
        self.lines = lines
        self.chars = chars


def format_number(n: int) -> str:
    return f"{n:,}"


def print_pretty_output(
    sorted_counts: list[tuple[str, int]], total: int, encoding: str
) -> None:
    total_formatted = format_number(total)
    token_width = len(total_formatted)

    print(file=sys.stderr)
    if len(sorted_counts) > 1:
        max_name = max(len(name) for name, _ in sorted_counts)
        total_line = f"{total_formatted}  total ({encoding})"
        content_width = max(token_width + 2 + max_name, len(total_line))

        print(f"  ┌─{'─' * content_width}─┐", file=sys.stderr)
        for name, count in sorted_counts:
            line = f"{format_number(count):>{token_width}}  {name}"
            print(f"  │ {line:<{content_width}} │", file=sys.stderr)
        print(f"  ├─{'─' * content_width}─┤", file=sys.stderr)
        print(f"  │ {total_line:<{content_width}} │", file=sys.stderr)
        print(f"  └─{'─' * content_width}─┘", file=sys.stderr)
    else:
        name = sorted_counts[0][0] if sorted_counts[0][0] != "<stdin>" else "stdin"
        label = f"{total_formatted} tokens ({encoding})"
        box_width = max(len(label) + 2, len(name) + 2)

        print(f"  ┌{'─' * box_width}┐", file=sys.stderr)
        print(f"  │ {name:<{box_width - 2}} │", file=sys.stderr)
        print(f"  ├{'─' * box_width}┤", file=sys.stderr)
        print(f"  │ {label:<{box_width - 2}} │", file=sys.stderr)
        print(f"  └{'─' * box_width}┘", file=sys.stderr)
    print(file=sys.stderr)

    print(total)


def print_json_output(
    sorted_counts: list[tuple[str, int]], total: int, encoding: str
) -> None:
    output = {
        "encoding": encoding,
        "files": [{"name": name, "tokens": count} for name, count in sorted_counts],
        "total": total,
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

    file_counts: list[tuple[str, int]] = []

    if args.files:
        for filepath in args.files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                tokens = count_tokens(content, args.encoding)
                file_counts.append((filepath, tokens))
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
        tokens = count_tokens(content, args.encoding)
        file_counts.append(("<stdin>", tokens))

    sorted_counts = sorted(file_counts, key=lambda x: x[1])
    total = sum(count for _, count in sorted_counts)

    if args.json:
        print_json_output(sorted_counts, total, args.encoding)
    else:
        print_pretty_output(sorted_counts, total, args.encoding)


if __name__ == "__main__":
    main()
