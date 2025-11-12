#!/usr/bin/env python3
"""
File Line Comparator - Compare two files line by line, ignoring line order.

This tool compares two files and shows which lines are unique to each file,
regardless of their position in the file.
"""

import argparse
import json
import sys
from typing import Set, Dict, List, Tuple
from pathlib import Path


class FileComparator:
    """Compare two files line by line, ignoring order."""

    def __init__(self, ignore_whitespace: bool = False, ignore_case: bool = False):
        """
        Initialize the comparator.

        Args:
            ignore_whitespace: If True, strip leading/trailing whitespace from lines
            ignore_case: If True, perform case-insensitive comparison
        """
        self.ignore_whitespace = ignore_whitespace
        self.ignore_case = ignore_case

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

    def read_file_lines(self, filepath: Path) -> Tuple[Set[str], List[str]]:
        """
        Read file and return both a set of unique lines and the original list.

        Args:
            filepath: Path to the file to read

        Returns:
            Tuple of (set of normalized lines, list of original lines)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.rstrip('\n\r') for line in f]

            normalized_lines = {self.normalize_line(line) for line in lines if line or not self.ignore_whitespace}
            return normalized_lines, lines
        except UnicodeDecodeError:
            # Try with latin-1 encoding if utf-8 fails
            with open(filepath, 'r', encoding='latin-1') as f:
                lines = [line.rstrip('\n\r') for line in f]

            normalized_lines = {self.normalize_line(line) for line in lines if line or not self.ignore_whitespace}
            return normalized_lines, lines

    def compare(self, file1: Path, file2: Path) -> Dict:
        """
        Compare two files and return the differences.

        Args:
            file1: Path to first file
            file2: Path to second file

        Returns:
            Dictionary with comparison results
        """
        lines1_set, lines1_orig = self.read_file_lines(file1)
        lines2_set, lines2_orig = self.read_file_lines(file2)

        only_in_file1 = sorted(lines1_set - lines2_set)
        only_in_file2 = sorted(lines2_set - lines1_set)
        common_lines = sorted(lines1_set & lines2_set)

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
                'only_in_file2': len(only_in_file2)
            },
            'only_in_file1': only_in_file1,
            'only_in_file2': only_in_file2,
            'common': common_lines
        }


class OutputFormatter:
    """Format comparison results for output."""

    @staticmethod
    def format_text(results: Dict, show_common: bool = False, use_color: bool = False) -> str:
        """
        Format results as human-readable text.

        Args:
            results: Comparison results dictionary
            show_common: If True, also show common lines
            use_color: If True, use ANSI color codes

        Returns:
            Formatted text string
        """
        output = []

        # Colors
        RED = '\033[91m' if use_color else ''
        GREEN = '\033[92m' if use_color else ''
        BLUE = '\033[94m' if use_color else ''
        YELLOW = '\033[93m' if use_color else ''
        RESET = '\033[0m' if use_color else ''
        BOLD = '\033[1m' if use_color else ''

        # Header
        output.append(f"{BOLD}=== File Comparison ==={RESET}")
        output.append(f"File 1: {results['file1']}")
        output.append(f"File 2: {results['file2']}")
        output.append("")

        # Statistics
        stats = results['stats']
        output.append(f"{BOLD}Statistics:{RESET}")
        output.append(f"  File 1: {stats['file1_total_lines']} total lines, {stats['file1_unique_lines']} unique lines")
        output.append(f"  File 2: {stats['file2_total_lines']} total lines, {stats['file2_unique_lines']} unique lines")
        output.append(f"  {GREEN}Common lines: {stats['common_lines']}{RESET}")
        output.append(f"  {RED}Only in File 1: {stats['only_in_file1']}{RESET}")
        output.append(f"  {BLUE}Only in File 2: {stats['only_in_file2']}{RESET}")
        output.append("")

        # Lines only in file 1
        if results['only_in_file1']:
            output.append(f"{BOLD}{RED}Lines only in File 1:{RESET}")
            for line in results['only_in_file1']:
                output.append(f"  {RED}- {line}{RESET}")
            output.append("")
        else:
            output.append(f"{GREEN}No lines unique to File 1{RESET}")
            output.append("")

        # Lines only in file 2
        if results['only_in_file2']:
            output.append(f"{BOLD}{BLUE}Lines only in File 2:{RESET}")
            for line in results['only_in_file2']:
                output.append(f"  {BLUE}+ {line}{RESET}")
            output.append("")
        else:
            output.append(f"{GREEN}No lines unique to File 2{RESET}")
            output.append("")

        # Common lines (optional)
        if show_common and results['common']:
            output.append(f"{BOLD}{GREEN}Common lines:{RESET}")
            for line in results['common']:
                output.append(f"  {GREEN}= {line}{RESET}")
            output.append("")

        return '\n'.join(output)

    @staticmethod
    def format_json(results: Dict, pretty: bool = True) -> str:
        """
        Format results as JSON.

        Args:
            results: Comparison results dictionary
            pretty: If True, use pretty-printing

        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(results, indent=2, ensure_ascii=False)
        return json.dumps(results, ensure_ascii=False)

    @staticmethod
    def format_simple(results: Dict) -> str:
        """
        Format results as simple diff-like output.

        Args:
            results: Comparison results dictionary

        Returns:
            Simple formatted string
        """
        output = []

        if results['only_in_file1']:
            output.append(f"< Lines only in {results['file1']}:")
            for line in results['only_in_file1']:
                output.append(f"< {line}")
            output.append("")

        if results['only_in_file2']:
            output.append(f"> Lines only in {results['file2']}:")
            for line in results['only_in_file2']:
                output.append(f"> {line}")

        return '\n'.join(output)


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
    parser.add_argument('--pretty-json', action='store_true', default=True,
                        help='Pretty-print JSON output (default: True)')

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
        ignore_case=args.ignore_case
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
