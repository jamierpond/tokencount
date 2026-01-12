# tc

Token counter CLI. Like `wc` but for LLM tokens.

## Quick Install

```bash
uv tool install git+https://github.com/jamierpond/tokencount
```

## Install from source

```bash
uv tool install .
# or for live edits during dev:
uv tool install --editable .
```

## Usage

```bash
tc file.txt                    # single file
tc *.py                        # multiple files
cat file.txt | tc              # stdin
tc -e cl100k_base file.txt     # different encoding
tc --json file.txt             # JSON output
```

## Output

```
   23L    301C     85T  Makefile
  138L  3,941C    866T  test_main.py
  172L  4,727C  1,098T  main.py
  ----  ------  ------
  333L  8,969C  2,049T  total (o200k_base)

2049
```

L = lines, C = chars, T = tokens

Sorted by token count (smallest first). Total on stdout for piping.

## Encodings

- `o200k_base` (default) - GPT-4o
- `cl100k_base` - GPT-4, GPT-3.5-turbo
- `p50k_base` - older GPT-3
