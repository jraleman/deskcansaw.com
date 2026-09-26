#!/usr/bin/env python3
"""Export the games in dcs_games/ for the web, into play/.

The games are one Godot 4 project, dcs_games/godot-base/, pulled in as a git
submodule, and that project is the list of games: tools/catalog.py reads them
out of its project.godot. Exporting with a game's feature tag pins the build
to that one game; the tag with an empty id is the collection -- every game at
once, which opens on its own picker.

    play/index.html            the collection, started with --game=all
    play/index.pck             every game
    play/<slug>/index.html     one game on its own, from its feature tag
    play/<slug>/index.pck      that game
    play/engine/<version>/     the engine, one copy shared by every page

The site lists them under /#games, and /play/ is all of them at once. A slug
is the game id with dashes for underscores, so games/anti_chess/ is
/play/anti-chess/.

The collection also comes off the web. The same build is exported for Windows
and Linux, x86_64 and arm64, and zipped into downloads/, which is served at
/downloads/ and linked from /#games and from the /play/ page itself:

    downloads/DCSGames-<os>-<arch>.zip

tools/catalog.py's desktops() is the list, so a file is named in one place.
They are built whenever the collection is, and --no-downloads leaves them out.

The builds are single-threaded, so they need no cross-origin isolation
headers, which GitHub Pages can't send. A game the project pins a tag to but
the pinned dcs_games commit has no folder for gets tools/play-missing.html and
a warning instead of a failed deploy.

Nothing is written into dcs_games/. The project's tracked files are copied to
.cache/project/, and the web export presets, plus one editor setting that keeps
the scenes as text (see TEXT_SCENES), are written into that copy.

    python3 tools/export_games.py                     # everything, into play/
    python3 tools/export_games.py --only collection   # just /play/
    python3 tools/export_games.py --only anti-chess   # just that one game
    python3 tools/export_games.py --no-downloads      # skip the desktop builds
    python3 tools/export_games.py --out _site/play    # what the deploy runs

Needs Godot 4: --godot, $GODOT, or godot on PATH. The export templates are
taken from Godot's own templates folder if it's installed there. Otherwise the
files needed are pulled out of the official template bundle into .cache/godot/
-- about 10 MB for the web, ~80 MB per desktop build, not the whole 1.2 GB
download.
"""

import argparse
import collections
import hashlib
import html
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import catalog  # noqa: E402 -- the games, read out of dcs_games
from catalog import ALL_GAMES, COLLECTION, COLLECTION_TITLE, warn  # noqa: E402

ROOT = catalog.ROOT
SOURCE = catalog.SOURCE                # the submodule
PROJECT = catalog.PROJECT              # the Godot project inside it
CACHE = ROOT / '.cache'
STAGE = CACHE / 'project'              # the copy Godot opens and imports into
SHELL = TOOLS / 'play-shell.html'
MISSING = TOOLS / 'play-missing.html'

WEB_TEMPLATE = 'web_nothreads_release.zip'
BUNDLE_URL = ('https://github.com/godotengine/godot-builds/releases/download/'
              '{tag}/Godot_v{tag}_export_templates.tpz')

# The engine files Godot writes next to every export. They come out of the
# template as they are, so they're the same for every game: the pages share
# one copy, and a browser only downloads it once.
ENGINE_FILES = ('.js', '.wasm', '.audio.worklet.js', '.audio.position.worklet.js')

# Never shipped: dev tools, tests, and the native plugin sources for the phone
# builds. Every other game's folder is added to this for each export.
EXCLUDE = ['tools/*', 'tests/*', 'games/*/tools/*', 'games/*/tests/*',
           'games/*/android/*', 'games/*/ios/*']

# Godot 4.7 turns .tscn into binary on export by instancing each scene and
# packing it again, and the repack resets the anchors of a Control that roots
# an inherited scene: games/anti_chess/intro.tscn and the other intros built
# on scenes/boot/intro.tscn boot at 0x0 in the top-left corner. Shipping the
# scenes as text keeps them exactly as the editor runs them. The editor
# ignores override.cfg, so this goes on the end of the staged project.godot;
# a repeated section is fine there, and the last value wins.
TEXT_SCENES = '\n[editor]\n\nexport/convert_text_resources_to_binary=false\n'

ON_CI = catalog.ON_CI


def say(line=''):
    print(line, flush=True)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def git(*args):
    """git, run inside the dcs_games submodule."""
    return subprocess.run(['git', '-C', str(SOURCE)] + list(args),
                          capture_output=True, check=True).stdout.decode('utf-8', 'replace')


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def megabytes(n):
    return '{:.1f} MB'.format(n / 1048576)


# --------------------------------------------------------------------------
# What to build: the games, checked against the folders this commit has.
# --------------------------------------------------------------------------

def resolve(games, settings):
    """Split the games into the ones this commit can build and the ones it can't."""
    app = settings.get('application', {})
    ready, missing = [], []
    for g in games:
        if not (STAGE / 'games' / g['id'] / 'game.gd').is_file():
            folder = '{}/games/{}'.format(PROJECT, g['id'])
            if git('ls-files', '--stage', '--', folder).startswith('160000') \
                    and not (SOURCE / folder / '.git').exists():
                raise SystemExit('dcs_games/{} is a submodule that isn\'t checked out. '
                                 'Run: git submodule update --init --recursive'.format(folder))
            missing.append(g)
            continue
        if 'config/custom_user_dir_name.' + g['tag'] not in app:
            raise SystemExit('{}: project.godot has no config/custom_user_dir_name.{}, so its '
                             'saves would land in another game\'s folder'.format(g['name'], g['tag']))
        ready.append(g)
    return ready, missing


# --------------------------------------------------------------------------
# Godot and its web export template.
# --------------------------------------------------------------------------

def find_godot(explicit):
    named = explicit or os.environ.get('GODOT')
    if named:
        path = shutil.which(named) or (named if Path(named).is_file() else None)
        if not path:
            raise SystemExit('no Godot at ' + named)
        return path
    for name in ('godot', 'godot4'):
        if shutil.which(name):
            return shutil.which(name)
    raise SystemExit('Godot 4 not found: put it on PATH as godot, set GODOT, or pass --godot')


def godot_version(godot):
    """'4.7.2.stable' names the templates folder, '4.7.2-stable' the release."""
    out = subprocess.run([godot, '--version'], capture_output=True, text=True, timeout=300).stdout
    for line in reversed(out.splitlines()):
        m = re.match(r'(\d+)\.(\d+(?:\.\d+)?)\.([a-z]+\d*)\b', line.strip())
        if m:
            if m.group(1) != '4':
                raise SystemExit('{} is Godot {}; the games need Godot 4'.format(godot, line.strip()))
            number = m.group(1) + '.' + m.group(2)
            return {'full': line.strip(), 'minor': '.'.join(number.split('.')[:2]),
                    'dir': number + '.' + m.group(3), 'tag': number + '-' + m.group(3)}
    raise SystemExit('cannot read a version out of {} --version: {!r}'.format(godot, out))


def installed_templates(godot, version, name):
    """Where the editor itself keeps export templates, most specific first."""
    exe = Path(godot).resolve()
    shim = exe.with_suffix('.shim')                  # scoop: the real binary is elsewhere
    if shim.is_file():
        m = re.search(r'^path\s*=\s*"?(.+?)"?\s*$', shim.read_text(errors='replace'), re.M)
        if m:
            exe = Path(m.group(1))
    home = Path.home()
    roots = []
    if (exe.parent / '_sc_').exists() or (exe.parent / '._sc_').exists():
        roots.append(exe.parent / 'editor_data')     # a self-contained editor
    if sys.platform == 'win32':
        roots.append(Path(os.environ.get('APPDATA') or home / 'AppData' / 'Roaming') / 'Godot')
    elif sys.platform == 'darwin':
        roots.append(home / 'Library' / 'Application Support' / 'Godot')
    else:
        roots.append(Path(os.environ.get('XDG_DATA_HOME') or home / '.local' / 'share') / 'godot')
    return [r / 'export_templates' / version['dir'] / name for r in roots]


def find_templates(godot, version, names, web_override):
    """{template name: file}, fetching in one pass whatever isn't already here.

    The editor's own templates folder comes first, then .cache/godot/, then
    the official bundle -- which is opened once however many files are wanted
    from it, because reading one is a walk over an HTTP range request.
    """
    found, wanted = {}, {}
    for name in dict.fromkeys(names):                # in order, without repeats
        if name == WEB_TEMPLATE and web_override:
            if not Path(web_override).is_file():
                raise SystemExit('no template at ' + web_override)
            found[name] = Path(web_override).resolve()
            continue
        for path in installed_templates(godot, version, name):
            if path.is_file():
                found[name] = path
                break
        else:
            found[name] = CACHE / 'godot' / 'templates' / version['dir'] / name
            if not found[name].is_file():
                wanted[name] = found[name]
    if wanted:
        download_templates(version, wanted)
    return found


class RemoteFile(io.RawIOBase):
    """A seekable, read-only file over HTTP range requests.

    zipfile only reads the bundle's directory and the members it's asked for,
    so this fetches the templates that are wanted, not the whole 1.2 GB file.
    """

    def __init__(self, url):
        super().__init__()
        self.url, self.pos = url, 0
        with self._fetch(0, 0) as r:
            if r.status != 206:
                raise SystemExit('{} ignores range requests. Install the web export '
                                 'template from the Godot editor, or pass --template'.format(url))
            self.size = int(r.headers['Content-Range'].rsplit('/', 1)[1])

    def _fetch(self, start, end):
        request = urllib.request.Request(self.url, headers={
            'Range': 'bytes={}-{}'.format(start, end),
            'User-Agent': 'deskcansaw.com tools/export_games.py',
        })
        for attempt in range(4):
            try:
                return urllib.request.urlopen(request, timeout=60)
            except urllib.error.HTTPError as e:
                if e.code < 500 or attempt == 3:
                    raise SystemExit('{}: HTTP {}'.format(self.url, e.code))
            except OSError:
                if attempt == 3:
                    raise
            time.sleep(2 ** attempt)

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=io.SEEK_SET):
        start = {io.SEEK_SET: 0, io.SEEK_CUR: self.pos, io.SEEK_END: self.size}[whence]
        self.pos = max(0, start + offset)
        return self.pos

    def readinto(self, buffer):
        if self.pos >= self.size or not len(buffer):
            return 0
        end = min(self.pos + len(buffer), self.size) - 1
        with self._fetch(self.pos, end) as r:
            data = r.read()
        buffer[:len(data)] = data
        self.pos += len(data)
        return len(data)


def download_templates(version, wanted):
    """{name: where it goes} out of the official bundle, in one open."""
    url = BUNDLE_URL.format(tag=version['tag'])
    say('fetching  {} out of {}'.format(', '.join(wanted), url))
    with zipfile.ZipFile(io.BufferedReader(RemoteFile(url), buffer_size=1 << 23)) as bundle:
        inside = bundle.read('templates/version.txt').decode().strip()
        if inside != version['dir']:
            raise SystemExit('{} holds templates for {}, not {}'.format(url, inside, version['dir']))
        for name, dest in wanted.items():
            part = dest.with_name(dest.name + '.part')
            part.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open('templates/' + name) as src, open(part, 'wb') as out:
                shutil.copyfileobj(src, out, 1 << 20)
            os.replace(part, dest)


# --------------------------------------------------------------------------
# The project copy, the presets, the pages.
# --------------------------------------------------------------------------

def stage_project():
    """Mirror the project's tracked files into STAGE; return how many changed.

    Only what git tracks is copied, from the submodules' working trees, and
    STAGE keeps its .godot/ import cache between runs, so the next export only
    re-imports what changed. project.godot gets TEXT_SCENES added on the way.
    """
    if not (SOURCE / '.git').exists():
        raise SystemExit('dcs_games/ is empty. Run: git submodule update --init --recursive')
    wanted = {}
    for path in filter(None, git('ls-files', '-z', '--recurse-submodules', '--', PROJECT).split('\0')):
        src, rel = SOURCE / path, path[len(PROJECT) + 1:]
        if src.is_file() and rel != 'export_presets.cfg':   # that one is written by main()
            wanted[rel] = src
    if 'project.godot' not in wanted:
        raise SystemExit('dcs_games/{}/project.godot is missing'.format(PROJECT))
    settings = wanted.pop('project.godot').read_bytes() + TEXT_SCENES.encode()

    listing = CACHE / 'project.files'
    before = set(listing.read_text(encoding='utf-8').splitlines()) if listing.is_file() else set()
    for rel in before - set(wanted) - {'project.godot'}:
        (STAGE / rel).unlink(missing_ok=True)
    changed = 0
    for rel, src in wanted.items():
        dst = STAGE / rel
        s = src.stat()
        try:
            d = dst.stat()
            if d.st_size == s.st_size and int(d.st_mtime) == int(s.st_mtime):
                continue
        except FileNotFoundError:
            pass
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        changed += 1
    dst = STAGE / 'project.godot'
    if not dst.is_file() or dst.read_bytes() != settings:
        dst.write_bytes(settings)
        changed += 1
    write(listing, '\n'.join(sorted(wanted) + ['project.godot']) + '\n')
    return changed


def cfg_string(value):
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def web_options(shell):
    """The options a Web preset takes, beyond the template."""
    return [
        'variant/extensions_support=false',
        'variant/thread_support=false',
        'vram_texture_compression/for_desktop=true',
        'vram_texture_compression/for_mobile=true',
        'html/export_icon=true',
        'html/custom_html_shell=' + cfg_string(shell.as_posix()),
        'html/head_include=""',
        'html/canvas_resize_policy=0',
        'html/focus_canvas_on_start=true',
        'html/experimental_virtual_keyboard=false',
        'progressive_web_app/enabled=false',
    ]


def desktop_options(d):
    """The options a Windows or Linux preset takes, beyond the template.

    Anything left out keeps the platform's own default, so this is only what
    the download depends on. The pack stays beside the binary rather than
    inside it, so the zip is the two files and a note, and there is one thing
    to unpack. Nothing is signed, and the Windows build's icon and version
    fields are left alone -- rewriting them needs rcedit, which the deploy has
    no business installing to change an icon.
    """
    out = ['binary_format/embed_pck=false',
           'binary_format/architecture=' + cfg_string(d['arch']),
           'texture_format/s3tc_bptc=true',
           'texture_format/etc2_astc=false',
           'ssh_remote_deploy/enabled=false']
    if d['platform'] == 'Windows Desktop':
        # A console wrapper would put a second .exe in the zip, and the games
        # have nothing to say on a terminal.
        out += ['debug/export_console_wrapper=0',
                'codesign/enable=false',
                'application/modify_resources=false']
    return out


def presets(targets, folders):
    """export_presets.cfg: one preset per page and per download, nothing else.

    Every target carries the name Godot exports it by, its platform, the
    template that platform takes and the options that go with it; the games it
    leaves out are whichever ones it doesn't keep.
    """
    lines = []
    for i, t in enumerate(targets):
        exclude = EXCLUDE + ['games/{}/*'.format(f) for f in folders if f not in t['keep']]
        lines += [
            '[preset.{}]'.format(i),
            '',
            'name=' + cfg_string(t['preset']),
            'platform=' + cfg_string(t['platform']),
            'runnable=false',
            'advanced_options=false',
            'dedicated_server=false',
            'custom_features=' + cfg_string(t['tag']),
            'export_filter="all_resources"',
            'include_filter=""',
            'exclude_filter=' + cfg_string(', '.join(exclude)),
            'export_path=""',
            'encryption_include_filters=""',
            'encryption_exclude_filters=""',
            'seed=0',
            'encrypt_pck=false',
            'encrypt_directory=false',
            'script_export_mode=2',
            '',
            '[preset.{}.options]'.format(i),
            '',
            'custom_template/debug=""',
            'custom_template/release=' + cfg_string(t['template'].as_posix()),
        ] + t['options'] + ['']
    return '\n'.join(lines)


def fill(template, values):
    """A page template with its {{NAME}}s filled. Godot fills the $GODOT_*s."""
    text = template.read_text(encoding='utf-8')
    for key, value in values.items():
        text = text.replace('{{' + key + '}}', value)
    left = sorted(set(re.findall(r'\{\{\w+\}\}', text)))
    if left:
        raise SystemExit('tools/{}: nothing fills {}'.format(template.name, ', '.join(left)))
    return text


def page_values(name, engine='', game='', downloads=''):
    """What a page template takes. ARGS lands in Godot's OS.get_cmdline_args()."""
    return {
        'TITLE': html.escape(name),
        'ENGINE': engine,
        'ARGS': json.dumps(['--game=' + game] if game else []),
        'DOWNLOADS': downloads,
    }


def downloads_block(pad='      '):
    """The desktop builds, as the /play/ page offers them. Only that page does.

    The same links the site's own page carries, from the same list, so the two
    can't come to disagree about what there is to download.
    """
    return '\n'.join([
        pad + '<div class="play-get">',
        pad + '  <p class="meta">Or keep the collection, and play it without a browser:</p>',
        pad + '  <div class="actions">',
        catalog.download_links(pad + '    '),
        pad + '  </div>',
        pad + '</div>',
    ])


# --------------------------------------------------------------------------
# Running Godot.
# --------------------------------------------------------------------------

def run_godot(godot, args, log_name, verbose):
    """The editor, headless, on STAGE. Returns (exit code, last lines, errors)."""
    log_path = CACHE / 'logs' / log_name
    log_path.parent.mkdir(parents=True, exist_ok=True)
    tail, errors = collections.deque(maxlen=60), []
    with open(log_path, 'w', encoding='utf-8', newline='\n') as log:
        proc = subprocess.Popen([godot, '--headless', '--path', str(STAGE)] + args,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for raw in proc.stdout:
            line = raw.decode('utf-8', 'replace').rstrip()
            log.write(line + '\n')
            tail.append(line)
            if verbose:
                say('  | ' + line)
            if re.match(r'\s*(SCRIPT )?ERROR:', line):
                errors.append(line.strip())
        code = proc.wait()
    return code, list(tail), errors


def report(errors, log_name):
    """Godot logs errors it recovers from; show them without failing the build."""
    if not errors:
        return
    say('          {} error line(s) in .cache/logs/{}, first ones:'.format(len(errors), log_name))
    for line in errors[:5]:
        say('            ' + line[:200])


def export_game(godot, t, engine_dir, first, verbose):
    dest = t['dest']
    if t['slug'] == COLLECTION:
        # The collection is /play/ itself, so only its own files go; the game
        # folders and the shared engine sit alongside them.
        for path in sorted(dest.glob('index.*')):
            path.unlink()
        dest.mkdir(parents=True, exist_ok=True)
    else:
        shutil.rmtree(dest, ignore_errors=True)
        dest.mkdir(parents=True)
    log_name = t['slug'] + '.log'
    code, tail, errors = run_godot(
        godot, ['--export-release', t['preset'], str(dest / 'index.html')], log_name, verbose)
    if code != 0 or not (dest / 'index.pck').is_file():
        say('\n'.join('  | ' + line for line in tail))
        raise SystemExit('{}: the export failed (the whole log is .cache/logs/{})'.format(
            t['slug'], log_name))
    report(errors, log_name)

    for suffix in ENGINE_FILES:
        built, shared = dest / ('index' + suffix), engine_dir / ('godot' + suffix)
        if not built.is_file():
            raise SystemExit('{}: the export wrote no {}'.format(t['slug'], built.name))
        if first:
            engine_dir.mkdir(parents=True, exist_ok=True)
            os.replace(built, shared)
        elif digest(built) == digest(shared):
            built.unlink()
        else:
            raise SystemExit('{}: {} is not the engine the other pages got'.format(
                t['slug'], built.name))
    (dest / 'index.png').unlink(missing_ok=True)   # the boot splash; the page draws its own
    return (dest / 'index.pck').stat().st_size


README = """\
{folder} -- every DeskCanSaw game in one build.

Keep {binary} and {pack} together; the game reads the pack that sits
next to it, so moving one without the other leaves it with nothing to play.
{run}
It is the collection that runs at https://deskcansaw.com/play/, off the web.
"""

RUN_LINUX = """\
On Linux, mark it executable if your unpacker didn't: chmod +x {binary}
"""


def zip_folder(folder, dest, executables):
    """Zip `folder` into `dest` as one top-level folder of that name.

    Python leaves a zip's Unix modes empty, and a build whose binary comes out
    without its executable bit is a build that doesn't start, so every member
    is given a mode and the binary is given 755.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + '.part')
    with zipfile.ZipFile(part, 'w', zipfile.ZIP_DEFLATED) as out:
        for path in sorted(p for p in folder.rglob('*') if p.is_file()):
            info = zipfile.ZipInfo('{}/{}'.format(folder.name, path.relative_to(folder).as_posix()),
                                   time.localtime(path.stat().st_mtime)[:6])
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3                  # Unix, so external_attr is read as a mode
            info.external_attr = (0o755 if path.name in executables else 0o644) << 16
            with open(path, 'rb') as src, out.open(info, 'w') as member:
                shutil.copyfileobj(src, member, 1 << 20)
    os.replace(part, dest)


def export_download(godot, t, out, verbose):
    """One desktop build of the collection, exported and zipped into `out`."""
    folder = CACHE / 'downloads' / t['slug'] / t['folder']
    shutil.rmtree(folder.parent, ignore_errors=True)
    folder.mkdir(parents=True)
    binary = folder / t['binary']
    pack = binary.with_suffix('.pck')
    log_name = 'download-{}.log'.format(t['slug'])
    code, tail, errors = run_godot(
        godot, ['--export-release', t['preset'], str(binary)], log_name, verbose)
    if code != 0 or not binary.is_file() or not pack.is_file():
        say('\n'.join('  | ' + line for line in tail))
        raise SystemExit('{}: the export failed (the whole log is .cache/logs/{})'.format(
            t['slug'], log_name))
    report(errors, log_name)
    write(folder / 'README.txt', README.format(
        folder=t['folder'], binary=binary.name, pack=pack.name,
        run=RUN_LINUX.format(binary=binary.name) if t['platform'] == 'Linux' else ''))

    dest = out / t['file']
    zip_folder(folder, dest, {binary.name})
    shutil.rmtree(folder.parent, ignore_errors=True)
    return dest.stat().st_size


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Export the games in dcs_games/ for the web, into play/.')
    parser.add_argument('--out', type=Path, default=ROOT / 'play',
                        help='the folder served at /play/ (default: play/)')
    parser.add_argument('--downloads', type=Path, default=ROOT / 'downloads',
                        help='the folder served at /downloads/, which the collection\'s '
                             'desktop builds go in (default: downloads/)')
    parser.add_argument('--no-downloads', action='store_true',
                        help='export the pages only, and leave the desktop builds out')
    parser.add_argument('--only', action='append', default=[], metavar='SLUG',
                        help='export just this page, "{}" for /play/ itself; repeat it, '
                             'or separate slugs with commas'.format(COLLECTION))
    parser.add_argument('--godot', help='the Godot 4 editor (default: $GODOT, then godot on PATH)')
    parser.add_argument('--template', help='a web_nothreads_release.zip to use as it is')
    parser.add_argument('--verbose', action='store_true', help="print Godot's output as it runs")
    args = parser.parse_args(argv)

    godot = find_godot(args.godot)
    version = godot_version(godot)
    say('godot     {} ({})'.format(version['full'], godot))

    changed = stage_project()
    commit = git('rev-parse', '--short', 'HEAD').strip()
    say('source    dcs_games@{}, {} file(s) copied to .cache/project/'.format(commit, changed))

    settings = catalog.settings(STAGE / 'project.godot')
    made_with = re.search(r'"(\d+\.\d+)"', settings.get('application', {}).get('config/features', ''))
    if made_with and made_with.group(1) != version['minor']:
        warn('the games are made with Godot {}, and this is Godot {}'.format(
            made_with.group(1), version['minor']))
    ready, missing = resolve(catalog.games(settings), settings)

    # Everything, unless --only picked some of it. The whole list is resolved
    # either way, so the collection ships the same games however it is built.
    want = {s.strip() for item in args.only for s in item.split(',') if s.strip()} or None
    if want:
        unknown = want - {g['slug'] for g in ready + missing} - {COLLECTION}
        if unknown:
            raise SystemExit('dcs_games@{} has no page for: {}'.format(
                commit, ', '.join(sorted(unknown))))

    out = args.out.resolve()
    engine_dir = out / 'engine' / version['dir']
    engine_rel = 'engine/{}/godot'.format(version['dir'])
    keep = {g['id'] for g in ready}
    collection = not want or COLLECTION in want

    targets = []
    if collection:
        targets.append({'slug': COLLECTION, 'name': COLLECTION_TITLE, 'tag': COLLECTION,
                        'dest': out, 'keep': keep, 'engine': engine_rel, 'game': ALL_GAMES})
    targets += [{'slug': g['slug'], 'name': g['name'], 'tag': g['tag'],
                 'dest': out / g['slug'], 'keep': {g['id']}, 'engine': '../' + engine_rel,
                 'game': g['id']}
                for g in ready if not want or g['slug'] in want]
    missing = [g for g in missing if not want or g['slug'] in want]

    # The downloads are the collection, so they are built whenever it is.
    wanted = catalog.desktops() if collection and not args.no_downloads else []
    for d in wanted:
        d.update({'preset': 'desktop-' + d['slug'], 'tag': COLLECTION, 'keep': keep})
    if not targets and not missing and not wanted:
        raise SystemExit('nothing to export')

    names = ([WEB_TEMPLATE] if targets else []) + [d['template'] for d in wanted]
    templates = find_templates(godot, version, names, args.template)
    for name in dict.fromkeys(names):
        say('template  {}'.format(templates[name]))

    for t in targets:
        shell = CACHE / 'shells' / (t['slug'] + '.html')
        write(shell, fill(SHELL, page_values(
            t['name'], t['engine'], t['game'],
            downloads_block() if t['slug'] == COLLECTION and not args.no_downloads else '')))
        t.update({'preset': 'web-' + t['slug'], 'platform': 'Web',
                  'template': templates[WEB_TEMPLATE], 'options': web_options(shell)})
    for d in wanted:
        d.update({'template': templates[d['template']], 'options': desktop_options(d)})
    folders = sorted(p.name for p in (STAGE / 'games').iterdir() if p.is_dir())
    write(STAGE / 'export_presets.cfg', presets(targets + wanted, folders))

    built = []
    if targets or wanted:
        say('importing')
        log_name = 'import.log'
        (CACHE / 'logs' / 'import-again.log').unlink(missing_ok=True)
        code, tail, errors = run_godot(godot, ['--import'], log_name, args.verbose)
        if code == 0 and errors:
            # A fresh import loads the project theme before the textures it
            # uses are imported, and logs an error for each one. A second pass
            # has nothing left to import, so the errors that come back are real.
            log_name = 'import-again.log'
            code, tail, errors = run_godot(godot, ['--import'], log_name, args.verbose)
        if code != 0:
            say('\n'.join('  | ' + line for line in tail))
            raise SystemExit('the import failed (the whole log is .cache/logs/{})'.format(log_name))
        report(errors, log_name)
    for i, t in enumerate(targets):
        say('exporting {} (feature tag "{}", --game={})'.format(t['slug'], t['tag'], t['game']))
        built.append((t['slug'], export_game(godot, t, engine_dir, i == 0, args.verbose)))

    downloaded = []
    for d in wanted:
        say('exporting {} ({}, {})'.format(d['file'], d['platform'], d['arch']))
        downloaded.append((d['file'], export_download(
            godot, d, args.downloads.resolve(), args.verbose)))

    for g in missing:
        warn('{}: games/{} isn\'t in dcs_games@{}, so /play/{}/ says it isn\'t up yet'.format(
            g['name'], g['id'], commit, g['slug']))
        write(out / g['slug'] / 'index.html', fill(MISSING, page_values(g['name'])))

    say()
    rows = [(slug, megabytes(size)) for slug, size in built]
    rows += [(g['slug'], 'not up yet') for g in missing]
    if built:
        rows.append(('engine', megabytes(sum(
            (engine_dir / ('godot' + s)).stat().st_size for s in ENGINE_FILES)) + ', shared'))
    rows += [(name, megabytes(size) + ', zipped') for name, size in downloaded]
    for name, size in rows:
        say('  {:<32} {}'.format(name, size))
    say('wrote {}'.format(out))
    if downloaded:
        say('wrote {}'.format(args.downloads.resolve()))

    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f:
            f.write('### Games, from dcs_games@{}\n\n| Page or file | Size |\n| --- | --- |\n'
                    .format(commit))
            f.writelines('| `{}` | {} |\n'.format(name, size) for name, size in rows)
    return 0


if __name__ == '__main__':
    sys.exit(main())
