#!/usr/bin/env python3
"""The games, read out of the dcs_games Godot project, and what ships of them.

dcs_games is the list of games, so nothing about them is written down twice.
project.godot names a feature tag per game, and that tag is what an export
uses to pin a build to that one game:

    id      the folder under games/, and what --game= takes
    tag     dcs/build/single_game_id.<tag>, application/config/name.<tag>
    slug    the id with dashes, which is its page under /play/
    name    what the game is called

The tag whose id is empty is the collection -- every game at once, which opens
on its own picker -- so it is not one of the games.

Only project.godot is read. Each game's own games/<id>/game.gd holds more (a
tagline, a menu order), but the game folders are submodules in their own
right, and a checkout that can't read the private ones still has to render the
same pages as one that can, so nothing here depends on a game folder being
checked out.

    tools/build.py          lists them under /#games
    tools/export_games.py   exports a page for each, and one for the lot

The collection also ships as a desktop build, which is what `desktops()` is:
one entry per file under /downloads/. Both tools read it, so a download is
named once -- tools/export_games.py exports and zips it, tools/build.py and
the play shell link to it.
"""

import html
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'dcs_games'            # the submodule
PROJECT = 'godot-base'                 # the Godot project inside it
PROJECT_FILE = SOURCE / PROJECT / 'project.godot'

# The collection: the feature tag whose single_game_id is empty, so nothing
# pins the build to one game. It is the page at /play/, and it is started with
# the selector scripts/game_catalog.gd reads off the command line.
COLLECTION = 'collection'
COLLECTION_TITLE = 'Games'
ALL_GAMES = 'all'

# The collection as something to keep: the same every-game build, for a
# desktop that runs it without a browser. One entry per file under
# /downloads/, and the only place any of them is named.
DOWNLOAD_NAME = 'DCSGames'         # the binary, and the folder inside the zip
DOWNLOAD_PATH = '/downloads/'      # where the files are served from

DESKTOPS = (
    # os         what the button says   architecture, and what it is called
    ('windows',  'Windows',             'x86_64', 'x86-64'),
    ('windows',  'Windows',             'arm64',  'ARM64'),
    ('linux',    'Linux',               'x86_64', 'x86-64'),
    ('linux',    'Linux',               'arm64',  'ARM64'),
)

SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')

# Slugs a game can't have: they would land on the collection's own files or on
# the engine every page shares.
RESERVED = {COLLECTION, 'engine', 'index'}

ON_CI = os.environ.get('GITHUB_ACTIONS') == 'true'


def warn(message):
    if ON_CI:
        print('::warning::' + message, flush=True)
    else:
        print('warning: ' + message, file=sys.stderr, flush=True)


def settings(path=None):
    """{section: {key: raw value}} for the one-line settings in project.godot."""
    path = path or PROJECT_FILE
    try:
        text = path.read_text(encoding='utf-8')
    except OSError as e:
        raise SystemExit('cannot read {}: {}. Run: git submodule update --init '
                         '--recursive'.format(path, e.strerror))
    sections, current = {}, {}
    for line in text.splitlines():
        line = line.strip()
        head = re.fullmatch(r'\[(.+)\]', line)
        if head:
            current = sections.setdefault(head.group(1), {})
            continue
        m = re.fullmatch(r'([\w/.\-]+)=(.*)', line)
        if m:
            current[m.group(1)] = m.group(2)
    return sections


def unquote(value):
    """A Godot string literal -> str. It escapes the way JSON does."""
    try:
        return json.loads(value)
    except ValueError:
        return value.strip('"')


def games(found=None):
    """The games, in the order project.godot names them."""
    found = found if found is not None else settings()
    app = found.get('application', {})
    out, tags = [], {}
    for key, value in found.get('dcs', {}).items():
        m = re.fullmatch(r'build/single_game_id\.(\w+)', key)
        if not m:
            continue
        tag, game_id = m.group(1), unquote(value)
        if not game_id:                      # the collection
            continue
        if game_id in tags:
            warn('project.godot pins both "{}" and "{}" to {}; taking "{}"'.format(
                tags[game_id], tag, game_id, tags[game_id]))
            continue
        tags[game_id] = tag

        slug = game_id.replace('_', '-')
        if not SLUG.fullmatch(slug) or slug in RESERVED:
            raise SystemExit('project.godot: dcs/build/single_game_id.{}="{}" is not a name a '
                             'page can have under /play/'.format(tag, game_id))
        name = unquote(app.get('config/name.' + tag, ''))
        if not name:
            name = game_id.replace('_', ' ').title()
            warn('project.godot has no application/config/name.{}, so /play/{}/ is titled '
                 '"{}"'.format(tag, slug, name))
        out.append({'id': game_id, 'tag': tag, 'slug': slug, 'name': name})

    if not out:
        raise SystemExit('project.godot pins no dcs/build/single_game_id.<tag> to a game, '
                         'so there are no games')
    return out


def desktops():
    """The collection's desktop builds, with everything a download needs.

        slug      windows-x86_64, and what its export preset is called
        label     the platform, as the button says it
        arch      the architecture, for the preset and for the button
        platform  the Godot export platform
        template  the export template that platform takes
        binary    what Godot exports, next to its .pck
        folder    the one folder the zip holds, so it unpacks into itself
        file      the zip itself, served from DOWNLOAD_PATH

    Every build is the collection -- the COLLECTION feature tag, which pins
    nothing, so it opens on the same picker /play/ does.
    """
    out = []
    for os_id, label, arch, arch_label in DESKTOPS:
        windows = os_id == 'windows'
        folder = '{}-{}-{}'.format(DOWNLOAD_NAME, os_id, arch)
        out.append({
            'slug': '{}-{}'.format(os_id, arch),
            'label': label,
            'arch': arch,
            'arch_label': arch_label,
            'platform': 'Windows Desktop' if windows else 'Linux',
            'template': ('windows_release_{}.exe'.format(arch) if windows
                         else 'linux_release.{}'.format(arch)),
            'binary': DOWNLOAD_NAME + ('.exe' if windows else '.' + arch),
            'folder': folder,
            'file': folder + '.zip',
        })
    return out


def download_links(pad=''):
    """One <a> per desktop build, as lines of HTML, indented by `pad`.

    The page (tools/build.py) and the play shell (tools/export_games.py) offer
    the same downloads and say the same thing about them, so the markup for a
    link is written here, next to the list it is written from.
    """
    out = []
    for d in desktops():
        out += [
            '<a class="btn btn-secondary" href="{}{}" download>'.format(
                DOWNLOAD_PATH, html.escape(d['file'])),
            '  {} <span class="tag">{}</span>'.format(
                html.escape(d['label']), html.escape(d['arch_label'])),
            '</a>',
        ]
    return '\n'.join(pad + line for line in out)
