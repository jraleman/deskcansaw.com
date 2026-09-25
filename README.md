# DeskCanSaw.com

The source for [deskcansaw.com](https://deskcansaw.com) — a retro video game
lover's site and the shopfront for small indie game concepts.

The visual identity lives in [`docs/style-guide.md`](docs/style-guide.md): one
palette sampled from [`assets/img/avatar.png`](assets/img/avatar.png), light and
dark, plus the type scale, components and voice the site is built to.

---

## The repo

Static HTML on GitHub Pages. The pages have no build step and no dependencies —
what is in the repo is what gets served. The games are the one exception: the
deploy exports them from the `dcs_games` submodule into `play/`. `main` is the
source and `gh-pages` is the site, built from it on every push — see
[Hosting the games](#hosting-the-games) and [Deploying](#deploying).

```
index.html            the site, one page
coming-soon.html      the holding page it replaced, kept but not linked
CNAME                 deskcansaw.com
.nojekyll             serve the files as they are; skip Jekyll
favicon.*             site icons, which belong at the root
apple-touch-icon.png

content/
  site.json           the site's own content — Gamer Profile, Files, Videos
  README.md           what the file holds and how to render it

docs/
  style-guide.md      the visual identity — the source of truth for §-numbers
                      referenced from the CSS comments

dcs_games/            the games' Godot project, a git submodule
play/                 the exported games — generated, never committed to main
downloads/            the collection's desktop builds — generated too

tools/
  catalog.py          the games, read out of the Godot project
  build.py            renders the generated blocks of index.html
  export_games.py     exports the games for the web, into play/
  play-shell.html     the page a game runs in
  play-missing.html   the page a game gets until dcs_games has it

.github/workflows/
  pages.yml           exports the games and builds the gh-pages branch

itch/                 the source for the deskcansaw.itch.io profile — the bio,
                      the theme editor values and the custom CSS. Pasted by
                      hand; itch has no API for it. See itch/README.md.

assets/css/
  tokens.css          colour, type, spacing, shape, motion. Every value in the
                      style guide lands here and nowhere else.
  base.css            reset, the 10px root scale, elements, text roles
  components.css      buttons, cards, tags, tables, wells, frames, the toggle
  layout.css          side nav, content column, hero, footer — full site pages
  holding.css         the holding page, coming-soon.html
  play.css            the game pages, play/ and play/<slug>/
assets/js/
  color-scheme.js     the day/night toggle
  scroll-spy.js       marks the nav item for the section in view
assets/img/
  avatar.png
```

Stylesheets are linked in dependency order — `tokens`, `base`, `components`,
then whichever of `layout`/`holding`/`play` the page needs. Two rules keep it that
way: component CSS reads the semantic tokens (`var(--dcs-surface)`) and never a
raw scheme colour, and markup carries classes rather than a `style` attribute.

A new page is a copy of `index.html`'s `<head>`, the same four `<link>` tags,
and the four-line inline script that sets the colour scheme before first paint.

## Where the content comes from

Nothing the site says is written down twice. The parts of the page that are a
list or a table are generated into `<!-- generated:… -->` markers by
`tools/build.py`, from whichever file actually owns them:

| Block | Comes from |
| --- | --- |
| `profile` | `content/site.json`, `"profile"` |
| `games` | `dcs_games`, its `project.godot` |
| `downloads` | `tools/catalog.py`, its `DESKTOPS` |
| `file-kinds` | `content/site.json`, `"files.kinds"` |
| `file-rules` | `content/site.json`, `"files.rules"` |
| `videos` | `content/site.json`, `"videos.featured"` |
| `streams` | `content/site.json`, `"videos.streams"` |

[`content/site.json`](content/site.json) is the site's own content, and
[`content/README.md`](content/README.md) says what shape it takes. The games
are not in it: the Godot project is the list of games, so a game is on the site
because it is in `dcs_games` — see [Hosting the games](#hosting-the-games).

Everything outside the markers, including all the prose, is written by hand in
the page and the script leaves it alone. This file is documentation, not
content; editing it changes nothing on the site.

```sh
python3 tools/build.py           # rewrite the generated blocks
python3 tools/build.py --check   # exit 1 if the pages are out of date
```

The output is committed, so the site stays static files with nothing in front
of them. The deploy runs `--check`, so a page that wasn't rebuilt fails the
build rather than going out stale.

## Running it locally

Paths are absolute from the site root, so open it over HTTP rather than from
the filesystem. Export the games first if you want them to load:

```sh
python3 tools/export_games.py --no-downloads   # the games, into play/ (needs Godot 4.7)
python3 -m http.server 8000                    # then http://localhost:8000
```

## Hosting the games

The games run here in the browser. `/play/` is all of them at once, which opens
on its own picker, and each one also has a page of its own at `/play/<slug>/`.
Their source is [dcs_games](https://github.com/jraleman/dcs_games), a git
submodule at `dcs_games/`. It's pinned to one commit, so what's on the site only
changes when this repo says so. Clone with it, or fetch it after:

```sh
git clone --recurse-submodules https://github.com/jraleman/deskcansaw.com
git submodule update --init --recursive   # in a clone made without it
```

To put newer games up, move the pin and commit it:

```sh
git submodule update --remote dcs_games
git -C dcs_games submodule update --init --recursive
git add dcs_games && git commit -m "Update the games"
```

`tools/catalog.py` is what reads the list. The project's `project.godot` names a
feature tag per game — `dcs/build/single_game_id.<tag>` — and that tag is both
what pins a build to that one game and what gives it its name. A slug is the
game id with dashes for underscores, so `games/anti_chess/` is
`/play/anti-chess/`. Add a game to the Godot project and it turns up on the
site; nothing here has to be told about it.

`tools/export_games.py` does the export. It copies the project out of the
submodule into `.cache/project/` — nothing is ever written into `dcs_games/` —
and makes one single-threaded web build per page: one per game, booted straight
into it, and one for the collection, started with `--game=all`. Single-threaded
builds need no cross-origin isolation headers, which GitHub Pages can't send.
Every page shares one copy of the engine in `play/engine/`, so a browser only
downloads it once.

```sh
python3 tools/export_games.py                     # everything, into play/
python3 tools/export_games.py --only collection   # just /play/
python3 tools/export_games.py --only anti-chess   # just that one game
python3 tools/export_games.py --no-downloads      # skip the desktop builds
```

It needs Godot 4.7: `--godot`, `$GODOT`, or `godot` on the PATH. The export
templates it needs are pulled into `.cache/` if Godot doesn't have them — the
web one is about 10 MB, and a desktop one about 80 MB, out of a 1.2 GB bundle
it never downloads whole. Each game is a submodule of its own, so a game the
project names but the checkout can't read gets a "not up yet" page and a
warning, not a failed deploy.

### Off the web

The collection is also a desktop build: the same every-game build, for a
machine that runs it without a browser. The same script exports it for Windows
and Linux, x86-64 and ARM64, and zips each one into `downloads/`, which is
served at `/downloads/`:

```
downloads/DCSGames-<os>-<arch>.zip
```

A zip holds one folder: the binary, its `.pck` — which is the games, and has
to stay beside the binary — and a short `README.txt`. The list of them is
`DESKTOPS` in [`tools/catalog.py`](tools/catalog.py), and both the buttons
under `/#games` and the ones on the `/play/` page are written from it, so a
file is named in one place. They are built whenever the collection is;
`--no-downloads` leaves them out, which is worth it locally, since a desktop
build is a few hundred MB that the web pages don't need.

### Deploying

`main` is the source; `gh-pages` is the site. Nothing on `gh-pages` is written
by hand — `.github/workflows/pages.yml` builds it on every push to `main`, or
by hand from the Actions tab. It checks out the submodules, runs
`tools/build.py --check`, exports the games with Godot 4.7.2 into `play/` and
the desktop builds into `downloads/`, and force-pushes the lot to `gh-pages` as
one commit with no history behind it, so the builds it replaces don't pile up
in the repo. Pages serves whatever lands there, games and all.

Two things to set up, and the branch has to exist before the second one:

1. **A `DCS_GAMES_TOKEN` secret**, under Settings → Secrets and variables →
   Actions. The game repos are private, so the checkout needs a fine-grained
   token with *Contents: read-only* on this repo, `dcs_games` and every game
   repo it pulls in. Tokens expire; when this one does, the deploy fails at
   the checkout until the secret is replaced.
2. **Settings → Pages → Source: Deploy from a branch → `gh-pages` / `(root)`.**
   Run the workflow once first — the branch isn't there to pick until it has.
   A branch deploy reads the `CNAME` file, so the custom domain comes off the
   repo rather than being set by hand. Pages on a private repo needs a paid
   plan.

Serving a branch means every file goes through `git push`, which refuses one
over 100 MiB. The game pages are well under it; a desktop build in `downloads/`
can come close, and one that goes over is left off the site with a warning in
the run's summary, rather than failing the push and taking the whole site with
it. If that happens, the fix is on the build side — a smaller `.pck`.

---

## Home

The front page is the short version of everything else. Who I am, what I'm
making right now, and the most recent thing worth looking at — a build, a file,
or a video.

Airy, hand-drawn, warm. Pale sky ground, cream paper to read on, a slate line
doing the describing, one peach thing per screen. Nothing on it is a dark
"gamer" site; the retro comes from ink and paper.

Everything below is a section of the site, not a separate place. Same nav, same
palette, same person writing.

## Gamer Profile

What I play on, and what I use to take things apart. The Files section is the
output of that table — if something there changes, the tools I can write change
with it. The table itself, and the favourites under it, are in
[`content/site.json`](content/site.json) under `"profile"`.

## Games

Where the playable things live. They run right here in the browser: `/play/` is
the whole collection, which opens on a rack of cartridges, and each game also
has a page of its own. The collection comes off the web too — a Windows or
Linux build of the same thing, which is what the buttons under the game list
are. My older games, made without gen-AI, are on
[itch.io](https://deskcansaw.itch.io).

The list is [dcs_games](https://github.com/jraleman/dcs_games) — the games the
Godot project names, in the order it names them. There is no second list here
to keep in step with it.

## Files

The archive: saves, tools, patches, romhacks and anything else I've made or
collected while poking at old games. The kinds of file it takes, and the rules
for what goes up, are in [`content/site.json`](content/site.json) under
`"files"`.

## Videos

The YouTube side of it: playthroughs, build logs from the games, and
teardowns of the files above.

Videos are embedded on the site next to the thing they're about — a devlog sits
on its project page, a romhack demo sits with the patch. The channel is the
feed; this site is where a video has context around it. The embeds are in
[`content/site.json`](content/site.json) under `"videos.featured"`, and they go
through `youtube-nocookie.com`.

Under them is the live archive: every stream the channel has done, in a card
per game, oldest first. They are links rather than embeds — a stream runs for
hours, and seventy iframes is not a landing page. That list is
[`content/site.json`](content/site.json) under `"videos.streams"`.

https://youtube.com/@deskcansaw

https://www.youtube.com/@DeskCanSaw/streams
