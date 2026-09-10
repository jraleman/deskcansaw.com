# DeskCanSaw.com

The source for [deskcansaw.com](https://deskcansaw.com) — a retro video game
lover's site and the shopfront for small indie game concepts.

The visual identity lives in [`style-guide.md`](style-guide.md): one palette
sampled from [`assets/img/avatar.png`](assets/img/avatar.png), light and dark,
plus the type scale, components and voice the site is built to.

---

## The repo

Static HTML on GitHub Pages. No build step, no dependencies — what is in the
repo is what gets served.

```
index.html            the holding page that is live now
preview.html          the full site, one page, ahead of being split up
style-guide.md        the visual identity — the source of truth for §-numbers
                      referenced from the CSS comments
CNAME                 deskcansaw.com
.nojekyll             serve the files as they are; skip Jekyll
favicon.*             site icons, which belong at the root
apple-touch-icon.png

tools/build.py        renders the parts of the page this README owns
                      (the game list, the statuses, Files, Gamer Profile)

itch/                 the source for the deskcansaw.itch.io profile — the bio,
                      the theme editor values and the custom CSS. Pasted by
                      hand; itch has no API for it. See itch/README.md.

assets/css/
  tokens.css          colour, type, spacing, shape, motion. Every value in the
                      style guide lands here and nowhere else.
  base.css            reset, the 10px root scale, elements, text roles
  components.css      buttons, cards, tags, tables, wells, frames, the toggle
  layout.css          side nav, content column, hero, footer — full site pages
  holding.css         the one page-specific stylesheet, for index.html
assets/js/
  color-scheme.js     the day/night toggle
  scroll-spy.js       marks the nav item for the section in view
assets/img/
  avatar.png
```

Stylesheets are linked in dependency order — `tokens`, `base`, `components`,
then whichever of `layout`/`holding` the page needs. Two rules keep it that
way: component CSS reads the semantic tokens (`var(--dcs-surface)`) and never a
raw scheme colour, and markup carries classes rather than a `style` attribute.

A new page is a copy of `preview.html`'s `<head>`, the same four `<link>` tags,
and the four-line inline script that sets the colour scheme before first paint.

## This README is the content

Most of the site's content is written here and rendered into the page, so the
game list can't drift out of sync with the one on the site:

| Block | Comes from |
| --- | --- |
| `profile` | everything under `## Gamer Profile` |
| `games` | the list under `### List of games:` |
| `statuses` | the status table under `## Games` |
| `file-kinds` | the `**Kind** — description` bullets under `## Files` |
| `file-rules` | the numbered rules under `## Files` |

Lists and tables are generated; the prose around them is written per medium,
because a README paragraph and a page paragraph are not the same sentence.
`## Gamer Profile` is the exception — that whole section is rendered as it is
written here.

A game line is ``Name (`status`): description``, or
``[Name](url) (`status`): description`` once it has its own page. Cards come out
in status order — released first, concept last — and a `released` game without
its own URL links to the itch profile.

Edit this file, then:

```sh
python3 tools/build.py           # rewrite the generated blocks
python3 tools/build.py --check   # exit 1 if the pages are out of date
```

The output is committed, so the site stays static files with nothing in front
of them. Everything outside the `<!-- generated:… -->` markers is written by
hand and the script leaves it alone.

## Running it locally

Paths are absolute from the site root, so open it over HTTP rather than from
the filesystem:

```sh
python3 -m http.server 8000   # then http://localhost:8000
```

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
output of this table — if something here changes, the tools I can write change
with it.

| Thing | What I run |
| --- | --- |
| Consoles | TBD |
| Handhelds | TBD |
| Display | TBD |
| Emulation | TBD |
| Dump and flash | TBD |
| Patching | TBD |

TBD — a paragraph on how it all actually gets used.

### Favorites

- The Legend of Zelda: Ocarina of Time [SoH]
- Super Mario 64: 16 Stars [Emu]
- Super Mario Bros. [Emu]
- Rocket League [Epic]
- Phantasy Star Online: Blue Burst [Ephinea]
- Old School Runescape [Mobile]
- Duolingo [Mobile]
- Cells to Singularity [Mobile]

## Games — `deskcansaw.itch.io`

Where the playable things live. Downloads and browser builds go up on
[deskcansaw.itch.io](https://deskcansaw.itch.io); this site keeps the pages that
say what each one actually is.

Every project carries a status, used plainly:

| Status | What it means |
| --- | --- |
| `concept` | An idea and maybe some art. Nothing to play. |
| `prototype` | Runs, proves one mechanic, ugly. |
| `playable` | You can finish it. Rough edges expected. |
| `released` | Done and on itch. |

### List of games:

- Desk Can Saw (`released`): Takes place on a DESK. Watch out for the sliding CANs. Slice them with a shmooving electric SAW ;)
- Triangle Rush (`released`): Press the key that matches with the triangle, be quick and earn a high score!
- Chicken Pit (`released`): Don't fall into the chicken pit! Beat your opponent in this tug-o-war game.
- Dead Metal Jam (`released`): Play with your musical instrument, use your voice, or make some noise to destroy evil robots!
- Anti-Chess (`playable`): A chess game, but you have to lose to win!
- EkiZero (`playable`): Play some tic-tac-toe with a small dinosaur.
- Wolf3D (`prototype`): Wolfenstein3D but there are portals and more vibes. Some ASCII art as well ;)
- Crunchy Chests (`prototype`): Move the chests, crunch them to unlock more chests. Get all the chests and win the chests game. You may need some chest hair.
- Florida Men, Presents... (`prototype`): Beat your opponents in this styled american-ware minigames based on "Florida Man" headlines.
- Tuki-Tuki, Los Agentes (`concept`): Dance for your life, beat your opponents and gain territory, conquer "Rojo Tinto"!
- Anti-Checkers (`concept`): You have to lose in this game of checkers to win!
- Dulce's Adventures (`concept`): (jumping/platformer) TBD
- Julio's Walk (`concept`): (physics/simulator) TBD
- Baloo's Chase (`concept`): (chase/stamina) TBD
- Best Vaper (`concept`): (mic) TBD
- Glitchidle (`concept`): (idle game) TBD

## Files

The archive: saves, tools, patches, romhacks and anything else I've made or
collected while poking at old games.

- **Save files** — Completed saves, useful mid-game states, testing saves.
- **Tools** — Small utilities for editing, extracting or converting game data.
- **Patches** — IPS/BPS patches. Patches only, never a patched ROM.
- **Romhacks** — My own hacks, and notes on hacks I like.
- **Notes** — Format documentation and teardowns from figuring the above out.

Rules for this section:

1. No copyrighted ROMs or game assets. Patches and tools, bring your own copy.
2. Every file says what it's for, what it was made with, and what it runs on.
3. Nothing goes up untested. If it's known-broken, the page says so.

## Videos

The YouTube side of it: playthroughs, build logs from whatever's on itch, and
teardowns of the files above.

Videos are embedded on the site next to the thing they're about — a devlog sits
on its project page, a romhack demo sits with the patch. The channel is the
feed; this site is where a video has context around it.

https://youtube.com/@deskcansaw
