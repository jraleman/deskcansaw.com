#!/usr/bin/env python3
"""Render the parts of the site that README.md owns.

README.md is the source of truth for content that would otherwise be written
twice. This script reads it and rewrites the matching generated blocks in the
HTML pages, which stay checked in — the site is still static files with no
build step in front of it. Run it after editing README.md:

    python3 tools/build.py            # rewrite the pages
    python3 tools/build.py --check    # exit 1 if they are out of date

What it owns, by block name:

    profile      the Gamer Profile section body
    games        one card per game in "### List of games:"
    statuses     the status table under "## Games"
    file-kinds   one card per bullet under "## Files"
    file-rules   the numbered rules under "## Files"

Everything between <!-- generated:NAME --> and <!-- /generated:NAME --> is
replaced; everything else in the page is written by hand and left alone.
"""

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / 'README.md'
PAGES = [ROOT / 'preview.html']

# A game's status decides its badge (style-guide.md §6.5) and whether the card
# is a link. Order is the order they appear on the page.
STATUS = {
    'released':  'badge badge-released',
    'playable':  'tag',
    'prototype': 'badge badge-neutral',
    'concept':   'badge badge-neutral',
    'abandoned': 'badge badge-neutral',
}
STATUS_ORDER = list(STATUS)
ITCH = 'https://deskcansaw.itch.io'


# --------------------------------------------------------------------------
# Markdown — only the small subset this README uses.
# --------------------------------------------------------------------------

def inline(md):
    """Inline markdown -> HTML. Links, code, bold, and bare URLs."""
    def text(t):
        # quote=False: these are text nodes, so ' and " stay readable.
        return html.escape(t, quote=False)

    out = []
    pos = 0
    pattern = re.compile(
        r'\[(?P<text>[^\]]+)\]\((?P<url>[^)]+)\)'      # [text](url)
        r'|`(?P<code>[^`]+)`'                          # `code`
        r'|\*\*(?P<bold>[^*]+)\*\*'                    # **bold**
        r'|(?P<url_bare>https?://[^\s<>()]+)'          # bare URL
    )
    for m in pattern.finditer(md):
        out.append(text(md[pos:m.start()]))
        if m.group('text') is not None:
            out.append('<a href="{}"{}>{}</a>'.format(
                html.escape(m.group('url')),
                ' rel="noopener"' if '://' in m.group('url') else '',
                text(m.group('text'))))
        elif m.group('code') is not None:
            out.append('<code>{}</code>'.format(text(m.group('code'))))
        elif m.group('bold') is not None:
            out.append('<strong>{}</strong>'.format(text(m.group('bold'))))
        else:
            url = m.group('url_bare')
            out.append('<a href="{}" rel="noopener">{}</a>'.format(
                html.escape(url), text(url)))
        pos = m.end()
    out.append(text(md[pos:]))
    return ''.join(out)


OL_ITEM = re.compile(r'^\d+\.\s+')


def blocks(md):
    """Split a markdown section into ('kind', payload) blocks, in order."""
    lines = md.splitlines()
    found, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            found.append(('heading', (level, line.lstrip('#').strip())))
            i += 1
        elif line.lstrip().startswith(('- ', '* ')):
            items = []
            while i < len(lines) and lines[i].lstrip().startswith(('- ', '* ')):
                items.append(lines[i].lstrip()[2:].strip())
                i += 1
            found.append(('list', items))
        elif OL_ITEM.match(line.lstrip()):
            items = []
            while i < len(lines) and OL_ITEM.match(lines[i].lstrip()):
                items.append(OL_ITEM.sub('', lines[i].lstrip()).strip())
                i += 1
            found.append(('olist', items))
        elif line.lstrip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(set(c) <= set('-: ') and c for c in cells):
                    rows.append(cells)
                i += 1
            found.append(('table', rows))
        else:
            para = []
            while i < len(lines) and lines[i].strip() \
                    and not lines[i].startswith('#') \
                    and not lines[i].lstrip().startswith(('- ', '* ', '|')) \
                    and not OL_ITEM.match(lines[i].lstrip()):
                para.append(lines[i].strip())
                i += 1
            found.append(('paragraph', ' '.join(para)))
    return found


def section(md, heading):
    """The body of a '## heading' section, up to the next '## '."""
    m = re.search(r'^##\s+' + re.escape(heading) + r'.*$', md, re.M)
    if not m:
        raise SystemExit('README.md: no "## {}" section'.format(heading))
    rest = md[m.end():]
    nxt = re.search(r'^##\s', rest, re.M)
    return rest[:nxt.start()] if nxt else rest


# --------------------------------------------------------------------------
# Renderers — one per generated block.
# --------------------------------------------------------------------------

def indent(lines, pad):
    return '\n'.join(pad + l if l else '' for l in lines)


def render_table(rows, pad, cell=None):
    """rows[0] is the header. `cell(index, text)` may return ready-made HTML."""
    cell = cell or (lambda i, text: inline(text))
    head, body = rows[0], rows[1:]
    out = ['<div class="table-wrap">', '  <table>', '    <thead>', '      <tr>']
    out += ['        <th scope="col">{}</th>'.format(inline(c)) for c in head]
    out += ['      </tr>', '    </thead>', '    <tbody>']
    for row in body:
        out.append('      <tr>')
        out += ['        <td>{}</td>'.format(cell(i, c)) for i, c in enumerate(row)]
        out.append('      </tr>')
    out += ['    </tbody>', '  </table>', '</div>']
    return indent(out, pad)


def render_profile(md, pad):
    """The Gamer Profile section body: paragraphs, the setup table, the list."""
    out = []
    for kind, payload in blocks(section(md, 'Gamer Profile')):
        if kind == 'paragraph':
            out.append('<p>{}</p>'.format(inline(payload)))
        elif kind == 'heading':
            _, text = payload
            out.append('<h3>{}</h3>'.format(inline(text)))
        elif kind in ('list', 'olist'):
            tag = 'ol' if kind == 'olist' else 'ul'
            out.append('<{}>'.format(tag))
            out += ['  <li>{}</li>'.format(inline(i)) for i in payload]
            out.append('</{}>'.format(tag))
        elif kind == 'table':
            out.append(render_table(payload, '').lstrip())
    return indent('\n'.join(out).splitlines(), pad)


GAME = re.compile(
    r'^(?:\[(?P<linked>[^\]]+)\]\((?P<url>[^)]+)\)|(?P<name>[^(\[]+?))'
    r'\s*\(`(?P<status>\w+)`\)\s*:\s*(?P<desc>.+)$'
)


def games(md):
    body = section(md, 'Games')
    listing = re.search(r'^###\s+List of games:?\s*$(.*)', body, re.M | re.S)
    if not listing:
        raise SystemExit('README.md: no "### List of games:" list')
    out = []
    for kind, payload in blocks(listing.group(1)):
        if kind != 'list':
            continue
        for item in payload:
            m = GAME.match(item)
            if not m:
                raise SystemExit('README.md: cannot parse game line: ' + item)
            status = m.group('status')
            if status not in STATUS:
                raise SystemExit('README.md: unknown status "{}" on: {}'.format(status, item))
            out.append({
                'name': (m.group('linked') or m.group('name')).strip(),
                'url': m.group('url'),
                'status': status,
                'desc': m.group('desc').strip(),
            })
    out.sort(key=lambda g: STATUS_ORDER.index(g['status']))
    return out


def render_games(md, pad):
    out = []
    for g in games(md):
        # A released game has somewhere to go; the rest are not links yet.
        href = g['url'] or (ITCH if g['status'] == 'released' else None)
        open_tag = '<a class="card" href="{}" rel="noopener">'.format(html.escape(href)) \
            if href else '<div class="card">'
        out += [
            open_tag,
            '  <div class="card-head">',
            '    <h3>{}</h3>'.format(inline(g['name'])),
            '    <span class="{}">{}</span>'.format(STATUS[g['status']], g['status']),
            '  </div>',
            '  <p>{}</p>'.format(inline(g['desc'])),
            '</a>' if href else '</div>',
        ]
    return indent(out, pad)


def render_statuses(md, pad):
    def cell(i, text):
        if i:
            return inline(text)
        key = text.strip('`')
        if key not in STATUS:
            raise SystemExit('README.md: unknown status "{}" in the table'.format(key))
        return '<span class="{}">{}</span>'.format(STATUS[key], key)

    for kind, payload in blocks(section(md, 'Games')):
        if kind == 'table' and payload[0][0].lower() == 'status':
            return render_table(payload, pad, cell=cell)
    raise SystemExit('README.md: no status table under "## Games"')


KIND = re.compile(r'^\*\*(?P<name>[^*]+)\*\*\s*[\u2014\u2013-]+\s*(?P<desc>.+)$')


def render_file_kinds(md, pad):
    """One card per "**Kind** — what it is" bullet under "## Files"."""
    for kind, payload in blocks(section(md, 'Files')):
        if kind != 'list':
            continue
        out = []
        for item in payload:
            m = KIND.match(item)
            if not m:
                raise SystemExit('README.md: cannot parse file kind: ' + item)
            out += [
                '<div class="card">',
                '  <h4>{}</h4>'.format(inline(m.group('name').strip())),
                '  <p>{}</p>'.format(inline(m.group('desc').strip())),
                '</div>',
            ]
        return indent(out, pad)
    raise SystemExit('README.md: no "**Kind** — description" list under "## Files"')


def render_file_rules(md, pad):
    """The numbered rules under "## Files", in a well (§4, §6.6)."""
    for kind, payload in blocks(section(md, 'Files')):
        if kind != 'olist':
            continue
        out = ['<div class="well">', '  <ol class="rules">']
        out += ['    <li>{}</li>'.format(inline(i)) for i in payload]
        out += ['  </ol>', '</div>']
        return indent(out, pad)
    raise SystemExit('README.md: no numbered rules under "## Files"')


BLOCKS = {
    'profile': render_profile,
    'games': render_games,
    'statuses': render_statuses,
    'file-kinds': render_file_kinds,
    'file-rules': render_file_rules,
}


# --------------------------------------------------------------------------

def build(page, md):
    src = original = page.read_text()
    for name, render in BLOCKS.items():
        marker = re.compile(
            r'(?P<pad>[ \t]*)<!-- generated:{0} -->.*?<!-- /generated:{0} -->'
            .format(name), re.S)
        m = marker.search(src)
        if not m:
            continue
        pad = m.group('pad')
        replacement = '{p}<!-- generated:{n} -->\n{body}\n{p}<!-- /generated:{n} -->'.format(
            p=pad, n=name, body=render(md, pad))
        src = src[:m.start()] + replacement + src[m.end():]
    return src, original


def main(argv):
    check = '--check' in argv
    md = README.read_text()
    stale = []
    for page in PAGES:
        built, original = build(page, md)
        if built == original:
            continue
        if check:
            stale.append(page.name)
        else:
            page.write_text(built)
            print('wrote', page.relative_to(ROOT))
    if check and stale:
        print('out of date (run tools/build.py):', ', '.join(stale), file=sys.stderr)
        return 1
    if check:
        print('up to date')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
