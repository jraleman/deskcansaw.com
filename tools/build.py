#!/usr/bin/env python3
"""Render the parts of the site that content/site.json owns.

content/site.json is the source of truth for content that would otherwise be
written twice. This script reads it and rewrites the matching generated blocks
in the HTML pages, which stay checked in, so the pages are static files with no
build step in front of them. The games are the one exception:
tools/export_games.py exports them into play/ from the dcs_games submodule, and
the deploy runs it. Run this after editing the content file:

    python3 tools/build.py            # rewrite the pages
    python3 tools/build.py --check    # exit 1 if they are out of date

What it owns, by block name, and what each block reads:

    profile      content/site.json "profile"           the Gamer Profile body
    game-filters catalog games + game_cards            genres, modes and count
    games        dcs_games' project.godot + game_cards one card per game
    downloads    tools/catalog.py "DESKTOPS"           the collection, to keep
    file-kinds   content/site.json "files.kinds"       one card per kind of file
    file-rules   content/site.json "files.rules"       the numbered rules
    videos       content/site.json "videos.featured"   one embed per video
    streams      content/site.json "videos.streams"    the live archive, by game

Everything between <!-- generated:NAME --> and <!-- /generated:NAME --> is
replaced; everything else in the page is written by hand and left alone. A
page only gets the blocks it has markers for. The content file holds the
lists and tables, which are the parts that would otherwise drift apart; the
prose around them is written per page.

The list of games is not in the content file: tools/catalog.py reads it from
dcs_games' project.godot, so adding a game there puts it on the site.
"game_cards" adds website copy, artwork descriptions, genres and play modes,
keyed by game id; it never determines which games appear or their order.
Artwork is a checked-in 640x640 WebP at assets/img/games/<slug>.webp, resized
from the game's assets/cover.png without cropping. Building the page never
needs to read a private game folder.

The content file:

    {
      "profile": [<block>, ...],
      "game_cards": {
        "<game_id>": {
          "description": ..., "alt": ...,
          "genres": ["Arcade"], "modes": ["solo", "local"]
        }
      },
      "files": {
        "kinds": [{"name": ..., "description": ...}, ...],
        "rules": [<rule>, ...]
      },
      "videos": {
        "featured": [{"id": ..., "title": ..., "caption": ...}, ...],
        "streams": [{"game": ..., "sessions": [{"id": ..., "label": ..., "date": ...}, ...]}, ...]
      }
    }

An "id" anywhere under "videos" is the 11-character YouTube id, not the watch
URL it came out of: the page builds the embed and the link from it, so the two
cannot point at different videos. Under "streams", a game is a card and its
"sessions" are listed in the order they are written -- oldest first, so a
playthrough reads top to bottom -- and each "date" is the YYYY-MM-DD it went
up, which is what tells two streams of the same episode apart.

A <block> under "profile" is one of these, rendered in the order they are
written:

    {"type": "paragraph", "text": ...}
    {"type": "heading",   "text": ...}
    {"type": "list",      "items": [...]}                      a <ul>
    {"type": "olist",     "items": [...]}                      an <ol>
    {"type": "table",     "columns": [...], "rows": [[...]]}
    {"type": "intro",     "lead": ..., "text": ...}
    {"type": "favorites", "text": ...,
     "items": [{"name": ..., "platform": ..., "note": ...}]}
    {"type": "setup",     "text": ..., "items": [{"name": ..., "note": ...}]}

Favorites and setup items have optional notes; omit the key when no personal
note or device detail is supplied. Their shared "text" introduces the list.
Leave out the setup block entirely when there is no hardware to publish.
An intro or favorites/setup item can also have an optional "image":

    {"src": "/assets/img/...", "alt": ..., "width": 512, "height": 512,
     "credit": {"title": ..., "author": ..., "source": "https://...",
                "license": ..., "license_url": "https://...", "changes": ...}}

Images must be checked-in local files; dimensions are positive integers.
The alt field is required but can be empty for a decorative illustration.
Third-party images carry a credit, with optional modification notes in
"changes". Credits are collected below the profile, without network access.
Platform labels are plain text. Other profile text takes the small inline
markdown the site uses -- links, `code`, **bold** and bare URLs -- and
everything else in it is escaped.
Game card titles, descriptions and alt text are plain text; only the launch
control is a link.
Genres are non-empty labels; the filter choices come from the active catalog.
Modes are solo (one human, including vs CPU), local (shared-device multiplayer)
or online (networked multiplayer, not simply running in a browser).
"""

import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import catalog  # noqa: E402 -- the games, read out of dcs_games

ROOT = catalog.ROOT
CONTENT = ROOT / 'content' / 'site.json'
CONTENT_NAME = 'content/site.json'   # how the content file is named in errors
PAGES = [ROOT / 'index.html']


# --------------------------------------------------------------------------
# Inline markdown — the small subset the content file's text takes.
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


# --------------------------------------------------------------------------
# The content file — read it, check it says what the renderers need, and tidy
# the whitespace. Every complaint names the path it came from, so a typo
# points at the line to fix instead of at a traceback.
# --------------------------------------------------------------------------

PROFILE_BLOCKS = ('paragraph', 'heading', 'list', 'olist', 'table',
                  'intro', 'favorites', 'setup')

# A YouTube id, and the two URLs the page builds out of one.
VIDEO_ID = re.compile(r'[A-Za-z0-9_-]{11}\Z')
DATE = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}\Z')
EMBED_URL = 'https://www.youtube-nocookie.com/embed/{}'
WATCH_URL = 'https://www.youtube.com/watch?v={}'

PLAY_MODES = {
    'solo': 'Single-player',
    'local': 'Local multiplayer',
    'online': 'Online multiplayer',
}


def fail(where, message):
    raise SystemExit('{}: {}: {}'.format(CONTENT_NAME, where, message))


def want_key(where, obj, name):
    """obj[name], or a complaint that `where` is missing it."""
    if not isinstance(obj, dict) or name not in obj:
        fail(where, 'has no "{}"'.format(name))
    return obj[name]


def want_text(where, value):
    """A non-empty string, stripped."""
    if not isinstance(value, str) or not value.strip():
        fail(where, 'must be a non-empty string')
    return value.strip()


def want_list(where, value, of=dict):
    """A non-empty list of `of`."""
    names = {dict: 'an object', str: 'a string', list: 'a list'}
    if not isinstance(value, list) or not value:
        fail(where, 'must be a non-empty list')
    for i, item in enumerate(value):
        if not isinstance(item, of):
            fail('{}[{}]'.format(where, i), 'must be ' + names[of])
    return value


def want_table(where, table):
    """A {"columns": [...], "rows": [[...], ...]} with rows the right width."""
    columns = [want_text('{}.columns[{}]'.format(where, i), c)
               for i, c in enumerate(want_list(where + '.columns', table.get('columns'), of=str))]
    rows = []
    for i, row in enumerate(want_list(where + '.rows', table.get('rows'), of=list)):
        at = '{}.rows[{}]'.format(where, i)
        if len(row) != len(columns):
            fail(at, 'has {} cell(s), and the table has {} column(s)'.format(
                len(row), len(columns)))
        for j, cell in enumerate(row):
            if not isinstance(cell, str):     # an empty cell is fine; a number is not
                fail('{}[{}]'.format(at, j), 'must be a string')
        rows.append([cell.strip() for cell in row])
    return columns, rows


def want_video_id(where, value):
    """The 11-character YouTube id, so a pasted watch URL is caught here."""
    vid = want_text(where, value)
    if not VIDEO_ID.match(vid):
        fail(where, 'must be an 11-character YouTube video id, not {!r}'.format(vid))
    return vid


def check_profile_image(where, owner):
    if 'image' not in owner:
        return
    at = where + '.image'
    image = owner['image']
    if not isinstance(image, dict):
        fail(at, 'must be an object with "src", "alt", "width" and "height"')
    src = image['src'] = want_text(at + '.src', image.get('src'))
    if (not re.fullmatch(r'/assets/img/[A-Za-z0-9_./-]+\.(?:png|jpe?g|webp|svg)', src)
            or '..' in src.split('/')):
        fail(at + '.src', 'must name a local image under /assets/img/, without traversal or query strings')
    path = ROOT.joinpath(*src.lstrip('/').split('/')).resolve()
    try:
        path.relative_to((ROOT / 'assets' / 'img').resolve())
    except ValueError:
        fail(at + '.src', 'must stay inside assets/img')
    if not path.is_file():
        fail(at + '.src', 'image is missing: ' + src)
    if not isinstance(image.get('alt'), str):
        fail(at + '.alt', 'must be a string; use "" for a decorative image')
    image['alt'] = image['alt'].strip()
    for field in ('width', 'height'):
        if type(image.get(field)) is not int or image[field] <= 0:
            fail(at + '.' + field, 'must be a positive integer')
    if 'credit' not in image:
        return
    credit = image['credit']
    at += '.credit'
    if not isinstance(credit, dict):
        fail(at, 'must be an object with the title, author, source and license')
    for field in ('title', 'author', 'source', 'license', 'license_url'):
        credit[field] = want_text(at + '.' + field, credit.get(field))
    for field in ('source', 'license_url'):
        value = credit[field]
        try:
            url = urlsplit(value)
        except ValueError:
            fail(at + '.' + field, 'must be an absolute HTTP or HTTPS URL')
        if (url.scheme not in ('http', 'https') or not url.netloc
                or any(c.isspace() for c in value)):
            fail(at + '.' + field, 'must be an absolute HTTP or HTTPS URL')
    if 'changes' in credit:
        credit['changes'] = want_text(at + '.changes', credit['changes'])


def check_profile(content):
    for i, block in enumerate(want_list('profile', want_key('the file', content, 'profile'))):
        at = 'profile[{}]'.format(i)
        kind = block['type'] = want_text(at + '.type', block.get('type'))
        if kind not in PROFILE_BLOCKS:
            fail(at, 'unknown type "{}"; one of {}'.format(kind, ', '.join(PROFILE_BLOCKS)))
        if kind in ('paragraph', 'heading'):
            block['text'] = want_text(at + '.text', block.get('text'))
        elif kind == 'intro':
            for field in ('lead', 'text'):
                block[field] = want_text(at + '.' + field, block.get(field))
            check_profile_image(at, block)
        elif kind in ('list', 'olist'):
            block['items'] = [want_text('{}.items[{}]'.format(at, j), item) for j, item
                              in enumerate(want_list(at + '.items', block.get('items'), of=str))]
        elif kind in ('favorites', 'setup'):
            block['text'] = want_text(at + '.text', block.get('text'))
            for j, item in enumerate(want_list(at + '.items', block.get('items'))):
                item_at = '{}.items[{}]'.format(at, j)
                fields = ('name', 'platform') if kind == 'favorites' else ('name',)
                for field in fields:
                    item[field] = want_text(item_at + '.' + field, item.get(field))
                if 'note' in item:
                    item['note'] = want_text(item_at + '.note', item['note'])
                check_profile_image(item_at, item)
        else:
            block['columns'], block['rows'] = want_table(at, block)


def check_game_cards(content):
    cards = want_key('the file', content, 'game_cards')
    if not isinstance(cards, dict):
        fail('game_cards', 'must be an object keyed by game id')
    for game_id, card in cards.items():
        at = 'game_cards.' + game_id
        if not isinstance(card, dict):
            fail(at, 'must be an object with "description", "alt", "genres" and "modes"')
        card['description'] = want_text(at + '.description', card.get('description'))
        card['alt'] = want_text(at + '.alt', card.get('alt'))
        for field in ('genres', 'modes'):
            where = at + '.' + field
            values = [want_text('{}[{}]'.format(where, i), value) for i, value
                      in enumerate(want_list(where, card.get(field), of=str))]
            if len({value.casefold() for value in values}) != len(values):
                fail(where, 'must not contain duplicate values')
            if field == 'modes':
                for value in values:
                    if value not in PLAY_MODES:
                        fail(where, 'unknown mode {!r}; one of {}'.format(
                            value, ', '.join(PLAY_MODES)))
            card[field] = values

    for game in content['games']:
        game_id = game['id']
        if game_id not in cards:
            catalog.warn('{}: game_cards.{} is missing; rendering a title-only card'.format(
                CONTENT_NAME, game_id))
            continue
        image = 'assets/img/games/{}.webp'.format(game['slug'])
        if not (ROOT / image).is_file():
            fail('game_cards.' + game_id, 'artwork is missing: ' + image)
        game['card'] = dict(cards[game_id], image='/' + image)


def check_files(content):
    files = want_key('the file', content, 'files')
    if not isinstance(files, dict):
        fail('files', 'must be an object with "kinds" and "rules"')
    for i, kind in enumerate(want_list('files.kinds', files.get('kinds'))):
        at = 'files.kinds[{}]'.format(i)
        kind['name'] = want_text(at + '.name', kind.get('name'))
        kind['description'] = want_text(at + '.description', kind.get('description'))
    files['rules'] = [want_text('files.rules[{}]'.format(i), rule) for i, rule
                      in enumerate(want_list('files.rules', files.get('rules'), of=str))]


def check_videos(content):
    videos = want_key('the file', content, 'videos')
    if not isinstance(videos, dict):
        fail('videos', 'must be an object with "featured" and "streams"')
    for i, video in enumerate(want_list('videos.featured', videos.get('featured'))):
        at = 'videos.featured[{}]'.format(i)
        video['id'] = want_video_id(at + '.id', video.get('id'))
        video['title'] = want_text(at + '.title', video.get('title'))
        video['caption'] = want_text(at + '.caption', video.get('caption'))
    seen = {}
    for i, group in enumerate(want_list('videos.streams', videos.get('streams'))):
        at = 'videos.streams[{}]'.format(i)
        group['game'] = want_text(at + '.game', group.get('game'))
        for j, session in enumerate(want_list(at + '.sessions', group.get('sessions'))):
            here = '{}.sessions[{}]'.format(at, j)
            vid = session['id'] = want_video_id(here + '.id', session.get('id'))
            if vid in seen:
                fail(here + '.id', 'is already under "{}"'.format(seen[vid]))
            seen[vid] = group['game']
            session['label'] = want_text(here + '.label', session.get('label'))
            session['date'] = want_text(here + '.date', session.get('date'))
            if not DATE.match(session['date']):
                fail(here + '.date', 'must be a YYYY-MM-DD date')


def load():
    """What the pages are rendered from: the content file, and the games.

    "games" is not in the content file -- it comes out of the dcs_games Godot
    project, so a game is on the site because it is in the project.
    """
    try:
        raw = CONTENT.read_text(encoding='utf-8')
    except OSError as e:
        raise SystemExit('{}: cannot read it: {}'.format(CONTENT_NAME, e.strerror))
    try:
        content = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit('{}: line {}, column {}: {}'.format(CONTENT_NAME, e.lineno, e.colno, e.msg))
    if not isinstance(content, dict):
        fail('the file', 'must be an object with "profile", "game_cards", "files" and "videos"')
    check_profile(content)
    check_files(content)
    check_videos(content)
    content['games'] = catalog.games()
    check_game_cards(content)
    return content


# --------------------------------------------------------------------------
# Renderers — one per generated block.
# --------------------------------------------------------------------------

def indent(lines, pad):
    return '\n'.join(pad + l if l else '' for l in lines)


def render_table(rows, pad):
    """rows[0] is the header; the rest are the body, in order."""
    head, body = rows[0], rows[1:]
    out = ['<div class="table-wrap">', '  <table>', '    <thead>', '      <tr>']
    out += ['        <th scope="col">{}</th>'.format(inline(c)) for c in head]
    out += ['      </tr>', '    </thead>', '    <tbody>']
    for row in body:
        out.append('      <tr>')
        out += ['        <td>{}</td>'.format(inline(c)) for c in row]
        out.append('      </tr>')
    out += ['    </tbody>', '  </table>', '</div>']
    return indent(out, pad)


def render_profile(content, pad):
    """The personal gaming shelf, plus any additional prose or tables."""
    out = []
    credits = []

    def add_image(owner, css_class, padding):
        if 'image' not in owner:
            return
        image = owner['image']
        out.append(
            '{}<img class="{}" src="{}" alt="{}" width="{}" height="{}" '
            'loading="lazy" decoding="async">'.format(
                padding, css_class, html.escape(image['src']), html.escape(image['alt']),
                image['width'], image['height']))
        if 'credit' in image and image['credit'] not in credits:
            credits.append(image['credit'])

    for block in content['profile']:
        kind = block['type']
        if kind == 'paragraph':
            out.append('<p>{}</p>'.format(inline(block['text'])))
        elif kind == 'heading':
            out.append('<h3>{}</h3>'.format(inline(block['text'])))
        elif kind in ('list', 'olist'):
            tag = 'ol' if kind == 'olist' else 'ul'
            out.append('<{}>'.format(tag))
            out += ['  <li>{}</li>'.format(inline(i)) for i in block['items']]
            out.append('</{}>'.format(tag))
        elif kind == 'table':
            out.append(render_table([block['columns']] + block['rows'], '').lstrip())
        elif kind == 'intro':
            css_class = 'card profile-intro'
            if 'image' in block:
                css_class += ' profile-intro-with-image'
            out.append('<div class="{}">'.format(css_class))
            add_image(block, 'profile-media profile-avatar', '  ')
            out += [
                '  <p class="profile-lead">{}</p>'.format(inline(block['lead'])),
                '  <p>{}</p>'.format(inline(block['text'])),
                '</div>',
            ]
        elif kind in ('favorites', 'setup'):
            favorites = kind == 'favorites'
            wrapper = 'profile-favorites' if favorites else 'card profile-setup'
            title = 'Favorites' if favorites else 'What I play on'
            grid = ('grid grid-2 profile-favorite-list' if favorites
                    else 'grid grid-3 profile-device-list')
            item_class = 'card profile-favorite' if favorites else 'profile-device'
            out += [
                '<div class="{}">'.format(wrapper),
                '  <h3>{}</h3>'.format(title),
                '  <p class="profile-section-note">{}</p>'.format(inline(block['text'])),
                '  <ul class="{}" role="list">'.format(grid),
            ]
            for item in block['items']:
                css_class = item_class
                if not favorites and 'image' in item:
                    css_class += ' profile-device-with-image'
                out.append('    <li class="{}">'.format(css_class))
                add_image(item, 'profile-media ' + (
                    'profile-thumbnail' if favorites else 'profile-hardware-image'), '      ')
                out += [
                    '      <div class="profile-item-copy">',
                    '        <h4>{}</h4>'.format(inline(item['name'])),
                ]
                if favorites:
                    out.append('        <span class="badge badge-neutral">{}</span>'.format(
                        html.escape(item['platform'])))
                if 'note' in item:
                    out.append('        <p class="profile-note">{}</p>'.format(inline(item['note'])))
                out += ['      </div>', '    </li>']
            out += ['  </ul>', '</div>']
    if credits:
        out += [
            '<details class="profile-image-credits">',
            '  <summary>Image credits</summary>',
            '  <ul>',
        ]
        for credit in credits:
            line = '    <li><a href="{}" rel="noopener">{}</a> by {}; '.format(
                html.escape(credit['source']), html.escape(credit['title']),
                html.escape(credit['author']))
            line += '<a href="{}" rel="noopener">{}</a>.'.format(
                html.escape(credit['license_url']), html.escape(credit['license']))
            if 'changes' in credit:
                line += ' ' + html.escape(credit['changes'])
            out.append(line + '</li>')
        out += ['  </ul>', '</details>']
    return indent('\n'.join(out).splitlines(), pad)


def render_game_filters(content, pad):
    """Filter choices follow the catalog, not unused card metadata."""
    genres = sorted({genre for g in content['games'] if g.get('card')
                     for genre in g['card']['genres']}, key=str.casefold)
    modes = [('solo', PLAY_MODES['solo']), ('multiplayer', 'Any multiplayer')]
    modes += [(key, label) for key, label in PLAY_MODES.items() if key != 'solo']
    total = len(content['games'])
    out = [
        '<form id="game-filters" class="game-filters" aria-label="Filter games" hidden>',
        '  <div class="game-filter-fields">',
        '    <label class="game-filter-search" for="game-query">Search games',
        '      <input id="game-query" name="q" type="search" placeholder="Title or keyword"',
        '             autocomplete="off" aria-controls="game-grid">',
        '    </label>',
        '    <label for="game-genre">Genre',
        '      <select id="game-genre" name="genre" aria-controls="game-grid">',
        '        <option value="">All genres</option>',
    ]
    out += ['        <option value="{0}">{0}</option>'.format(html.escape(genre))
            for genre in genres]
    out += [
        '      </select>',
        '    </label>',
        '    <label for="game-mode">Play mode',
        '      <select id="game-mode" name="mode" aria-controls="game-grid" aria-describedby="game-mode-help">',
        '        <option value="">All play modes</option>',
    ]
    out += ['        <option value="{}">{}</option>'.format(key, html.escape(label))
            for key, label in modes]
    out += [
        '      </select>',
        '    </label>',
        '  </div>',
        '  <p id="game-mode-help" class="meta game-filter-help">Local shares one device. '
        'Online means multiplayer over the internet.</p>',
        '  <div class="game-filter-summary">',
        '    <p id="game-results" class="meta" role="status" aria-live="polite" aria-atomic="true">{} game{}</p>'.format(
            total, '' if total == 1 else 's'),
        '    <button class="btn btn-secondary" type="reset">Clear filters</button>',
        '  </div>',
        '</form>',
    ]
    return indent(out, pad)


def render_games(content, pad):
    """One non-interactive card per game, with a dedicated launch link."""
    out = []
    for g in content['games']:
        slug = html.escape(g['slug'])
        name = html.escape(g['name'])
        card = g.get('card')
        describedby = ' aria-describedby="game-{}-description"'.format(slug) if card else ''
        genres = card['genres'] if card else []
        modes = card['modes'] if card else []
        out += [
            '<article class="card game-card" data-genres="{}" data-modes="{}"'.format(
                html.escape(json.dumps(genres)), ' '.join(modes)),
            '         aria-labelledby="game-{}">'.format(slug),
        ]
        if card:
            out += [
                '  <img class="game-card-art" src="{}"'.format(html.escape(card['image'])),
                '       alt="{}" width="640" height="640" loading="lazy" decoding="async">'.format(
                    html.escape(card['alt'])),
            ]
        out += [
            '  <div class="game-card-body">',
            '    <h3 id="game-{}">{}</h3>'.format(slug, name),
        ]
        if card:
            out.append('    <div class="game-card-tags">')
            out += ['      <span class="tag">{}</span>'.format(html.escape(genre))
                    for genre in genres]
            out += [
                '    </div>',
                '    <p id="game-{}-description">{}</p>'.format(
                    slug, html.escape(card['description'], quote=False)),
                '    <p class="game-card-modes">{}</p>'.format(
                    ' &middot; '.join(PLAY_MODES[mode] for mode in modes)),
            ]
        out += [
            '  </div>',
            '  <div class="game-card-action">',
            '    <a class="btn game-card-launch" href="/play/{}/"'.format(slug),
            '       aria-label="Launch game: {}"{}>'.format(name, describedby),
            '      <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" '
            'aria-hidden="true" focusable="false">',
            '        <path d="M8 5v14l11-7z"/>',
            '      </svg>',
            '      <span>Launch game</span>',
            '    </a>',
            '  </div>',
            '</article>',
        ]
    return indent(out, pad)


def render_downloads(content, pad):
    """One button per desktop build of the collection, from tools/catalog.py.

    The play shell offers the same ones, from the same list, so the two can't
    drift apart; tools/export_games.py is what puts the files there.
    """
    return indent(['<div class="actions">']
                  + catalog.download_links('  ').splitlines()
                  + ['</div>'], pad)


def render_file_kinds(content, pad):
    """One card per kind of file in the archive."""
    out = []
    for kind in content['files']['kinds']:
        out += [
            '<div class="card">',
            '  <h4>{}</h4>'.format(inline(kind['name'])),
            '  <p>{}</p>'.format(inline(kind['description'])),
            '</div>',
        ]
    return indent(out, pad)


def render_file_rules(content, pad):
    """The rules for the Files section, numbered, in a well (§4, §6.6)."""
    out = ['<div class="well">', '  <ol class="rules">']
    out += ['    <li>{}</li>'.format(inline(rule)) for rule in content['files']['rules']]
    out += ['  </ol>', '</div>']
    return indent(out, pad)


def render_videos(content, pad):
    """One 16:9 embed per featured video, in the album frame from §8.

    youtube-nocookie.com, so the page does not hand a visitor to YouTube's
    ad cookies for having scrolled this far.
    """
    out = []
    for video in content['videos']['featured']:
        out += [
            '<figure class="frame">',
            '  <div class="ratio">',
            '    <iframe src="{}" title="{}"'.format(
                EMBED_URL.format(video['id']), html.escape(video['title'])),
            '            allowfullscreen loading="lazy"></iframe>',
            '  </div>',
            '  <figcaption>{}</figcaption>'.format(inline(video['caption'])),
            '</figure>',
        ]
    return indent(out, pad)


def render_streams(content, pad):
    """The live archive: one card per game, its streams in the order played.

    Links rather than embeds -- there are far too many of them to hand the
    page seventy iframes, and a stream is hours long, so it belongs on
    YouTube rather than in a box on a landing page.
    """
    out = []
    for group in content['videos']['streams']:
        sessions = group['sessions']
        out += [
            '<div class="card">',
            '  <div class="card-head">',
            '    <h4>{}</h4>'.format(inline(group['game'])),
            '    <span class="meta">{} stream{}</span>'.format(
                len(sessions), '' if len(sessions) == 1 else 's'),
            '  </div>',
            '  <ul class="linklist">',
        ]
        out += ['    <li><a href="{}" rel="noopener">{}</a>'
                '<span class="meta">{}</span></li>'.format(
                    WATCH_URL.format(s['id']), inline(s['label']), html.escape(s['date']))
                for s in sessions]
        out += ['  </ul>', '</div>']
    return indent(out, pad)


BLOCKS = {
    'profile': render_profile,
    'game-filters': render_game_filters,
    'games': render_games,
    'downloads': render_downloads,
    'file-kinds': render_file_kinds,
    'file-rules': render_file_rules,
    'videos': render_videos,
    'streams': render_streams,
}


# --------------------------------------------------------------------------

def build(page, content):
    src = original = page.read_text(encoding='utf-8')
    for name, render in BLOCKS.items():
        marker = re.compile(
            r'(?P<pad>[ \t]*)<!-- generated:{0} -->.*?<!-- /generated:{0} -->'
            .format(name), re.S)
        m = marker.search(src)
        if not m:
            continue
        pad = m.group('pad')
        replacement = '{p}<!-- generated:{n} -->\n{body}\n{p}<!-- /generated:{n} -->'.format(
            p=pad, n=name, body=render(content, pad))
        src = src[:m.start()] + replacement + src[m.end():]
    return src, original


def main(argv):
    if set(argv) - {'--check'}:
        raise SystemExit('usage: build.py [--check]')
    check = '--check' in argv
    content = load()
    stale = []
    for page in PAGES:
        built, original = build(page, content)
        if built == original:
            continue
        if check:
            stale.append(page.name)
        else:
            page.write_text(built, encoding='utf-8')
            print('wrote', page.relative_to(ROOT))
    if check and stale:
        print('out of date (run tools/build.py):', ', '.join(stale), file=sys.stderr)
        return 1
    if check:
        print('up to date')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
