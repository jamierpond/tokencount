import argparse
import sys

import tiktoken

DEFAULT_ENCODING = "o200k_base"


def count_tokens(text: str, encoding: str) -> int:
    enc = tiktoken.get_encoding(encoding)
    return len(enc.encode(text))


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

    if len(sorted_counts) > 1:
        for name, count in sorted_counts:
            print(f"{name}: {count}", file=sys.stderr)

    total = sum(count for _, count in sorted_counts)
    print(total)


if __name__ == "__main__":
    main()
