"""Refresh committed homepage coverage panels and map colours from one registry.

The published site stays plain HTML/CSS and works directly from file://.
"""

import argparse
from collections import Counter
from html import escape
import json
from pathlib import Path
import re

try:
    from format_docs import format_html
except ImportError:
    from .format_docs import format_html


ROOT = Path(__file__).resolve().parent.parent


def icon(colour: str, label: str) -> str:
    """Render an accessible status dot."""
    return (f'<span class="coverage-icon coverage-{escape(colour)}" '
            f'role="img" aria-label="{escape(label)}"></span>')


def render_panel(data: dict, platform: str) -> str:
    """Render the older vertical coverage list with platform-specific evidence."""
    name = data['platforms'][platform]['name']
    heading = (f'<span id="xbox360-title">{escape(name)}</span>'
               if platform == 'xbox360' else escape(name))
    title_id = 'format-coverage-title' if platform == 'ps3' else 'xbox360-format-coverage-title'
    legend_id = 'conversion-status-legend' if platform == 'ps3' else 'xbox360-conversion-status-legend'
    entries = [entry for entry in data['formats'] if platform in entry['platforms']]
    counts = Counter(entry['platforms'][platform]['colour'] for entry in entries)
    summary = '; '.join(f'{counts[colour]} {description["short"]}'
                        for colour, description in data['legend'].items())
    legend = ''.join(f'<li>{icon(colour, item["label"])}<strong>{escape(colour.title())}</strong> '
                     f'{escape(item["label"])}</li>' for colour, item in data['legend'].items())
    rows = []
    for entry in entries:
        status = entry['platforms'][platform]
        label = status.get('label', entry['label'])
        rows.append(f'''<li class="format-coverage-item" data-format-route="{escape(entry['route'])}" data-coverage-status="{escape(status['colour'])}">
{icon(status['colour'], status['status'])}<div><strong><a href="#{escape(entry['route'])}">{escape(label)}</a></strong>
<span class="coverage-status">{escape(status['status'])}</span><span class="coverage-detail">{escape(status['detail'])}</span></div></li>''')
    return f'''<section class="format-coverage" aria-labelledby="{title_id}">
<div class="format-coverage-heading"><h1 id="{title_id}">{heading}: Pipeline Format Coverage</h1>
<p>Format understanding and practical support at a glance. This homepage combines research progress with Remake Engine implementation progress; each entry states its limits.</p></div>
<p class="coverage-summary"><strong>{len(entries)} tracked format references</strong> · {escape(summary)}.</p>
<ul class="format-coverage-legend" id="{legend_id}" aria-label="{escape(name)} progress legend">{legend}</ul>
<p class="documentation-tree-note">Language variants and equivalent model suffixes are grouped. Counts describe the entries below, not a percentage of all game data understood. Green does not mean every field or original runtime behavior is recovered. Evidence last reviewed {escape(data['reviewed'])}.</p>
<ul class="format-coverage-list">{''.join(rows)}</ul>
<p><a href="#FormatAnalysis-relationships">Resource relationships</a> · <a href="#remake-integration">Implementation details</a> · <a href="#reference-sources">Reference sources</a></p></section>'''


def render_index(root: Path = ROOT) -> str:
    """Update only marked panels and map status adornments, preserving routes."""
    data = json.loads((root / 'reference/coverage.json').read_text(encoding='utf-8'))
    routes: dict[str, dict] = {}
    for entry in data['formats']:
        for route in [entry['route'], *entry.get('aliases', [])]:
            if route in routes:
                raise ValueError(f'Duplicate coverage route: {route}')
            routes[route] = entry
        for status in entry['platforms'].values():
            if status['colour'] not in data['legend']:
                raise ValueError(f'Unknown coverage colour: {status["colour"]}')
    text = (root / 'index.html').read_text(encoding='utf-8-sig')
    for platform in data['platforms']:
        marker = f'<!-- coverage:{platform}:start -->'
        ending = f'<!-- coverage:{platform}:end -->'
        if text.count(marker) != 1 or text.count(ending) != 1:
            raise ValueError(f'Missing or duplicate {platform} coverage markers')
        text = re.sub(re.escape(marker) + r'.*?' + re.escape(ending),
                      lambda _: marker + '\n' + render_panel(data, platform) + '\n' + ending,
                      text, flags=re.S)
    for platform in data['platforms']:
        marker = f'<!-- map:{platform}:start -->'
        ending = f'<!-- map:{platform}:end -->'
        if text.count(marker) != 1 or text.count(ending) != 1:
            raise ValueError(f'Missing or duplicate {platform} map markers')
        start = text.index(marker)
        stop = text.index(ending, start)
        section = text[start:stop]

        def adorn(match: re.Match) -> str:
            """Keep the label in the second grid column after a status dot."""
            opening, route, content = match.group(1), match.group(2), match.group(3)
            if 'format-status-link' not in opening:
                return match.group(0)
            entry = routes.get(route)
            status = entry['platforms'].get(platform) if entry else None
            if status is None:
                status = {'colour': 'grey', 'status': 'Reference group',
                          'detail': 'A suffix family or navigation group; see its individual resource references.'}
            content = re.sub(r'<span class="coverage-icon[^>]*></span>', '', content)
            opening = re.sub(r' (?:data-conversion-status|data-coverage-status|title)="[^"]*"', '', opening)
            opening += f' data-coverage-status="{escape(status["colour"])}" title="{escape(status["status"] + ": " + status["detail"])}"'
            return opening + '>' + icon(status['colour'], status['status']) + content.strip() + '</a>'

        section = re.sub(r'(<a\b[^>]*href="#([^"]+)"[^>]*?)>(.*?)</a>', adorn, section, flags=re.S)
        text = text[:start] + section + text[stop:]
    return format_html(text)


def main() -> int:
    """Refresh HTML or report stale coverage without modifying it."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    expected = render_index()
    path = ROOT / 'index.html'
    stale = path.read_bytes() != expected.encode('utf-8')
    if stale and not args.check:
        path.write_text(expected, encoding='utf-8', newline='\n')
    print('Homepage coverage: ' + ('stale' if stale and args.check else 'current'))
    return int(stale and args.check)


if __name__ == '__main__':
    raise SystemExit(main())
