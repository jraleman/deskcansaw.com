# The site's content

`site.json` is the source of truth for the parts of the site that would
otherwise be written twice — the Gamer Profile body, game card descriptions,
the kinds and rules under Files, and the videos and live streams under Videos.
`tools/build.py` renders it into the `<!-- generated:… -->` blocks of
`index.html`.

The `"profile"` array is the personal gaming shelf below Games. Its blocks
render in the order written:

- `intro`: a prominent `lead` and a short personal introduction in `text`.
- `favorites`: a shared `text` explaining the selection, then `items` with
  `name`, a plain-text `platform` badge, and an optional personal `note`.
- `setup`: a shared `text` explaining how you play, then hardware `items`
  with `name` and an optional `note` about how you use each device.

Keep all favorites visible; this is a two-column shelf, not another filtered
catalog. Omit notes that have not been supplied, and omit the entire setup
block if there is no hardware to publish. Provided fields must be non-empty;
do not add placeholder specs or infer a personal reason for liking a game.
The existing paragraph, heading, list, ordered-list and table blocks still
work alongside these panels.

An intro or favorites/setup item may include an `image` with a local `src`
under `/assets/img/`, integer `width` and `height`, and an `alt` string.
Use `alt: ""` for a decorative illustration beside an already-labelled game.
Keep informative alt text for the avatar and hardware photos. Missing images,
invalid dimensions and remote image URLs fail the build. No image means no
placeholder or reserved thumbnail space.

Third-party images need a `credit` object inside `image`: `title`, `author`,
`source`, `license`, `license_url`, and optional `changes`. Link to the original
source and its actual reuse terms; public availability is not a license.
Credits are collected into an expandable **Image credits** list. Record
recoloring or other modifications, and identify representative imagery rather
than presenting it as a screenshot or a photo of a personally owned device.
The current themed icons are CC BY 3.0 illustrations from Game-icons.net;
the handheld photographs are public-domain images from Wikimedia Commons.
Their local copies live in `assets/img/profile/`, so rendering the page never
fetches artwork from third parties.

The list of games is not in here. `dcs_games` is the list of games, and
[`../tools/catalog.py`](../tools/catalog.py) reads it straight out of that
Godot project, so the site never keeps a second copy to fall out of date.
`tools/build.py` lists them under `/#games`, and `tools/export_games.py`
exports a page for each one plus `/play/`, which is all of them at once.

`game_cards` adds website-only presentation, keyed by the game's ID, not its
slug. Each entry has a short `description` and an `alt` describing what happens
in the artwork. Both are plain text, not inline markdown. The card's artwork,
title and copy are non-clickable; only its **Launch game** button opens the
game. Names, destinations and order still come from the Godot project.
Describe playable prototypes as prototypes, with their current scope rather
than planned features or unimplemented input methods.

Each entry also needs non-empty `genres` and `modes` arrays. Genres are plain
labels, such as `["Board", "Strategy"]`; reuse existing spellings when the
genre is the same. The genre filter is generated from active catalog cards,
so adding a new genre requires no HTML or JavaScript changes.

Modes describe actual human-player support: `solo` means one human, including
play against a CPU; `local` means multiple humans sharing a device; `online`
means networked multiplayer. A game can list several. Being playable in a
browser does **not** make it online multiplayer, and CPU opponents do not
make it local multiplayer. The **Any multiplayer** filter matches either
`local` or `online`. Only label capabilities the current game implements.

Artwork lives at `assets/img/games/<slug>.webp`: a checked-in, web-optimized
copy of the game's `assets/cover.png`, resized to 640×640 without cropping.
The source folder is normally the game's ID; `tuki_tuki` lives in
`tuki-tuki_agents`. To refresh a cover, resize the full image and export it
here as WebP at quality 90, then update its `alt` to match. Cards preserve
the square composition rather than cropping it to a gameplay frame.
The site build never reads private game folders, so a checkout without them
still renders the same cards.

A new catalog game without a `game_cards` entry still appears as a title-only
card, with a build warning. It remains visible in the unfiltered catalog and
title search, but cannot match a genre or play mode until classified. Once an
entry is supplied, both text fields, both arrays and its artwork must exist.
Invalid metadata or missing artwork fails the build instead of shipping a
broken card. Extra entries never add games or filter choices to the list.

The desktop grid has three columns and unlimited rows, with two columns on
tablets and one on phones. Search, genre and play-mode filters combine; the
live count, clear button and empty state follow the same matches. With
JavaScript disabled, the controls stay hidden and every game remains available.

Edit `site.json`, then:

```sh
python3 tools/build.py           # rewrite the generated blocks
python3 tools/build.py --check   # exit 1 if the pages are out of date
```

The rendered pages are committed, so the site stays static files with nothing
in front of them. The deploy runs `--check`, so a page that was not rebuilt
fails the build rather than going out stale.

The shape of the file, the blocks the Gamer Profile takes, and the inline
markdown its text can use are all documented at the top of
[`../tools/build.py`](../tools/build.py) — which is also what checks the file
and names the exact key it is unhappy about.
