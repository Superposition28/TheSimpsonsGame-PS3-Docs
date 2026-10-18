"""Format HTML documentation structures into canonical 4-space indented markup.

Run from any directory with Python 3.11+. No third-party packages are required.
Preserves preformatted (<pre>) content verbatim while normalizing tag structure,
attribute quoting, void elements, and block indentation across all HTML pages.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import textwrap

INDENT_UNIT = '    '

VOID_TAGS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr',
}

INLINE_TAGS = {
    'a', 'abbr', 'b', 'br', 'cite', 'code', 'dfn', 'em', 'i', 'img',
    'input', 'kbd', 'mark', 'q', 'samp', 'small', 'span', 'strong',
    'sub', 'sup', 'time', 'u', 'var', 'wbr',
}

CONTAINER_TAGS = {
    'html', 'head', 'body', 'main', 'section', 'details',
    'dl', 'ul', 'ol', 'table', 'thead', 'tbody', 'tfoot', 'tr',
}

CONTAINER_ONLY_TAGS = {
    'html', 'head', 'body', 'main', 'section', 'details',
    'dl', 'ul', 'ol', 'table', 'thead', 'tbody', 'tfoot', 'tr',
}


@dataclass
class DoctypeNode:
    text: str = 'DOCTYPE html'


@dataclass
class CommentNode:
    text: str


@dataclass
class VoidNode:
    tag: str
    attrs: list[tuple[str, str | None]] = field(default_factory=list)


@dataclass
class ElementNode:
    tag: str
    attrs: list[tuple[str, str | None]] = field(default_factory=list)
    children: list[Node] = field(default_factory=list)


Node = DoctypeNode | CommentNode | VoidNode | ElementNode | str


def format_attrs(attrs: list[tuple[str, str | None]]) -> str:
    """Serialize HTML attributes with double quotes and normalized escaping."""
    if not attrs:
        return ''
    parts: list[str] = []
    for key, value in attrs:
        if value is None:
            parts.append(key)
        else:
            escaped = (
                value.replace('&', '&amp;')
                .replace('"', '&quot;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
            )
            parts.append(f'{key}="{escaped}"')
    return ' ' + ' '.join(parts)


class HTMLTreeBuilder(HTMLParser):
    """Parse an HTML document into a lightweight structural AST."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.root = ElementNode('ROOT')
        self.stack: list[ElementNode] = [self.root]

    def _append_text(self, text: str) -> None:
        children = self.stack[-1].children
        if children and isinstance(children[-1], str):
            children[-1] += text
        else:
            children.append(text)

    def handle_decl(self, decl: str) -> None:
        self.stack[-1].children.append(DoctypeNode(decl.strip()))

    def handle_comment(self, data: str) -> None:
        self.stack[-1].children.append(CommentNode(data.strip()))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in VOID_TAGS:
            self.stack[-1].children.append(VoidNode(tag, list(attrs)))
            return
        element = ElementNode(tag, list(attrs))
        self.stack[-1].children.append(element)
        self.stack.append(element)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in VOID_TAGS:
            self.stack[-1].children.append(VoidNode(tag, list(attrs)))
        else:
            self.stack[-1].children.append(ElementNode(tag, list(attrs)))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in VOID_TAGS:
            return
        if len(self.stack) > 1 and self.stack[-1].tag == tag:
            self.stack.pop()
        else:
            for index in range(len(self.stack) - 1, 0, -1):
                if self.stack[index].tag == tag:
                    del self.stack[index:]
                    break

    def handle_data(self, data: str) -> None:
        self._append_text(data)

    def handle_entityref(self, name: str) -> None:
        self._append_text(f'&{name};')

    def handle_charref(self, name: str) -> None:
        self._append_text(f'&#{name};')


def is_inline_node(node: Node) -> bool:
    """Return True if a node belongs in an inline content run."""
    if isinstance(node, str):
        return True
    if isinstance(node, VoidNode):
        return node.tag in INLINE_TAGS
    if isinstance(node, ElementNode):
        return node.tag in INLINE_TAGS
    return False


def serialize_pre_inner(nodes: list[Node]) -> str:
    """Serialize children inside <pre> verbatim without altering whitespace."""
    parts: list[str] = []
    for node in nodes:
        if isinstance(node, str):
            parts.append(node)
        elif isinstance(node, VoidNode):
            parts.append(f'<{node.tag}{format_attrs(node.attrs)}>')
        elif isinstance(node, ElementNode):
            inner = serialize_pre_inner(node.children)
            parts.append(f'<{node.tag}{format_attrs(node.attrs)}>{inner}</{node.tag}>')
        elif isinstance(node, CommentNode):
            parts.append(f'<!-- {node.text} -->')
    return ''.join(parts)


def serialize_inline_node(node: Node) -> str:
    """Serialize a single inline node prior to line-wrap normalization."""
    if isinstance(node, str):
        return node
    if isinstance(node, VoidNode):
        return f'<{node.tag}{format_attrs(node.attrs)}>'
    if isinstance(node, ElementNode):
        inner = ''.join(serialize_inline_node(child) for child in node.children)
        inner = re.sub(r'^[ \t]*\n[ \t]*', '', inner)
        inner = re.sub(r'[ \t]*\n[ \t]*$', '', inner)
        if node.tag == 'a':
            inner = re.sub(r'</span>[ \t]*\n[ \t]*<span\b', '</span><span', inner)
        return f'<{node.tag}{format_attrs(node.attrs)}>{inner}</{node.tag}>'
    return ''


def format_inline_run(nodes: list[Node]) -> str:
    """Collapse source line wraps inside an inline run into a single clean line."""
    raw = ''.join(serialize_inline_node(node) for node in nodes)
    raw = re.sub(r'(<br\b[^>]*>)[ \t]*\n[ \t]*', r'\1', raw)
    raw = re.sub(r'(</span>)[ \t]*\n[ \t]*(<span\b)', r'\1\2', raw)
    raw = re.sub(r'[ \t]*\n[ \t]*', ' ', raw)
    return raw.strip()


def repair_list_children(node: ElementNode) -> None:
    """Ensure bare text lines inside <ul> or <ol> are wrapped in <li> elements."""
    if node.tag in ('ul', 'ol'):
        repaired: list[Node] = []
        for child in node.children:
            if isinstance(child, str) and child.strip():
                for line in child.splitlines():
                    stripped = line.strip()
                    if stripped:
                        repaired.append(ElementNode('li', [], [stripped]))
            else:
                repaired.append(child)
        node.children = repaired
    for child in node.children:
        if isinstance(child, ElementNode) and child.tag not in ('pre', 'script'):
            repair_list_children(child)


def render_block(node: Node, depth: int, lines: list[str]) -> None:
    """Render a block-level AST node into indented lines."""
    indent = INDENT_UNIT * depth

    if isinstance(node, DoctypeNode):
        lines.append(f'<!{node.text}>')
        return

    if isinstance(node, CommentNode):
        lines.append(f'{indent}<!-- {node.text} -->')
        return

    if isinstance(node, VoidNode):
        lines.append(f'{indent}<{node.tag}{format_attrs(node.attrs)}>')
        return

    if isinstance(node, str):
        stripped = format_inline_run([node])
        if stripped:
            lines.append(f'{indent}{stripped}')
        return

    tag = node.tag
    attrs = format_attrs(node.attrs)

    if tag == 'pre':
        inner = serialize_pre_inner(node.children)
        lines.append(f'{indent}<pre{attrs}>{inner}</pre>')
        return

    if tag == 'script':
        raw_script = ''.join(child for child in node.children if isinstance(child, str))
        raw_lines = raw_script.strip('\r\n').splitlines()
        if not raw_lines:
            lines.append(f'{indent}<script{attrs}></script>')
            return
        dedented = textwrap.dedent('\n'.join(raw_lines)).splitlines()
        lines.append(f'{indent}<script{attrs}>')
        body_indent = INDENT_UNIT * (depth + 1)
        for script_line in dedented:
            stripped_right = script_line.rstrip()
            lines.append(f'{body_indent}{stripped_right}' if stripped_right else '')
        lines.append(f'{indent}</script>')
        return

    has_block_child = any(not is_inline_node(child) for child in node.children)
    is_container = tag in CONTAINER_TAGS or has_block_child

    if not is_container:
        inline_text = format_inline_run(node.children)
        lines.append(f'{indent}<{tag}{attrs}>{inline_text}</{tag}>')
        return

    lines.append(f'{indent}<{tag}{attrs}>')
    inline_buffer: list[Node] = []

    def flush_inline() -> None:
        if not inline_buffer:
            return
        text = format_inline_run(inline_buffer)
        inline_buffer.clear()
        if text:
            lines.append(f'{INDENT_UNIT * (depth + 1)}{text}')

    for child in node.children:
        if is_inline_node(child):
            inline_buffer.append(child)
        else:
            flush_inline()
            render_block(child, depth + 1, lines)
    flush_inline()
    lines.append(f'{indent}</{tag}>')


def format_html(text: str) -> str:
    """Format an HTML document string into canonical structure and indentation."""
    normalized = text.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')
    builder = HTMLTreeBuilder()
    builder.feed(normalized)
    repair_list_children(builder.root)

    lines: list[str] = []
    for child in builder.root.children:
        if isinstance(child, str) and not child.strip():
            continue
        render_block(child, 0, lines)
    return '\n'.join(lines) + '\n'


def check_html_formatting(raw_bytes: bytes) -> list[str]:
    """Return formatting error descriptions for a single HTML file's raw bytes."""
    issues: list[str] = []
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        issues.append('contains UTF-8 BOM')
    if b'\r\n' in raw_bytes or b'\r' in raw_bytes:
        issues.append('contains CRLF/CR line endings (expected LF)')

    text = raw_bytes.decode('utf-8-sig')
    normalized = text.replace('\r\n', '\n').replace('\r', '\n')

    if not normalized.startswith('<!DOCTYPE html>\n'):
        issues.append('must start with <!DOCTYPE html> on line 1')
    if not normalized.endswith('\n') or normalized.endswith('\n\n'):
        issues.append('must end with a single trailing newline')

    # Strip <pre> blocks before checking line-level indentation and self-closing void tags
    outside_pre = re.sub(r'<pre\b[^>]*>.*?</pre>', '<pre></pre>', normalized, flags=re.S)
    for line_num, line in enumerate(outside_pre.splitlines(), 1):
        if line != line.rstrip(' \t'):
            issues.append(f'line {line_num}: trailing whitespace')
            break
    for line_num, line in enumerate(outside_pre.splitlines(), 1):
        leading = len(line) - len(line.lstrip(' \t'))
        prefix = line[:leading]
        if '\t' in prefix:
            issues.append(f'line {line_num}: tab indentation (expected 4 spaces)')
            break
        if leading % 4 != 0:
            issues.append(f'line {line_num}: indentation of {leading} spaces is not a multiple of 4')
            break

    void_pattern = r'<(?:' + '|'.join(sorted(VOID_TAGS)) + r')\b[^>]*/>'
    void_match = re.search(void_pattern, outside_pre, flags=re.I)
    if void_match:
        line_num = outside_pre[:void_match.start()].count('\n') + 1
        issues.append(f'line {line_num}: self-closing void tag {void_match.group(0)}')

    builder = HTMLTreeBuilder()
    builder.feed(normalized)

    def check_bare_text(node: ElementNode) -> None:
        if node.tag in CONTAINER_ONLY_TAGS:
            for child in node.children:
                if isinstance(child, str) and child.strip():
                    issues.append(f'<{node.tag}> contains unwrapped text outside child elements')
                    break
        for child in node.children:
            if isinstance(child, ElementNode) and child.tag not in ('pre', 'script'):
                check_bare_text(child)

    check_bare_text(builder.root)

    expected = format_html(normalized)
    if normalized != expected:
        actual_lines = normalized.splitlines()
        expected_lines = expected.splitlines()
        diff_line = 1
        for idx, (act, exp) in enumerate(zip(actual_lines, expected_lines), 1):
            if act != exp:
                diff_line = idx
                break
        else:
            diff_line = min(len(actual_lines), len(expected_lines)) + 1
        issues.append(
            f'line {diff_line}: non-canonical HTML structure/formatting '
            f'(run python tools/format_docs.py)'
        )

    return issues


def collect_html_files(targets: list[Path], default_root: Path) -> list[Path]:
    """Collect HTML files from target paths, excluding .history directories."""
    if not targets:
        targets = [default_root]
    found: list[Path] = []
    for target in targets:
        resolved = target.resolve()
        if resolved.is_file() and resolved.suffix.lower() == '.html':
            if '.history' not in resolved.parts:
                found.append(resolved)
        elif resolved.is_dir():
            for path in sorted(resolved.rglob('*.html')):
                if '.history' not in path.parts:
                    found.append(path.resolve())
    return sorted(set(found))


def main(argv: list[str] | None = None) -> int:
    """CLI entry point to format or check HTML documentation files."""
    parser = argparse.ArgumentParser(
        description='Format HTML documentation structures under reversing/docs.'
    )
    parser.add_argument(
        'paths',
        nargs='*',
        type=Path,
        help='Optional HTML files or directories to format (defaults to docs root).',
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check formatting without modifying files on disk.',
    )
    args = parser.parse_args(argv)

    docs_root = Path(__file__).resolve().parent.parent
    files = collect_html_files(args.paths, docs_root)

    changed_count = 0
    for path in files:
        raw_bytes = path.read_bytes()
        original = raw_bytes.decode('utf-8-sig')
        formatted = format_html(original)
        try:
            label = path.relative_to(docs_root).as_posix()
        except ValueError:
            label = path.as_posix()

        if raw_bytes != formatted.encode('utf-8'):
            changed_count += 1
            if args.check:
                issues = check_html_formatting(raw_bytes)
                detail = '; '.join(issues) if issues else 'formatting differs'
                print(f'UNFORMATTED: {label}: {detail}')
            else:
                path.write_text(formatted, encoding='utf-8', newline='\n')
                print(f'Formatted: {label}')

    if args.check:
        print(f'Checked {len(files)} HTML page(s): {changed_count} unformatted.')
        return 1 if changed_count else 0

    print(f'Formatted {changed_count} of {len(files)} HTML page(s).')
    return 0


if __name__ == '__main__':
    sys.exit(main())

