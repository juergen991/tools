# File Line Comparator

A Python tool for comparing two files while ignoring line order.

## Problem

The standard `diff` tool compares files line by line in their order. This tool instead compares the content of lines independently of their position in the file.

## Features

- Compares two files line by line, independent of order
- Shows lines that only appear in file 1
- Shows lines that only appear in file 2
- Optional display of common lines
- File statistics
- Multiple output formats: Text, JSON, Simple
- Colored console output
- Options: ignore whitespace, ignore case
- Output to file possible

## Installation

No additional dependencies required. Python 3.6+ is needed.

```bash
chmod +x file_compare.py
```

## Usage

### Basic Usage

```bash
python file_compare.py file1.txt file2.txt
```

### Examples

**Ignore whitespace:**
```bash
python file_compare.py file1.txt file2.txt --ignore-whitespace
# or
python file_compare.py file1.txt file2.txt -w
```

**Ignore case:**
```bash
python file_compare.py file1.txt file2.txt --ignore-case
# or
python file_compare.py file1.txt file2.txt -i
```

**Combine both options:**
```bash
python file_compare.py file1.txt file2.txt -w -i
```

**Show common lines:**
```bash
python file_compare.py file1.txt file2.txt --show-common
```

**JSON output:**
```bash
python file_compare.py file1.txt file2.txt --format json
```

**Simple diff-like output:**
```bash
python file_compare.py file1.txt file2.txt --format simple
```

**Without colors:**
```bash
python file_compare.py file1.txt file2.txt --no-color
```

**Write output to file:**
```bash
python file_compare.py file1.txt file2.txt --output result.txt
```

## Output Formats

### Text (Default)

Colored, structured output with statistics:

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

Lines only in File 1:
  - Line only in file 1
  - Another unique line

Lines only in File 2:
  + Line only in file 2
  + Another new line
```

### JSON

Structured output for programmatic processing:

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
    "only_in_file2": 30
  },
  "only_in_file1": ["Line 1", "Line 2"],
  "only_in_file2": ["Line A", "Line B"],
  "common": ["Common line 1", "Common line 2"]
}
```

### Simple

Compact diff-like output:

```
< Lines only in file1.txt:
< Line only in file 1
< Another unique line

> Lines only in file2.txt:
> Line only in file 2
> Another new line
```

## Options

```
positional arguments:
  file1                 First file to compare
  file2                 Second file to compare

optional arguments:
  -h, --help            show this help message and exit
  -w, --ignore-whitespace
                        Ignore leading and trailing whitespace
  -i, --ignore-case     Perform case-insensitive comparison
  -f {text,json,simple}, --format {text,json,simple}
                        Output format (default: text)
  --show-common         Also show common lines (text format only)
  --no-color            Disable colored output
  --pretty-json         Pretty-print JSON output (default: True)
  -o OUTPUT, --output OUTPUT
                        Write output to file instead of stdout
```

## Exit Codes

- `0`: Files are identical (same lines, independent of order)
- `1`: Differences found or error occurred

## Use Cases

- Comparing configuration files where order doesn't matter
- Comparing lists or inventories
- Checking if all entries from one file exist in another
- Finding missing or additional entries between two versions

## Technical Details

- Uses sets for efficient comparison
- Supports UTF-8 and Latin-1 encoding
- Automatically removes line breaks (\n, \r)
- Empty lines are considered (except with --ignore-whitespace)

## Difference to diff

| Feature | diff | file_compare.py |
|---------|------|-----------------|
| Order matters | Yes | No |
| Shows position | Yes | No |
| Shows only differences | No (shows context) | Yes (optional common lines) |
| JSON output | No | Yes |
| Statistics | No | Yes |

## Example Scenarios

### Scenario 1: Sorted vs. unsorted list

**file1.txt:**
```
apple
pear
cherry
```

**file2.txt:**
```
cherry
apple
pear
```

**Result:**
```bash
python file_compare.py file1.txt file2.txt
```
```
No lines unique to File 1
No lines unique to File 2
```
Exit code: 0 (identical)

### Scenario 2: Finding missing entries

**file1.txt:**
```
user1
user2
user3
```

**file2.txt:**
```
user2
user4
user3
```

**Result:**
```bash
python file_compare.py file1.txt file2.txt
```
```
Lines only in File 1:
  - user1

Lines only in File 2:
  + user4
```

## License

This tool is freely available for all purposes.
