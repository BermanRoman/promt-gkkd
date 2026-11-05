#!/usr/bin/env python3
"""Select complete ATX Markdown sections locally, without truncation or network."""

import argparse
import hashlib
from pathlib import Path
import re
import sys
import unicodedata


def sections(text, selectors):
    if any(unicodedata.category(char) == 'Cf' for char in text):
        raise ValueError('input contains hidden format characters')
    if len(set(selectors)) != len(selectors):
        raise ValueError('duplicate heading selector')
    # Ignore heading-like text inside fenced code blocks.
    headings = []
    fence = None
    offset = 0
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line.rstrip('\r\n'))
        if marker:
            run, tail = marker.groups()
            if fence is None:
                fence = (run[0], len(run))
            elif run[0] == fence[0] and len(run) >= fence[1] and not tail.strip():
                fence = None
        elif fence is None:
            match = re.match(r'^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*$', line.rstrip('\r\n'))
            if match:
                label = re.sub(r'[ \t]+#+[ \t]*$', '', match[2]).strip()
                headings.append((label, len(match[1]), offset))
        offset += len(line)
    selected = []
    for selector in selectors:
        matches = [i for i, heading in enumerate(headings) if heading[0] == selector]
        if len(matches) != 1:
            raise ValueError('heading must occur exactly once: ' + selector)
        index = matches[0]
        _, level, start = headings[index]
        end = next((pos for _, depth, pos in headings[index + 1:] if depth <= level), len(text))
        selected.append((start, end))
    # Overlapping selections include each source character only once, in source order.
    merged = []
    for start, end in sorted(selected):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return '\n'.join(text[start:end] for start, end in merged)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', type=Path, required=True)
    parser.add_argument('--heading', action='append', required=True,
                        help='exact ATX heading text without #; repeatable')
    parser.add_argument('--output', type=Path, help='write to a new local UTF-8 file instead of stdout')
    args = parser.parse_args(argv)
    try:
        text = args.file.read_bytes().decode('utf-8')
        result = sections(text, args.heading)
        if args.output:
            # Exclusive creation prevents accidental source replacement or clobbering.
            with args.output.open('x', encoding='utf-8', newline='') as stream:
                stream.write(result)
        else:
            sys.stdout.write(result)
    except (OSError, UnicodeError, ValueError) as error:
        print('context: ' + str(error), file=sys.stderr)
        return 2
    print('source SHA-256: ' + hashlib.sha256(text.encode('utf-8')).hexdigest(), file=sys.stderr)
    print('selection SHA-256: ' + hashlib.sha256(result.encode('utf-8')).hexdigest(), file=sys.stderr)
    print(f'context: {len(args.heading)} selector(s), {len(result)} characters, '
          f'{len(result.encode("utf-8"))} UTF-8 bytes; complete sections, no truncation', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
