# tc

Token counter CLI. Like `wc` but for LLM tokens.

```bash
git diff | tc        # before pasting into chat
tc *.py              # check project size
```

## Install

```bash
uv tool install git+https://github.com/jamierpond/tokencount
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
   475  counts.py
   878  test_main.py
 1,565  main.py

  386 lines, 11.36 KB

  2,918 tokens (o200k_base)
  Somewhere between The Cat in the Hat and The Waste Land
  139% of The Cat in the Hat, 69% of The Waste Land

2918
```

Sorted by token count. Total on stdout for piping. Warns if over 1M tokens.

## Encodings

- `o200k_base` (default) - GPT-4o, Claude
- `cl100k_base` - GPT-4, GPT-3.5-turbo
