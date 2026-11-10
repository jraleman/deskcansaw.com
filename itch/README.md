# deskcansaw.itch.io — the profile page

The itch profile is the shopfront: it holds the builds, and
[deskcansaw.com](https://deskcansaw.com) holds the pages that say what each
build actually is. This directory is the source for that profile — the same
identity as the site, expressed in the three things itch lets you change.

```
profile.html   the bio, for "edit profile" with the editor in HTML mode
theme.css      the custom CSS, for "edit theme" — optional, see below
preview.html   a local preview of the two above, on a stand-in of itch's layout
```

Everything here is the **light scheme** of [`../docs/style-guide.md`](../docs/style-guide.md).
An itch page has one scheme and no toggle, and light is the source of every
rule (§1) — so this is the site with the lights on, not a third design.

Look at it first:

```sh
python3 -m http.server 8000   # from the repo root, then
                              # http://localhost:8000/itch/preview.html
```

## 1. Theme editor — the colours

Profile → **Edit theme** → Colors. These six fields carry the design; the
rest of this directory only cleans up after them.

| Field | Value | Token | Why |
| --- | --- | --- | --- |
| BG | `#afdde9` | `--dcs-sky` | The page ground, and ~75% of the view (§2.3) |
| BG2 | `#f4eed7` | `--dcs-cream` | The paper the profile is read on |
| BG2 Alpha | `100%` | — | Flat fills only. No translucency over the ground (§4) |
| Text | `#333c45` | `--dcs-ink-700` | 9.64:1 on cream, 7.66:1 on sky (§2.8) |
| Link | `#205e6f` | `--dcs-deep-sky` | The go-there colour. 6.24:1 on cream |
| Buttons | `#e9c6af` | `--dcs-peach` | The press-me colour, and the only peach in view |
| Headers | `#21272d` | `--dcs-ink` | 11.65:1 on cream |

These two settings are the sentence in §1 made literal: a big calm field of
pale sky blue, with a warm cream shape sitting in the middle of it. The cream
is spent on the content column, which is why the game tiles are not cream —
see §5 below.

Leave the background *image* empty. A repeating image under a 75% field
fights it, and this palette is doing the work already.

**One thing to check by eye.** itch picks the button label colour itself from
the button fill. Peach wants ink `#21272d` on it (9.45:1); if itch picks white
you get 1.7:1, which is the one failure the editor can produce on its own.
`theme.css` pins it, but if you are running without custom CSS and the Follow
button reads white-on-peach, set Buttons to `#205e6f` deep-sky instead and
accept a page with no peach on it — an unreadable button is worse than a
missing accent.

## 2. Theme editor — type and shape

| Field | Value | Why |
| --- | --- | --- |
| Font | Roboto | Body face, already the site's (§3.1) |
| Header font | Silkscreen | The display face — pixel type as a spice, headings only |
| Font size | default | 16px body, `line-height: 1.7` (§3.2) |
| Corner radius | `12px` | Cards and panels (§4) |
| Shadow | none | The sample has no shadows, and neither does this (§4) |
| Banner | none for now | See below |

Silkscreen must never carry a paragraph and never go below 16px (§3.1) — as a
header font it only ever gets headings, which is exactly the intended use.

**The banner.** itch recommends 1920px wide. There isn't one in the repo yet;
until there is, no banner is better than a stretched one. When it gets drawn:
flat palette fills, a 2–2.5px slate line with round caps, no gradient, no glow
(§8) — the sticker sheet, not a key art render.

## 3. The bio

Profile → **Edit profile** → the description field, with the editor switched to
HTML. Paste [`profile.html`](profile.html) whole.

It says four things, in the order a stranger needs them: what this is, that the
labels are honest, which game to play first, and where else to look. Voice per
§9 — short sentences, first person, unembarrassed about the jank.

The status list is the part worth keeping in sync: it is the same four statuses
as [`../content/site.json`](../content/site.json) and the site, worded the same
way. If a status changes meaning there, change it here too — nothing generates
this file.

itch's sanitiser strips any class that does not begin with `custom-`, so the
three hooks in the markup (`custom-lede`, `custom-status-list`, `custom-links`)
are prefixed. They are hooks for §4 below and nothing else: with no custom CSS
loaded the bio is plain semantic HTML and reads correctly anyway. That is the
point — it degrades to something fine, rather than depending on CSS you may
never be granted.

## 4. Custom CSS — optional

[`theme.css`](theme.css) is the last 10%: flat surfaces instead of itch's drop
shadows, 12px game cells that lift 2px on hover, underlined links, the status
list as peach-100 tag pills, a visible focus ring.

Custom CSS is not on by default. You email itch support and ask for it, which
takes anywhere from days to weeks. Once it is granted: Profile → **Edit theme**
→ the CSS box at the bottom of the sidebar → paste the file.

Two rules from itch's guidelines shape the file, and any edit to it:

1. Every rule is scoped to `#wrapper`, so nothing leaks into itch's own chrome.
2. Only the documented class names are stable — `.game_cell`, `.game_thumb`,
   `.game_text`, `.formatted_description`, `.user_game_grid`, `.collection_row`.
   Anything else can change under you without warning.

Check it logged out and at 480px before calling it done; `preview.html` covers
the second, not the first.

## 5. Two deliberate deviations

**Metadata colour.** §3.2 puts small metadata on `--dcs-slate-400`. On cream
that measures 2.22:1 — the one value §2.8 marks ✗ — and itch's CSS guidelines
require the page stay readable. Metadata here is `--dcs-ink-700` at 13px
instead: the size carries the hierarchy, and the colour clears AAA. Same for
the tagline under the name.

**Tile fill.** On the site a project tile is cream on the sky ground. itch
gives the profile a content column and BG2 spends the cream on it, so a cream
tile would be a card on a card, which §4 forbids outright. The tiles take the
raised surface `--dcs-paper` instead, making the stack sky → cream → paper —
§4's three levels, in order. Without custom CSS itch's own near-white cell
lands in roughly the same place, so the page degrades correctly.

## Keeping it honest

Nothing in this directory is generated, and itch has no API here — the profile
is updated by pasting. Two things to re-paste when they change:

- the status list in `profile.html`, if the statuses change in
  `../content/site.json`
- the "Start here" paragraph, if a different game becomes the one to open with
