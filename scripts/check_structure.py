#!/usr/bin/env python3
"""Check supported inline local links and required agent metadata."""

from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted(
    list(ROOT.glob('*.md'))
    + [p for folder in ('agents', 'core', 'knowledge', 'library')
       for p in (ROOT / folder).rglob('*.md')]
)
errors = []
references = 0
names = {}
for path in FILES:
    text = path.read_text(encoding='utf-8')
    rel = path.relative_to(ROOT)
    for match in re.finditer(r'`((?:agents|core|knowledge|library)/[^`\n]+\.md)`', text):
        target = match.group(1)
        if any(c in target for c in ('*', '<', '>', '…')):
            continue
        references += 1
        if not (ROOT / target).is_file():
            line = text.count('\n', 0, match.start()) + 1
            errors.append(f'{rel}:{line}: missing local reference {target}')
    for match in re.finditer(r'\]\(([^)\n]+)\)', text):
        target = match.group(1).strip('<>')
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        target_path = Path(unquote(parts.path))
        # Absolute links can refer to the user's external workspace.
        if target_path.is_absolute():
            continue
        references += 1
        if not (path.parent / target_path).exists():
            line = text.count('\n', 0, match.start()) + 1
            errors.append(f'{rel}:{line}: missing Markdown target {target}')
    if path.parent.name == 'agents':
        header = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
        if not header:
            errors.append(f'{rel}: missing frontmatter')
            continue
        fields = {}
        for field in re.finditer(r'^(name|description|version):[^\S\n]*(.*)$',
                                 header.group(1), re.M):
            key, value = field.groups()
            if key in fields:
                errors.append(f'{rel}: duplicate metadata field {key}')
            value = value.strip()
            if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1].strip()
            fields[key] = value
        name = fields.get('name', '')
        description = fields.get('description', '')
        if not re.fullmatch(r'[a-z][a-z0-9_-]*', name):
            errors.append(f'{rel}: missing or invalid agent name')
        if not description or description in ('null', '~', '|', '>', '|-', '>-'):
            errors.append(f'{rel}: missing nonempty single-line description')
        if not re.fullmatch(r'[1-9][0-9]*', fields.get('version', '')):
            errors.append(f'{rel}: missing positive integer version')
        if name in names:
            errors.append(f'{rel}: duplicate agent name from {names[name]}')
        elif name:
            names[name] = str(rel)

print(f'Checked {len(FILES)} Markdown files, {references} local references, {len(names)} agent names.')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print('Structure OK. Content, interface behavior and sales effectiveness require separate checks.')
print('Scope: inline links and agent name/description/version; reference-style links, anchors and external dependencies are not validated.')
