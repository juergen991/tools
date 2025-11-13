# File Line Comparator

A lightweight Python tool that compares two files line by line without considering order. It displays differences compactly, provides statistics, and can generate JSON or simple diff outputs on request.

## Highlights

- Comparison purely based on line content, completely independent of position
- Clear listing of lines that appear only in File 1 or File 2
- Optional display of common lines including frequency per file
- Statistics on total, unique, and common lines as well as frequency mismatches
- Flexible output formats: colored text (default), JSON, or simple diff layout
- Convenience options like `--ignore-whitespace`, `--ignore-case`, `--include-empty-lines`, `--no-color`
- Output can be written directly to a file (`--output`)

## Installation

Python 3.6 or newer is sufficient. No additional dependencies are required.

```bash
chmod +x file_compare.py
```

## Quick Start

```bash
python file_compare.py file1.txt file2.txt
```

For an overview of all arguments:

```bash
python file_compare.py --help
```

## Commonly Used Options

| Purpose | Example |
|---------|----------|
| Ignore whitespace at line start/end | `--ignore-whitespace` or `-w` |
| Ignore case | `--ignore-case` or `-i` |
| Combine both options | `-w -i` |
| Show common lines | `--show-common` |
| Generate JSON output | `--format json` |
| Generate simple diff output | `--format simple` |
| Disable colors | `--no-color` |
| Write result to file | `--output result.txt` |
| Include empty lines | `--include-empty-lines` |
| Output compact JSON | `--no-pretty-json` |

## Output Modes

### Colored Text (Default)

```
=== File Comparison ===
File 1: file1.txt
File 2: file2.txt

Statistics:
  File 1: 100 total lines, 95 unique lines
  File 2: 120 total lines, 110 unique lines
  Common lines: 80
  Only in File 1: 15
  Only in File 2: 30
  Frequency mismatches: 1

Lines only in File 1:
  - Line only in file 1
  - Another unique line (3x)

Lines only in File 2:
  + Line only in file 2
  + Another new line (2x)
```

The suffix **`(Nx)`** indicates how many times a specific line appears exclusively in the respective file. For lines appearing in both files, text mode only displays a hint when frequencies differ: `= apple (File1: 2x, File2: 1x)`.

### JSON

Structured and easy to process:

```json
{
  "file1": "file1.txt",
  "file2": "file2.txt",
  "stats": {
    "file1_total_lines": 100,
    "file2_total_lines": 120,
    "file1_unique_lines": 95,
    "file2_unique_lines": 110,
    "common_lines": 80,
    "only_in_file1": 15,
    "only_in_file2": 30,
    "frequency_mismatches": 1
  },
  "only_in_file1": ["Line 1", "Line 2"],
  "only_in_file2": ["Line A", "Line B"],
  "common": ["Common line 1", "Common line 2"],
  "frequencies": {
    "common": {
      "Common line 1": {"file1": 2, "file2": 2},
      "Common line 2": {"file1": 1, "file2": 3}
    },
    "only_in_file1": {
      "Line 1": 1,
      "Line 2": 3
    },
    "only_in_file2": {
      "Line A": 2,
      "Line B": 1
    }
  }
}
```

### Simple Diff

```
< Lines only in file1.txt:
< Line only in file 1
< Another unique line (3x)

> Lines only in file2.txt:
> Line only in file 2
> Another new line (2x)
```

## Empty Lines

- By default, empty lines are ignored to exclude pure formatting differences.
- Use `--include-empty-lines` to explicitly include empty lines in the comparison.
- In combination with `--ignore-whitespace`, a line is considered empty if it has no content after trimming.

## Exit Codes

- `0` – no differences found (identical line set)
- `1` – differences or errors occurred

## Typical Use Cases

- Compare configuration files where line order may vary
- Check if all entries of one list are present in another
- Check inventory lists or CSV exports for missing or additional elements
- Visualize different frequencies in two data sets

## Example Scenarios

### 1. Sorted vs. Unsorted List

```
file1.txt        file2.txt
-----------      -----------
apple            cherry
pear             apple
cherry           pear
```

```
python file_compare.py file1.txt file2.txt
=> Exit code 0 (identical)
```

### 2. Find Missing Entries

```
file1.txt        file2.txt
-----------      -----------
user1            user2
user2            user4
user3            user3
```

```
python file_compare.py file1.txt file2.txt
```
```
Lines only in File 1:
  - user1

Lines only in File 2:
  + user4
```

### 3. Visualize Frequencies

```
file1.txt        file2.txt
-----------      -----------
apple            apple
apple            pear
pear             pear
cherry           pear
```

```
python file_compare.py file1.txt file2.txt --show-common
```
```
Common lines:
  = apple (File1: 2x, File2: 1x)
  = pear (File1: 1x, File2: 3x)
```

## Technical Details

- Implemented with `Path` and `Counter` from the standard library
- Reads files initially as UTF-8, automatically falls back to Latin-1 on errors
- Automatically removes line breaks (`\r`, `\n`)
- Works internally with sets and counters for fast set operations

## Difference from Classic `diff`

| Feature | `diff` | `file_compare.py` |
|---------|--------|-------------------|
| Order relevant | Yes | No |
| Line position visible | Yes | No |
| Context around changes | Yes | No (focuses on differences) |
| JSON output | No | Yes |
| Statistics & frequencies | No | Yes |

## License

Free to use for all purposes.
