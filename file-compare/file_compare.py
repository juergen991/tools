#!/usr/bin/env python3
"""
File Line Comparator - Compare two files line by line, ignoring line order.

This tool compares two files and shows which lines are unique to each file,
regardless of their position in the file.
"""

import argparse
import json
import sys
from typing import Dict, List, Set, Tuple, TypedDict
from pathlib import Path
from collections import Counter


class FrequencyPair(TypedDict):
    """Frequency pair for a line that appears in both files."""

    file1: int
    file2: int


class ComparisonFrequencies(TypedDict):
    """Frequencies for unique and common lines."""

    common: Dict[str, FrequencyPair]
    only_in_file1: Dict[str, int]
    only_in_file2: Dict[str, int]


class ComparisonStats(TypedDict):
    """Statistical overview of the comparison."""

    file1_total_lines: int
    file2_total_lines: int
    file1_unique_lines: int
    file2_unique_lines: int
    common_lines: int
    only_in_file1: int
    only_in_file2: int
    frequency_mismatches: int


class ComparisonResult(TypedDict):
    """Structured comparison result."""

    file1: str
    file2: str
    stats: ComparisonStats
    only_in_file1: List[str]
    only_in_file2: List[str]
    common: List[str]
    frequencies: ComparisonFrequencies

class FileComparator:
    """Compare two files line by line, ignoring order."""

    def __init__(self, ignore_whitespace: bool = False, ignore_case: bool = False, ignore_empty_lines: bool = True):
        """
        Initialize the comparator.

        Args:
            ignore_whitespace: If True, strip leading/trailing whitespace from lines
            ignore_case: If True, perform case-insensitive comparison
            ignore_empty_lines: If True, ignore empty lines during comparison (default: True)
        """
        self.ignore_whitespace = ignore_whitespace
        self.ignore_case = ignore_case
        self.ignore_empty_lines = ignore_empty_lines

    def normalize_line(self, line: str) -> str:
        """
        Normalize a line according to comparison options.

        Args:
            line: The line to normalize

        Returns:
            Normalized line string
        """
        if self.ignore_whitespace:
            line = line.strip()
        if self.ignore_case:
            line = line.lower()
        return line

    def _read_file_with_encoding(self, filepath: Path, encoding: str) -> List[str]:
        """
        Read file with specified encoding.

        Args:
            filepath: Path to the file to read
            encoding: Encoding to use

        Returns:
            List of lines with line breaks removed
        """
        with open(filepath, 'r', encoding=encoding) as f:
            return [line.rstrip('\n\r') for line in f]


    def _filter_lines(self, lines: List[str]) -> List[str]:
        """Filter lines according to the empty-line handling configuration.
    
        Args:
            lines (List[str]): Lines read from the input file.
    
        Returns:
            List[str]: Lines that comply with the active empty-line settings.
        """
        if not self.ignore_empty_lines:
            return lines
    
        if self.ignore_whitespace:
            return [line for line in lines if line.strip()]
    
        return [line for line in lines if line]
    
    def read_file_lines(self, filepath: Path) -> Tuple[Set[str], List[str], Counter[str]]:
        """Read file and return normalized line collections.
    
        Args:
            filepath: Path to the file to read
    
        Returns:
            Tuple of (set of normalized lines, list of original lines, Counter over normalized lines)
        """
        try:
            lines = self._read_file_with_encoding(filepath, 'utf-8')
        except UnicodeDecodeError:
            # Try with latin-1 encoding if utf-8 fails
            lines = self._read_file_with_encoding(filepath, 'latin-1')
    
        filtered_lines = self._filter_lines(lines)
    
        # Normalize and count lines
        normalized_lines_list = [self.normalize_line(line) for line in filtered_lines]
        normalized_lines_set = set(normalized_lines_list)
        normalized_lines_counter = Counter(normalized_lines_list)
    
        return normalized_lines_set, lines, normalized_lines_counter


    def compare(self, file1: Path, file2: Path) -> ComparisonResult:
        """Compare two files and return the differences including line frequencies.
    
        Args:
            file1: Path to first file.
            file2: Path to second file.
    
        Returns:
            ComparisonResult: Structured comparison of both files.
        """
        lines1_set, lines1_orig, lines1_counter = self.read_file_lines(file1)
        lines2_set, lines2_orig, lines2_counter = self.read_file_lines(file2)
    
        only_in_file1 = sorted(lines1_set - lines2_set)
        only_in_file2 = sorted(lines2_set - lines1_set)
        common_lines = sorted(lines1_set & lines2_set)
    
        common_frequencies: Dict[str, FrequencyPair] = {
            line: {'file1': lines1_counter[line], 'file2': lines2_counter[line]}
            for line in common_lines
        }
        only_in_file1_frequencies: Dict[str, int] = {
            line: lines1_counter[line] for line in only_in_file1
        }
        only_in_file2_frequencies: Dict[str, int] = {
            line: lines2_counter[line] for line in only_in_file2
        }
        frequency_mismatches = sum(
            1 for freq in common_frequencies.values() if freq['file1'] != freq['file2']
        )
    
        return {
            'file1': str(file1),
            'file2': str(file2),
            'stats': {
                'file1_total_lines': len(lines1_orig),
                'file2_total_lines': len(lines2_orig),
                'file1_unique_lines': len(lines1_set),
                'file2_unique_lines': len(lines2_set),
                'common_lines': len(common_lines),
                'only_in_file1': len(only_in_file1),
                'only_in_file2': len(only_in_file2),
                'frequency_mismatches': frequency_mismatches,
            },
            'only_in_file1': only_in_file1,
            'only_in_file2': only_in_file2,
            'common': common_lines,
            'frequencies': {
                'common': common_frequencies,
                'only_in_file1': only_in_file1_frequencies,
                'only_in_file2': only_in_file2_frequencies,
            },
        }
    
    


class OutputFormatter:
    """Format comparison results for output."""

    @staticmethod
    def _count_suffix(count: int) -> str:
        """Return a suffix that encodes how often a line appears.

        Args:
            count (int): Number of occurrences of a specific line.

        Returns:
            str: Formatted suffix or an empty string if no suffix is needed.
        """
        return f" ({count}x)" if count > 1 else ""

    @staticmethod
    def _common_suffix(freq: FrequencyPair) -> str:
        """Return a suffix describing occurrences in both files.

        Args:
            freq (FrequencyPair): Occurrence counts for the same line in both files.

        Returns:
            str: Suffix when frequencies differ, otherwise an empty string.
        """
        if freq['file1'] == freq['file2']:
            return ""

        return f" (File1: {freq['file1']}x, File2: {freq['file2']}x)"

    @staticmethod
    def _append_difference_block(
        output: List[str],
        *,
        lines: List[str],
        header: str,
        symbol: str,
        color: str,
        message_color: str,
        empty_message: str,
        frequencies: Dict[str, int],
        bold: str,
        reset: str,
        suffix_color: str,
    ) -> None:
        """Append formatted information about differing lines.

        Args:
            output (List[str]): Aggregated output buffer to extend.
            lines (List[str]): Lines that are unique to one of the files.
            header (str): Section header to render.
            symbol (str): Prefix symbol that indicates the diff direction.
            color (str): ANSI color escape for the section content.
            message_color (str): ANSI color escape for the empty-state message.
            empty_message (str): Message to display when no lines are present.
            frequencies (Dict[str, int]): Mapping of line to occurrence count.
            bold (str): ANSI bold escape sequence (or empty string).
            reset (str): ANSI reset escape sequence (or empty string).
            suffix_color (str): ANSI color escape for suffix information.
        """
        if lines:
            output.append(f"{bold}{color}{header}:{reset}")
            for line in lines:
                suffix = OutputFormatter._count_suffix(frequencies.get(line, 1))
                base = f"  {color}{symbol} {line}{reset}"
                if suffix:
                    base = f"{base}{suffix_color}{suffix}{reset}"
                output.append(base)
            output.append("")
            return

        output.append(f"{message_color}{empty_message}{reset}")
        output.append("")

    @staticmethod
    def format_text(
        results: ComparisonResult, show_common: bool = False, use_color: bool = False
    ) -> str:
        """Format results as human-readable text.

        Args:
            results (ComparisonResult): Structured comparison data.
            show_common (bool): Whether to include common lines in the output.
            use_color (bool): Whether to emit ANSI color codes.

        Returns:
            str: Formatted text representation of the comparison.
        """
        output: List[str] = []

        # Colors
        red = '\033[91m' if use_color else ''
        green = '\033[92m' if use_color else ''
        blue = '\033[94m' if use_color else ''
        yellow = '\033[93m' if use_color else ''
        suffix_color = '\033[97m' if use_color else ''
        reset = '\033[0m' if use_color else ''
        bold = '\033[1m' if use_color else ''

        # Header
        output.append(f"{bold}=== File Comparison ==={reset}")
        output.append(f"File 1: {results['file1']}")
        output.append(f"File 2: {results['file2']}")
        output.append("")

        # Statistics
        stats = results['stats']
        mismatches = stats['frequency_mismatches']
        mismatch_prefix = yellow if use_color and mismatches else ''
        mismatch_suffix = reset if mismatch_prefix else ''

        output.append(f"{bold}Statistics:{reset}")
        output.append(
            f"  File 1: {stats['file1_total_lines']} total lines, {stats['file1_unique_lines']} unique lines"
        )
        output.append(
            f"  File 2: {stats['file2_total_lines']} total lines, {stats['file2_unique_lines']} unique lines"
        )
        output.append(f"  {green}Common lines: {stats['common_lines']}{reset}")
        output.append(f"  {red}Only in File 1: {stats['only_in_file1']}{reset}")
        output.append(f"  {blue}Only in File 2: {stats['only_in_file2']}{reset}")
        output.append(
            f"  {mismatch_prefix}Frequency mismatches: {mismatches}{mismatch_suffix}"
        )
        output.append("")

        frequencies = results['frequencies']

        OutputFormatter._append_difference_block(
            output,
            lines=results['only_in_file1'],
            header='Lines only in File 1',
            symbol='-',
            color=red,
            message_color=green,
            empty_message='No lines unique to File 1',
            frequencies=frequencies['only_in_file1'],
            bold=bold,
            reset=reset,
            suffix_color=suffix_color,
        )

        OutputFormatter._append_difference_block(
            output,
            lines=results['only_in_file2'],
            header='Lines only in File 2',
            symbol='+',
            color=blue,
            message_color=green,
            empty_message='No lines unique to File 2',
            frequencies=frequencies['only_in_file2'],
            bold=bold,
            reset=reset,
            suffix_color=suffix_color,
        )

        if show_common and results['common']:
            output.append(f"{bold}{green}Common lines:{reset}")
            for line in results['common']:
                suffix = OutputFormatter._common_suffix(frequencies['common'][line])
                base = f"  {green}= {line}{reset}"
                if suffix:
                    base = f"{base}{suffix_color}{suffix}{reset}"
                output.append(base)
            output.append("")

        return '\n'.join(output)

    @staticmethod
    def format_json(results: ComparisonResult, pretty: bool = True) -> str:
        """Format results as JSON.

        Args:
            results (ComparisonResult): Structured comparison data.
            pretty (bool): Whether to pretty-print the JSON output.

        Returns:
            str: JSON formatted comparison results.
        """
        if pretty:
            return json.dumps(results, indent=2, ensure_ascii=False)
        return json.dumps(results, ensure_ascii=False)

    @staticmethod
    def format_simple(results: ComparisonResult) -> str:
        """Format results as simple diff-like output.

        Args:
            results (ComparisonResult): Structured comparison data.

        Returns:
            str: Diff-style summary of lines unique to each file.
        """
        output: List[str] = []
        frequencies = results['frequencies']

        def append_section(symbol: str, header: str, lines: List[str], counts: Dict[str, int]) -> None:
            """Append a diff section to the output buffer."""
            if not lines:
                return
            output.append(header)
            for line in lines:
                suffix = OutputFormatter._count_suffix(counts.get(line, 1))
                output.append(f"{symbol} {line}{suffix}")
            output.append("")

        append_section('<', f"< Lines only in {results['file1']}:", results['only_in_file1'], frequencies['only_in_file1'])
        append_section('>', f"> Lines only in {results['file2']}:", results['only_in_file2'], frequencies['only_in_file2'])

        return '\n'.join(output).rstrip()



def main():
    """Main entry point for the file comparator."""
    parser = argparse.ArgumentParser(
        description='Compare two files line by line, ignoring line order.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file1.txt file2.txt
  %(prog)s file1.txt file2.txt --ignore-whitespace
  %(prog)s file1.txt file2.txt --ignore-case
  %(prog)s file1.txt file2.txt --format json
  %(prog)s file1.txt file2.txt --format simple
  %(prog)s file1.txt file2.txt --show-common
  %(prog)s file1.txt file2.txt --no-color
  %(prog)s file1.txt file2.txt --output result.txt
        """
    )

    parser.add_argument('file1', type=Path, help='First file to compare')
    parser.add_argument('file2', type=Path, help='Second file to compare')

    parser.add_argument('-w', '--ignore-whitespace', action='store_true',
                        help='Ignore leading and trailing whitespace')
    parser.add_argument('-i', '--ignore-case', action='store_true',
                        help='Perform case-insensitive comparison')

    parser.add_argument('-f', '--format', choices=['text', 'json', 'simple'], default='text',
                        help='Output format (default: text)')
    parser.add_argument('--show-common', action='store_true',
                        help='Also show common lines (text format only)')
    parser.add_argument('--no-color', action='store_true',
                        help='Disable colored output')
    parser.add_argument('--no-pretty-json', action='store_false', dest='pretty_json', default=True,
                        help='Disable pretty-printing of JSON output')

    parser.add_argument('--include-empty-lines', action='store_false', dest='ignore_empty_lines',
                        default=True, help='Include empty lines in comparison (default ignores them)')

    parser.add_argument('-o', '--output', type=Path,
                        help='Write output to file instead of stdout')

    args = parser.parse_args()

    # Check if files exist
    if not args.file1.exists():
        print(f"Error: File not found: {args.file1}", file=sys.stderr)
        sys.exit(1)
    if not args.file2.exists():
        print(f"Error: File not found: {args.file2}", file=sys.stderr)
        sys.exit(1)

    # Perform comparison
    comparator = FileComparator(
        ignore_whitespace=args.ignore_whitespace,
        ignore_case=args.ignore_case,
        ignore_empty_lines=args.ignore_empty_lines
    )

    try:
        results = comparator.compare(args.file1, args.file2)
    except Exception as e:
        print(f"Error comparing files: {e}", file=sys.stderr)
        sys.exit(1)

    # Format output
    formatter = OutputFormatter()

    if args.format == 'json':
        output = formatter.format_json(results, pretty=args.pretty_json)
    elif args.format == 'simple':
        output = formatter.format_simple(results)
    else:  # text
        use_color = not args.no_color and sys.stdout.isatty()
        output = formatter.format_text(results, show_common=args.show_common, use_color=use_color)

    # Write output
    if args.output:
        try:
            args.output.write_text(output, encoding='utf-8')
            print(f"Results written to {args.output}")
        except Exception as e:
            print(f"Error writing to output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)

    # Exit with appropriate code
    if results['stats']['only_in_file1'] > 0 or results['stats']['only_in_file2'] > 0:
        sys.exit(1)  # Differences found
    else:
        sys.exit(0)  # Files are identical (in terms of line content)


if __name__ == '__main__':
    main()
