import argparse
import json
import sys

import tiktoken

DEFAULT_ENCODING = "o200k_base"


def count_tokens(text: str, encoding: str) -> int:
    enc = tiktoken.get_encoding(encoding)
    return len(enc.encode(text))


def format_number(n: int) -> str:
    return f"{n:,}"


def print_pretty_output(
    sorted_counts: list[tuple[str, int]], total: int, encoding: str
) -> None:
    if len(sorted_counts) > 1:
        max_tokens = max(count for _, count in sorted_counts)
        token_width = len(format_number(max_tokens))
        max_name = max(len(name) for name, _ in sorted_counts)

        print("\n### Token counts:", file=sys.stderr)
        for name, count in sorted_counts:
            print(f"  {format_number(count):>{token_width}}  {name}", file=sys.stderr)
        print("-" * (token_width + max_name + 4), file=sys.stderr)
        print(
            f"  {format_number(total):>{token_width}}  total ({encoding})",
            file=sys.stderr,
        )
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
