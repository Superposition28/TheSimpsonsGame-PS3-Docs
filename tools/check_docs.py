"""Check the standalone documentation and optional module integration.

Run from any directory with Python 3.11+. No third-party packages are required.
This checks documentation contracts; it does not execute game operations.
"""

import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import json
import sys
import tomllib
from urllib.parse import unquote, urlsplit

try:
    from format_docs import VOID_TAGS, check_html_formatting
    from render_reference import generated_pages
    from render_home import render_index
except ImportError:
    from tools.format_docs import VOID_TAGS, check_html_formatting
    from tools.render_reference import generated_pages
    from tools.render_home import render_index


class Document(HTMLParser):
    """Collect links and structural metadata without loading external resources."""

    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.links: list[tuple[str, str, str]] = []
        self.classes: set[str] = set()
        self.sections: list[str] = []
        self.section_ids: set[str] = set()
        self.viewport = False
        self.inline_styles = False
        self.operations: dict[int, dict[str, str | None]] = {}
        self.tag_stack: list[str] = []
        self.structure_errors: list[str] = []
        self.has_title = False
        self.metadata: dict[str, str] = {}
        self.feed(text)
        if self.tag_stack:
            self.structure_errors.append(f'unclosed tags: {self.tag_stack}')

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag not in VOID_TAGS:
            self.tag_stack.append(tag)
        if tag == 'title':
            self.has_title = True
        if values.get('id'):
            self.ids.append(values['id'])
        self.classes.update((values.get('class') or '').split())
        if tag == 'section':
            self.sections.append(values.get('id') or '')
            self.section_ids.update(self.sections)
        if tag == 'meta' and values.get('name') == 'viewport':
            self.viewport = True
        if tag == 'meta' and values.get('name'):
            self.metadata[values['name']] = values.get('content') or ''
        if tag == 'style':
            self.inline_styles = True
        if values.get('data-operation'):
            self.operations[int(values['data-operation'])] = values
        for attribute in ('href', 'src'):
            if values.get(attribute):
                self.links.append((tag, values[attribute], self.sections[-1] if self.sections else ''))

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_TAGS:
            return
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        else:
            self.structure_errors.append(f'line {self.getpos()[0]}: misplaced </{tag}>')
            if tag in self.tag_stack:
                while self.tag_stack.pop() != tag:
                    pass
        if tag == 'section' and self.sections:
            self.sections.pop()


def check(root: Path, module_checks: bool = False) -> int:
    """Return a failing exit code for broken targets or coverage inconsistencies."""
    root = root.resolve()
    pages = {
        path.resolve(): Document(path.read_text(encoding='utf-8-sig'))
        for path in root.rglob('*.html')
        if '.history' not in path.parts
    }
    errors: list[str] = []
    files_by_case = {str(path.resolve()).casefold(): path.resolve()
                     for path in root.rglob('*') if path.is_file()}
    relationships: dict[Path, set[Path]] = {}
    format_root = root / 'PS3_GAME/FormatAnalysis'
    overviews = {format_root / name for name in ('index.html', 'pipeline.html', 'relationships.html')}
    format_pages = {
        path for path, document in pages.items()
        if 'format-summary' in document.classes
        or (path.is_relative_to(format_root) and path not in overviews)
    }
    registry = json.loads((root / 'reference/sources.json').read_text(encoding='utf-8'))
    source_ids = [source['id'] for source in registry['sources']]
    if len(source_ids) != len(set(source_ids)):
        errors.append('reference/sources.json: duplicate source identifiers')
    if not {'ps3-eu-original', 'ps3-eu-extracted', 'ps3-eu-flattened'}.issubset(source_ids):
        errors.append('reference/sources.json: missing canonical source identities')
    for path, expected_html in generated_pages(root).items():
        if not path.exists() or path.read_bytes() != expected_html.encode('utf-8'):
            errors.append(f'{path.relative_to(root)}: stale generated reference; run tools/render_reference.py')
    if (root / 'index.html').read_bytes() != render_index(root).encode('utf-8'):
        errors.append('index.html: stale coverage counts/map colours; run tools/render_home.py')
    namespace_ids = {'original', 'extracted', 'flattened', 'mixed-explicit', 'legacy-mixed'}
    for path, document in pages.items():
        label = path.relative_to(root).as_posix()
        duplicates = [value for value, count in Counter(document.ids).items() if count > 1]
        if duplicates:
            errors.append(f'{label}: duplicate IDs {duplicates}')
        if not document.viewport:
            errors.append(f'{label}: missing viewport metadata')
        if not document.has_title:
            errors.append(f'{label}: missing document title')
        errors.extend(f'{label}: {error}' for error in document.structure_errors)
        if document.inline_styles:
            errors.append(f'{label}: per-page style block; use the shared stylesheet')
        if not any(url.endswith('style/main.css') for _, url, _ in document.links):
            errors.append(f'{label}: missing shared stylesheet')
        if path in format_pages:
            required = {'related-formats', 'evidence-limits'}
            if 'format-summary' not in document.classes or not required.issubset(document.section_ids):
                errors.append(f'{label}: missing format coverage sections')
            relationships[path] = set()
        if path in format_pages or path.is_relative_to(root / 'PS3_GAME/USRDIR'):
            if document.metadata.get('reference-source') not in source_ids:
                errors.append(f'{label}: missing or unknown reference-source metadata')
            if document.metadata.get('path-namespace') not in namespace_ids:
                errors.append(f'{label}: missing or unknown path-namespace metadata')
        for tag, value, section in document.links:
            url = urlsplit(value)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.is_relative_to(root):
                errors.append(f'{label}: non-portable local target {value}')
            elif not target.exists():
                errors.append(f'{label}: missing target {value}')
            elif str(target).casefold() in files_by_case and str(target) != str(files_by_case[str(target).casefold()]):
                errors.append(f'{label}: target capitalization differs from disk: {value}')
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f'{label}: missing anchor {value}')
            if section == 'related-formats' and target in format_pages:
                relationships.setdefault(path, set()).add(target)
        text = path.read_text(encoding='utf-8-sig')
        for tag in ('pre', 'code', 'div', 'table', 'section', 'details'):
            opened = len(re.findall(r'<' + tag + r'(?:\s|>)', text))
            closed = text.count('</' + tag + '>')
            if opened != closed:
                errors.append(f'{label}: unbalanced {tag}: {opened} opens, {closed} closes')
        if re.search(r'╬|├|�', text):
            errors.append(f'{label}: unresolved text encoding damage')
        for issue in check_html_formatting(path.read_bytes()):
            errors.append(f'{label}: {issue}')

    for source, targets in relationships.items():
        for target in targets:
            if source not in relationships.get(target, set()):
                errors.append(f'{source.relative_to(root)}: relationship to {target.name} has no reciprocal link')

    module = root.parent.parent
    manifest = module / 'operations.toml'
    operation_count = 0
    if module_checks and not manifest.exists():
        errors.append('--module-checks requires operations.toml in a parent module checkout')
    if module_checks and manifest.exists():
        operations = tomllib.loads(manifest.read_text(encoding='utf-8-sig'))['operation']
        pipeline = pages[root / 'integrations/remake-engine/pipeline.html'].operations
        expected = {operation['id']: operation for operation in operations}
        operation_count = len(expected)
        if pipeline.keys() != expected.keys():
            errors.append('pipeline.html: operation IDs differ from operations.toml')
        for identifier, operation in expected.items():
            row = pipeline.get(identifier, {})
            dependencies = ','.join(str(value) for value in operation.get('depends-on', []))
            if row.get('data-depends-on') != dependencies:
                errors.append(f'pipeline.html: operation {identifier} dependency drift')
            if row.get('data-run-all') != str(operation.get('run-all', False)).lower():
                errors.append(f'pipeline.html: operation {identifier} run-all drift')
        for path in pages:
            text = path.read_text(encoding='utf-8-sig')
            for reference in re.findall(r'operations/[A-Za-z0-9_./-]+\.(?:lua|bms|py)', text):
                if not (module / reference).is_file():
                    errors.append(f'{path.relative_to(root)}: missing module script {reference}')

    for error in errors:
        print('ERROR:', error)
    print(f'Checked {len(pages)} HTML pages, {len(relationships)} format pages, '
          f'{sum(len(targets) for targets in relationships.values()) // 2} reciprocal relationships'
          + (f' and {operation_count} registered operations.' if operation_count else '. Core reference checked independently of module integration.'))
    print(f'{len(errors)} error(s).')
    return 1 if errors else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module-checks', action='store_true',
                        help='Also compare optional Remake Engine integration with the parent checkout.')
    arguments = parser.parse_args()
    sys.exit(check(Path(__file__).resolve().parent.parent, arguments.module_checks))
