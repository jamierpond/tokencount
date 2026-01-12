import subprocess
import tempfile
from pathlib import Path

from main import DEFAULT_ENCODING, count_tokens


def test_count_tokens_basic() -> None:
    assert count_tokens("hello", DEFAULT_ENCODING) > 0


def test_count_tokens_empty() -> None:
    assert count_tokens("", DEFAULT_ENCODING) == 0


def test_custom_encoding() -> None:
    result = subprocess.run(
        ["python", "main.py", "-e", "cl100k_base"],
        input="hello world",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip().isdigit()


def test_invalid_encoding() -> None:
    result = subprocess.run(
        ["python", "main.py", "-e", "invalid_encoding"],
        input="hello",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "unknown encoding" in result.stderr


def test_single_file() -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello world")
        f.flush()
        result = subprocess.run(
            ["python", "main.py", f.name],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout.strip().isdigit()
        assert int(result.stdout.strip()) > 0
        assert result.stderr == ""
    Path(f.name).unlink()


def test_multiple_files_sorted_output() -> None:
    with (
        tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as small,
        tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as large,
    ):
        small.write("hi")
        large.write("hello world this is a longer text with more tokens")
        small.flush()
        large.flush()

        result = subprocess.run(
            ["python", "main.py", large.name, small.name],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout.strip().isdigit()

        assert "### Token counts:" in result.stderr
        assert small.name in result.stderr
        assert large.name in result.stderr
        assert "total" in result.stderr
        small_pos = result.stderr.find(small.name)
        large_pos = result.stderr.find(large.name)
        assert small_pos < large_pos

    Path(small.name).unlink()
    Path(large.name).unlink()


def test_json_output() -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello world")
        f.flush()
        result = subprocess.run(
            ["python", "main.py", "--json", f.name],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        import json

        data = json.loads(result.stdout)
        assert "encoding" in data
        assert "files" in data
        assert "total" in data
        assert data["total"] > 0
    Path(f.name).unlink()


def test_stdin_input() -> None:
    result = subprocess.run(
        ["python", "main.py"],
        input="hello world",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip().isdigit()
    assert int(result.stdout.strip()) > 0


def test_file_not_found() -> None:
    result = subprocess.run(
        ["python", "main.py", "nonexistent_file.txt"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "No such file or directory" in result.stderr


def test_directory_error() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["python", "main.py", tmpdir],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Is a directory" in result.stderr
