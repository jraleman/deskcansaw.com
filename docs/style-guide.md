# DeskCanSaw — Site Style Guide

The visual identity for **deskcansaw.com**: a retro video game lover's site and
the shopfront for small indie game concepts.

One document, two schemes. Light is the default and the source of every rule;
dark is a *lighting change, not a personality change*. Where a section says
nothing about dark, dark is identical.

---

## 1. The idea in one paragraph

A big calm field of pale sky blue, a warm cream shape sitting in the middle of
it, and a hand-drawn slate line doing all the describing. One peach accent,
used sparingly, for the thing you're meant to press. It reads like a sticker
sheet or a game manual illustration from a console generation that had good
art directors and cheap printing — friendly, hand-made, unhurried, and
completely unlike a dark "gamer" site. The retro comes from *ink and paper*,
not from neon and scanlines.

Three words: **airy, hand-drawn, warm.**

### 1.1 The same idea at night

The lights go off in the room, not in the drawing. A deep blue-black field, a
slate-blue card sitting in the middle of it, and the same hand-drawn line doing
all the describing — except the line is now the light thing and the paper is
the dark thing. Cream, which was the paper, is promoted to headings. Sky, which
was the whole ground, shrinks down to a single bright accent and carries the
links. Peach stays exactly where it was: one warm press-me thing per screen.
It should read like the same sticker sheet photographed at night, not like a
different site.

Three words: **airy, hand-drawn, warm** — unchanged.

### 1.2 What this is not

- Not neon-on-black. No purple/cyan gradients, no glow, no CRT scanline overlay.
  Turning the lights off is not permission for any of them.
- Not pixel-art everywhere. Pixel type is a **spice**, used at small sizes for
  labels and numbers — never for body copy.
- Not flat corporate. Lines wobble, corners are soft, shapes overlap.
- Not pure black on pure white. The dark ground is `#0e1519`, never `#000`; the
  brightest dark text is cream `#f4eed7`, never `#fff` (18.42:1 white-on-night
  is halation, not contrast).
- Not the light scheme with `filter: invert()`. Peach and sky keep their hues.
  Only their *jobs* change.

---

## 2. Colour

### 2.1 The sampled palette

Six colours, taken directly from `sample.png` with their share of the image.
The share column matters: it *is* the recommended usage ratio.

| Token | Hex | RGB | % of sample | Role |
| --- | --- | --- | --- | --- |
| `--dcs-sky` | `#afdde9` | 175, 221, 233 | 75.1% | Page ground. The default background of everything. |
| `--dcs-cream` | `#f4eed7` | 244, 238, 215 | 11.3% | Cards, panels, post bodies — the "paper" you read on. |
| `--dcs-slate` | `#495663` | 73, 86, 99 | 2.5% | Linework, borders, icon strokes, the drawn outline. |
| `--dcs-peach` | `#e9c6af` | 233, 198, 175 | 2.2% | **The** accent. Buttons, active state, highlights. |
| `--dcs-ice` | `#ecf0f1` | 236, 240, 241 | 1.8% | Cool highlight / raised facet inside a cream panel. |
| `--dcs-paper` | `#f9f9f9` | 249, 249, 249 | 1.1% | Brightest highlight, input fields, top nav. |

### 2.2 The inversion

Same six colours at night. Three of them change job entirely.

| Token | Hex | Light role | **Dark role** |
| --- | --- | --- | --- |
| `--dcs-sky` | `#afdde9` | Page ground (75%) | **Links, focus ring, accent (~2%)** |
| `--dcs-cream` | `#f4eed7` | Reading surface | **Headings** |
| `--dcs-slate` | `#495663` | Linework, borders | Retired — too dark to see on night |
| `--dcs-peach` | `#e9c6af` | Accent | Accent — **unchanged** |
| `--dcs-ice` | `#ecf0f1` | Raised facet | Retired — replaced by `--dcs-deep-100` |
| `--dcs-paper` | `#f9f9f9` | Nav, inputs | Retired — nav drops to `--dcs-deep` |

The dark ground itself is not one of the six. It comes from the game palette, so
the site and the builds share a background:

| Token | Hex | Source | Role |
| --- | --- | --- | --- |
| `--dcs-night` | `#0e1519` | game `INK` | Page ground |
| `--dcs-deep` | `#172a33` | game `DEEP`, pushed toward sky | Cards, panels, nav |
| `--dcs-night-700` | `#2f4753` | game palette | Decorative panel edge |

### 2.3 The 75/11/5/2 rule

The sample is doing something worth copying: it is *overwhelmingly* one colour.
Hold to roughly that ratio on every screen, in both schemes — only the ink is
inverted.

```
light                                            dark
███████████████████████████████████████████████  sky / night    ~75%   background
███████                                          cream / deep   ~11%   reading surfaces
██                                               slate / mist    ~5%   type + lines
█                                                peach           ~2%   one accent per view
                                                 ice, paper / sky       highlights, links
```

Practical reading: **one peach thing per viewport.** If a page has a primary
button, that button is peach and nothing else is. If two elements are competing
to be peach, one of them is wrong.

Dark makes this harder, because sky is now bright too. Two rules keep the accent
budget honest:

1. Peach is the *press-me* colour. Sky is the *go-there* colour. Never use sky
   as a button fill or peach as a link — that ambiguity is invisible in light
   (where both are quiet) and glaring in dark.
2. A paragraph dense with sky links reads as noise on night. If a block runs
   past three links, that block wants a list, not more colour.

### 2.4 Derived tokens — light

Generated from the six above. The operation is given so any missing step can be
recreated — `mix(a, b, t)` is a straight linear RGB blend, `t` = amount of `b`.

**Ink scale** — `mix(slate, #000, t)`. Slate itself is a *line* colour; it is
too light for long body copy on cream, so text uses the darker steps.

| Token | Hex | Derivation | Use |
| --- | --- | --- | --- |
| `--dcs-ink` | `#21272d` | `mix(slate, #000, .55)` | Headings, maximum-emphasis text |
| `--dcs-ink-700` | `#333c45` | `mix(slate, #000, .30)` | Body copy |
| `--dcs-slate` | `#495663` | — | Borders, rules, illustration strokes |
| `--dcs-slate-400` | `#9ba2a9` | `mix(slate, #fff, .45)` | Muted text, captions, metadata |
| `--dcs-slate-200` | `#ccd0d3` | `mix(slate, #fff, .72)` | Hairlines, disabled edges |

**Sky scale** — the ground and its quieter/deeper cousins.

| Token | Hex | Derivation | Use |
| --- | --- | --- | --- |
| `--dcs-sky-100` | `#e9f5f9` | `mix(sky, #fff, .72)` | Zebra rows, hover on cream |
| `--dcs-sky-200` | `#d3ecf3` | `mix(sky, #fff, .45)` | Section bands, code block ground |
| `--dcs-sky` | `#afdde9` | — | Page background |
| `--dcs-sky-600` | `#7a9ba3` | `mix(sky, #000, .30)` | Sky-on-sky borders, muted icons |
| `--dcs-deep-sky` | `#205e6f` | sky hue @ 28% L, 55% S | **Links**, focus ring, active nav |

**Warm scale** — peach and its readable form. Peach at full strength has a
1.37:1 contrast on cream, so it can never carry text; when a *word* needs to be
warm, use `--dcs-rust`.

| Token | Hex | Derivation | Use |
| --- | --- | --- | --- |
| `--dcs-peach-100` | `#f9efe9` | `mix(peach, #fff, .72)` | Warm hover wash, tag background |
| `--dcs-peach` | `#e9c6af` | — | Primary button fill, active tab, badges |
| `--dcs-peach-600` | `#a38b7a` | `mix(peach, #000, .30)` | Border under a peach fill |
| `--dcs-rust` | `#7e4f30` | peach hue @ 34% L, 45% S | Warm text, "new"/"WIP" labels |

### 2.5 Derived tokens — dark

Same operation, derived from the sampled six or from `--dcs-night` /
`--dcs-deep`.

**Surface scale** — the stack climbs *toward the sky*, not toward white.

| Token | Hex | Derivation | Use |
| --- | --- | --- | --- |
| `--dcs-night` | `#0e1519` | — | Page ground, recessed wells (code) |
| `--dcs-deep` | `#172a33` | game `DEEP`, pushed toward sky | Cards, panels, nav, footer |
| `--dcs-deep-100` | `#233d48` | `mix(deep, sky, .08)`, lightened | Raised facet, inset, secondary button |
| `--dcs-night-700` | `#2f4753` | — | Decorative edge — see the warning in §2.8 |

**Mist scale** — the ink scale, run the other way. Note the symmetry: dark's
body text `#cbd8de` sits one step from light's *hairline* colour `#ccd0d3`. The
scale is the same scale; dark just reads it from the top.

| Token | Hex | Derivation | Use |
| --- | --- | --- | --- |
| `--dcs-cream` | `#f4eed7` | — | Headings, maximum-emphasis text |
| `--dcs-mist` | `#cbd8de` | — | Body copy |
| `--dcs-slate-400` | `#9aabb3` | `mix(slate, sky, .45)` | Muted text, captions, metadata, illustration strokes |
| `--dcs-slate-500` | `#768f9a` | `mix(slate, sky, .25)` | Placeholder text; **functional** borders |

**Accent scale** — sky, promoted.

| Token | Hex | Derivation | Use |
| --- | --- | --- | --- |
| `--dcs-sky-100` | `#e9f5f9` | `mix(sky, #fff, .72)` | Link hover, active nav text |
| `--dcs-sky` | `#afdde9` | — | Links, focus ring |
| `--dcs-sky-dim` | `#25454f` | `mix(sky, night, .78)`, saturated | Neutral badge ground, quiet band |

**Warm scale** — peach, unchanged in fill, promoted in text. The light rule
"peach can never carry text" **inverts**: on night, peach is a 11.55:1 text
colour. `--dcs-rust` is retired (3.14:1 on night — fails).

| Token | Hex | Derivation | Use |
| --- | --- | --- | --- |
| `--dcs-peach-tint` | `#f0d7c7` | `mix(peach, #fff, .30)` | Primary button hover fill |
| `--dcs-peach` | `#e9c6af` | — | Primary fill, **and** warm text / "WIP" labels |
| `--dcs-peach-dim` | `#46372f` | `mix(peach, night, .76)`, warmed | Tag ground |
| `--dcs-ink` | `#21272d` | — | Text *on* peach, sky or cream fills |

### 2.6 Semantic mapping

| Purpose | Light token | Hex | Dark token | Hex |
| --- | --- | --- | --- | --- |
| Page background | `--dcs-sky` | `#afdde9` | `--dcs-night` | `#0e1519` |
| Card / panel / post body | `--dcs-cream` | `#f4eed7` | `--dcs-deep` | `#172a33` |
| Nav, header | `--dcs-sky-100` | `#e9f5f9` | `--dcs-deep` | `#172a33` |
| Raised facet / inset | `--dcs-ice` | `#ecf0f1` | `--dcs-deep-100` | `#233d48` |
| Body text | `--dcs-ink-700` | `#333c45` | `--dcs-mist` | `#cbd8de` |
| Headings | `--dcs-ink` | `#21272d` | `--dcs-cream` | `#f4eed7` |
| Muted / metadata | `--dcs-slate` | `#495663` | `--dcs-slate-400` | `#9aabb3` |
| Decorative border, `<hr>` | `--dcs-sky-600` | `#7a9ba3` | `--dcs-night-700` | `#2f4753` |
| Functional border (input, active) | `--dcs-slate` | `#495663` | `--dcs-slate-500` | `#768f9a` |
| Link | `--dcs-deep-sky` | `#205e6f` | `--dcs-sky` | `#afdde9` |
| Link hover | `--dcs-ink` | `#21272d` | `--dcs-sky-100` | `#e9f5f9` |
| Warm text | `--dcs-rust` | `#7e4f30` | `--dcs-peach` | `#e9c6af` |
| Primary button fill | `--dcs-peach` | `#e9c6af` | `--dcs-peach` | `#e9c6af` |
| Primary button text | `--dcs-ink` | `#21272d` | `--dcs-ink` | `#21272d` |
| Focus ring | `--dcs-deep-sky` | `#205e6f` | `--dcs-sky` | `#afdde9` |

Light metadata reads in `--dcs-slate`, not `--dcs-slate-400`: slate-400 is
1.76:1 on the sky ground, and the sky is where the hero subtitle, footer and
captions sit. The light decorative border is `--dcs-sky-600`, because
slate-200 is 1.06:1 against sky and cards lost their drawn outline. Dark's
`--dcs-slate-400` is its own hex, `#9aabb3` (`mix(slate, sky, .45)`).

### 2.7 What does not flip

- **Peach fills and their labels.** `--dcs-ink` on `--dcs-peach` is 9.45:1 in
  both schemes. A primary button is pixel-identical light and dark — which is
  the point: it is the one fixed landmark across the toggle.
- **Illustration fills.** Cream, peach and sky fills inside a drawing stay put.
  Only the *stroke* changes (§4).
- **Radii, spacing, motion, type scale.** Identical.

### 2.8 Contrast — measured, not assumed

All ratios below are computed WCAG 2.1 values. Anything used for body copy
clears AA (4.5:1); everything listed clears it comfortably.

**Light.**

| Foreground | Background | Ratio | Verdict |
| --- | --- | --- | --- |
| `#333c45` ink-700 | `#f4eed7` cream | **9.64** | AAA |
| `#333c45` ink-700 | `#afdde9` sky | **7.66** | AAA |
| `#21272d` ink | `#f4eed7` cream | **11.65** | AAA |
| `#21272d` ink | `#e9c6af` peach | **9.45** | AAA — button label |
| `#205e6f` deep-sky | `#f4eed7` cream | **6.24** | AAA (normal text) |
| `#205e6f` deep-sky | `#afdde9` sky | **4.96** | AA |
| `#7e4f30` rust | `#f4eed7` cream | **5.92** | AA |
| `#7e4f30` rust | `#afdde9` sky | **4.71** | AA — eyebrows, h2 stub |
| `#495663` slate | `#afdde9` sky | **5.13** | AA — muted text on the ground |
| `#7a9ba3` sky-600 border | `#afdde9` sky | **2.04** | Decorative outline (was slate-200, 1.06) |
| `#495663` slate | `#f4eed7` cream | **6.46** | AA — lines/large text only, by role |
| `#9ba2a9` slate-400 | `#f4eed7` cream | **2.22** | ✗ Large/decorative only |

**Dark.**

| Foreground | Background | Ratio | Verdict |
| --- | --- | --- | --- |
| `#cbd8de` mist | `#172a33` deep | **10.19** | AAA — body on a card |
| `#cbd8de` mist | `#0e1519` night | **12.65** | AAA — body on the ground |
| `#cbd8de` mist | `#233d48` deep-100 | **7.87** | AAA |
| `#f4eed7` cream | `#172a33` deep | **12.76** | AAA — headings |
| `#f4eed7` cream | `#0e1519` night | **15.84** | AAA |
| `#afdde9` sky | `#172a33` deep | **10.13** | AAA — links |
| `#afdde9` sky | `#0e1519` night | **12.58** | AAA |
| `#e9f5f9` sky-100 | `#172a33` deep | **13.35** | AAA — link hover |
| `#e9c6af` peach | `#172a33` deep | **9.30** | AAA — warm text |
| `#e9c6af` peach | `#0e1519` night | **11.55** | AAA |
| `#21272d` ink | `#e9c6af` peach | **9.45** | AAA — button label |
| `#21272d` ink | `#f0d7c7` peach-tint | **10.95** | AAA — button label, hover |
| `#9aabb3` slate-400 | `#172a33` deep | **6.25** | AA — metadata |
| `#9aabb3` slate-400 | `#233d48` deep-100 | **4.83** | AA — metadata on an inset |
| `#768f9a` slate-500 | `#172a33` deep | **4.36** | AA large / placeholder only |
| `#e9c6af` peach | `#46372f` peach-dim | **7.12** | AA — tag text |
| `#cbd8de` mist | `#25454f` sky-dim | **7.06** | AA — neutral badge |

**Non-text contrast, dark (WCAG 1.4.11, needs 3:1).**

| Element | Against | Ratio | Verdict |
| --- | --- | --- | --- |
| `#768f9a` slate-500 border | `#233d48` deep-100 | **3.36**–5.41 | Passes on every surface |
| `#afdde9` sky focus ring | `#0e1519` night | **12.58** | Passes |
| `#afdde9` sky focus ring | `#233d48` deep-100 | **7.83** | Passes |
| `#2f4753` night-700 border | `#172a33` deep | **1.52** | ✗ Decorative only |

> **The one dark-specific trap.** `--dcs-night-700` is a *mood* line, not a
> boundary. It is fine as the hairline between rows in a table or the `<hr>` in
> a post. It must never be the only thing telling you where an input begins,
> which tab is active, or that a card is selected — those all take
> `--dcs-slate-500` at 1.5px, or a surface-value change. The light scheme can
> get away with a whisper-quiet border; dark cannot.

**Never do — light:** peach text on cream (1.37), sky text on cream (1.26),
slate-400 on sky (1.76).

**Never do — dark:** slate `#495663` as text or stroke on night (2.45), rust
`#7e4f30` on night (2.7), deep-sky `#205e6f` on night (2.54) — the light
scheme's link colour is invisible here, which is exactly why the schemes swap.
And never pure white text: `#fff` on night is 18.42 and blooms.

If it needs to be read, it comes from that scheme's text scale.

---

## 3. Typography

### 3.1 The pairing

The site currently loads Roboto only. The retro character should come from a
**display face used at small sizes**, with a neutral, extremely readable body
face carrying everything else.

| Role | Face | Weight | Notes |
| --- | --- | --- | --- |
| Display / page title | `"Silkscreen"` | 400/700 | Pixel face with real lowercase; legible at 24px+ |
| Body, UI, nav | `"Roboto"` | 300/400/500/700 | Already in the theme — keep it |
| Numerals, scores, timers | `"VT323"` or Roboto tabular | 400 | Speedrun times, version numbers, score tables |
| Code | `ui-monospace, "SFMono-Regular", Consolas, monospace` | 400 | System stack; no webfont cost |

To load them, replace the URL in `_data/conf/main.yml`:

```yaml
google_font_style_url: https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Silkscreen:wght@400;700&family=VT323&display=swap
```

**Pixel-type rules.** Silkscreen and VT323 render on a fixed grid; anything that
fights that grid looks broken.

- Never below 16px, never as a paragraph, never italic, never faux-bold.
- Set `letter-spacing: 0` — pixel faces already carry their own spacing.
- Only whole-pixel font sizes (16, 24, 32, 40) so stems stay crisp.
- Always pair with a real fallback: `"Silkscreen", "Roboto", sans-serif`.

Faces, the loading URL and these rules are identical in both schemes.

### 3.2 Scale

The theme sets `html { font-size: 10px }` (9px ≤500px, 8px ≤360px), so
`1rem = 10px` and the existing heading sizes are already `2.6rem = 26px` etc.
Keep that base; these are the intended values. Sizes and weights are the same in
both schemes — the colour column gives light first, dark second.

| Element | Size | Weight | Colour (light / dark) | Notes |
| --- | --- | --- | --- | --- |
| Home hero | `4.8rem` / 48px | 400 Silkscreen | `--dcs-ink` / `--dcs-cream` | Single line, never wraps on desktop |
| Hero subtitle | `1.8rem` / 18px | 400 Roboto | `--dcs-slate-400` | "Weird little games" |
| `h1` | `2.6rem` | 700 | `--dcs-ink` / `--dcs-cream` | One per page |
| `h2` | `2.5rem` | 700 | `--dcs-ink` / `--dcs-cream` | Gets a 2px `--dcs-peach` rule under it |
| `h3` | `2.35rem` | 700 | `--dcs-ink` / `--dcs-cream` | |
| `h4`–`h6` | `2.2`–`2.0rem` | 500 | `--dcs-ink-700` / `--dcs-mist` | |
| Eyebrow / label | `1.2rem` | 700 | `--dcs-rust` / `--dcs-peach` | `text-transform: uppercase; letter-spacing: .12em` |
| Body | `1.6rem` / 16px | 400 | `--dcs-ink-700` / `--dcs-mist` | `line-height: 1.7` |
| Small / meta | `1.3rem` | 400 | `--dcs-slate-400` | Dates, tags, read time |
| Score / time | `2.0rem` | 400 VT323 | `--dcs-ink` / `--dcs-cream` | `font-variant-numeric: tabular-nums` |

Measure: cap body copy at **68 characters**. The theme's
`--main-container-width-limit: 800px` with 16px body lands close; do not widen it.

### 3.3 Dark-only corrections

Light type on a dark ground renders visually *bolder* than the same type
inverted. Three weight corrections follow from that:

| Element | Light | **Dark** | Why |
| --- | --- | --- | --- |
| Body | `400` | `400` | Never `500` to "fix" legibility — it smears |
| Roboto Light `300` | Allowed | **Banned** | Hairline stems disappear at 16px on night |
| Silkscreen headings | `700` allowed | `400` below 32px | Bold pixel stems fill their own counters |

**Halation.** If a cream heading looks like it is glowing, the problem is
almost always `font-weight: 700` at a large size, not the colour. Drop the
weight before you touch the hex.

---

## 4. Shape, surface and depth

The sample has no gradients, no blur and no drop shadows — it is flat fills with
a drawn outline. The site follows. Radii are the same in both schemes.

| Property | Value | Applies to |
| --- | --- | --- |
| Radius — cards, panels | `12px` | Post cards, project tiles, about panel |
| Radius — buttons, tags | `8px` | Buttons, pills, tabs |
| Radius — inputs | `8px` | Search, contact form |
| Radius — thumbnails | `12px` | Post/project images |
| Border | `1.5px solid var(--dcs-slate-200)` | Default panel edge (light) |
| Border — emphasis | `2px solid var(--dcs-slate)` | Featured card, active tab (light) |
| Shadow — light | **none** by default | — |
| Shadow — light, floating only | `0 2px 0 var(--dcs-slate-200)` | Dropdown, sliding message box |
| Shadow — dark | **none, ever** | See below |

The "floating" shadow is a hard offset with no blur — a printed-sticker
shadow, not a Material elevation. If it looks like a soft glow, it's wrong.

**Dark has no shadows at all.** On night a dark shadow is invisible
(deep-on-night is 1.12:1) and a light one is the glow this site does not do.

**Surface stack.** Three levels maximum, in both schemes. A card never sits on
another card.

| Level | Light | Dark surface | Dark border | Example |
| --- | --- | --- | --- | --- |
| 0 — ground | `--dcs-sky` | `--dcs-night` `#0e1519` | — | Page |
| 1 — card | `--dcs-cream` | `--dcs-deep` `#172a33` | `1.5px --dcs-night-700` | Post card, project tile |
| 2 — raised | `--dcs-ice` / `--dcs-paper` | `--dcs-deep-100` `#233d48` | `1.5px --dcs-slate-500` | Dropdown, sliding message box, active tab |
| −1 — well | `--dcs-sky-200` | `--dcs-night` `#0e1519` | `1.5px --dcs-night-700` | Code block, inset figure |

The well is the one place a surface goes *back down* — a code block recessing to
the page ground is how dark says "this is not prose".

**Illustration.** Anything hand-drawn (icons, dividers, 404 art, project
thumbnails) uses 2–2.5px strokes with round caps and joins, filled from the
palette. Strokes are `--dcs-slate` in light and `--dcs-slate-400` `#9aabb3`
(6.46:1 on night) in dark; fills stay cream, peach and sky, with
`--dcs-deep-100` in place of ice. Strokes may wobble; they must never be pure
black. Author SVGs with `stroke="currentColor"` and set the colour on the
wrapper — one asset then serves both schemes with no second file.

---

## 5. Spacing and layout

Identical in both schemes. An 8px base unit; the theme's fluid `--text-spacing`
and `--main-container-margin` handle the page gutters already.

| Step | Value | Use |
| --- | --- | --- |
| `xs` | 4px | Icon–label gap |
| `sm` | 8px | Inside a pill, tight stacks |
| `md` | 16px | Card padding, paragraph rhythm |
| `lg` | 24px | Card interior padding, gap between cards |
| `xl` | 40px | Between page sections |
| `2xl` | 64px | Above/below the home hero |

Grid: content column max 800px (theme default). Project and post-list cards run
in a responsive grid — 3 up ≥1024px, 2 up ≥640px, 1 up below, `24px` gap.

---

## 6. Components

Geometry is shared: height 40px and padding `0 20px` on buttons, 12px radius and
24px padding on cards, 8px radius on pills and inputs, `all .16s ease-out` on
every hover. Only colour and, where noted, the hover affordance differ.

### 6.1 Buttons

**Light.**

| Variant | Fill | Text | Border | Hover |
| --- | --- | --- | --- | --- |
| Primary | `--dcs-peach` | `--dcs-ink` | `1.5px --dcs-peach-600` | fill → `#f3e0d3`, translate `-1px` Y |
| Secondary | `--dcs-cream` | `--dcs-ink-700` | `1.5px --dcs-slate-200` | border → `--dcs-slate` |
| Ghost | transparent | `--dcs-deep-sky` | none | underline |

**Dark.**

| Variant | Fill | Text | Border | Hover |
| --- | --- | --- | --- | --- |
| Primary | `--dcs-peach` | `--dcs-ink` | none | fill → `--dcs-peach-tint`, translate `-1px` Y |
| Secondary | `--dcs-deep-100` | `--dcs-mist` | `1.5px --dcs-slate-500` | border → `--dcs-mist` |
| Ghost | transparent | `--dcs-sky` | none | underline |

Weight 500, one primary per view (see §2.3). Dark makes two changes: the primary
button drops its `--dcs-peach-600` border (a mid-tone edge around a bright fill
on a dark ground reads as a halo), and secondary's hover moves the border rather
than tinting the fill. Transition `all .16s ease-out` — matches the game's
interactive timing.

### 6.2 Links

Underlined with `text-decoration-thickness: 1.5px; text-underline-offset: 3px`.
Body links are `--dcs-deep-sky` in light, hovering to `--dcs-ink`; `--dcs-sky`
in dark, hovering to `--dcs-sky-100`. Note the direction flip: in light, hover
*darkens* toward ink; in dark, hover *brightens* toward white. Both move toward
maximum emphasis, and both keep the underline.

Never remove the underline in body copy; nav and button links are the only
exception. Underlines are load-bearing in dark in a way they aren't in light —
sky against mist is a hue shift more than a value shift.

### 6.3 Cards (posts, projects, game archive)

12px radius, 24px padding, no shadow, `1.5px` border. Light: cream fill,
`--dcs-slate-200` border, hover moves the border to `--dcs-slate` with
`translateY(-2px)`. Dark: `--dcs-deep` fill, `--dcs-night-700` border, hover
moves the border to `--dcs-slate-500`, lifts the same `-2px`, **and** raises the
fill to `--dcs-deep-100` — a 1.36:1 border moving to 3.20:1 is a small signal on
its own. Both at `.16s ease-out`.

Thumbnail sits flush to the card's top edge with matching top corners.
Metadata line is `1.3rem --dcs-slate-400`. Tags are peach-100 pills with rust
text in light, `--dcs-peach-dim` pills with `--dcs-peach` text in dark.

### 6.4 Navigation

Side nav (`230px`, theme default) sits on `--dcs-paper` over sky in light and on
`--dcs-deep` over night in dark — lighter than the page in both. The
relationship survives the flip; the values don't.

Active item: peach 8px-radius background, ink text — the same landmark in both
schemes. Hover: `--dcs-sky-100` in light, `--dcs-deep-100` in dark. The brand
text uses the display face at `2.3rem` (`--dcs-cream` in dark) — the theme
variable `--side-nav-brand-text-font-size` is already set for it.

The active nav item is peach, so it **is** the viewport's one peach thing on any
page that doesn't have a primary button. A page with both an active nav item and
a peach CTA is over budget — make the CTA the peach one and drop the nav item to
a quiet raised background (`--dcs-sky-100` light, `--dcs-deep-100` with
`--dcs-sky-100` text in dark).

### 6.5 Tags, badges, status

| Kind | Light background | Light text | Dark background | Dark text |
| --- | --- | --- | --- | --- |
| Tag / category | `--dcs-peach-100` | `--dcs-rust` | `--dcs-peach-dim` `#46372f` | `--dcs-peach` |
| "New" / "WIP" | `--dcs-peach` | `--dcs-ink` | `--dcs-peach` | `--dcs-ink` |
| Neutral / count | `--dcs-sky-200` | `--dcs-ink-700` | `--dcs-sky-dim` `#25454f` | `--dcs-mist` |
| Released | `--dcs-cream` + `1.5px --dcs-slate-200` | `--dcs-ink-700` | `--dcs-deep-100` + `1.5px --dcs-night-700` | `--dcs-mist` |

All: 8px radius, `1.2rem`, weight 700, padding `2px 8px`, uppercase.

### 6.6 Code blocks

`1.5px` border, 8px radius, 16px padding, `1.4rem` monospace.

- **Light:** ground `--dcs-sky-200`, `--dcs-slate-200` border, `--dcs-ink` text.
  Inline code on a `--dcs-sky-100` ground, 4px radius, `0 4px` padding.
- **Dark:** ground `--dcs-night` (recessed, §4), `--dcs-night-700` border,
  `--dcs-mist` text. Inline code goes *up* to `--dcs-deep-100` so it stays
  visible mid-sentence on a card.

Syntax highlighting, if any, draws from the palette only: keywords sky/deep-sky,
strings peach/rust, comments `--dcs-slate-400`, everything else the body text
colour. No red/green/purple rainbow.

### 6.7 Forms

Inputs take the raised surface, a **functional** border and 8px radius. Light:
`--dcs-paper` surface, `1.5px --dcs-slate-200`, `--dcs-ink-700` text. Dark is
the component that needs real work: `--dcs-deep-100` surface,
`1.5px --dcs-slate-500` border (3.20:1 — the decorative `--dcs-night-700` is not
legal here), `--dcs-mist` text, `--dcs-slate-500` placeholder. Focus adds the
ring below *and* moves the border to the scheme's link colour.

### 6.8 Focus

```css
:focus-visible {
  outline: 2px solid var(--dcs-deep-sky);   /* light */
  outline-offset: 2px;
  border-radius: 4px;
}

body[data-color-scheme="dark"] :focus-visible {
  outline-color: var(--dcs-sky);
}
```

Never `outline: none` without a replacement. On peach fills the light deep-sky
ring holds 4.55:1 against the button — visible enough. In dark, `outline-offset:
2px` puts the ring on the surface *behind* the control, so the ratio that
matters is sky against night (12.58) or deep (11.18) — not against the peach
fill it surrounds (1.09, which is why the ring must never sit flush).

---

## 7. Motion

Short, and it never blocks reading. Identical in both schemes. These match the
game's transition timings so the site and the builds feel like one product.

| What | Duration | Easing |
| --- | --- | --- |
| Hover, focus, colour change | `160ms` | `ease-out` |
| Card lift, tab switch | `200ms` | `cubic-bezier(.2,.8,.3,1)` |
| Panel/menu open | `240ms` | `cubic-bezier(.2,.8,.3,1)` |
| Page fade | `300ms` | `ease` |

No parallax, no scroll-jacking, no autoplaying loops longer than 3s.

**The scheme toggle itself does not animate.** No cross-fade between palettes. A
300ms fade through the mid-tones looks like a bug and strobes anyone who toggles
twice.

Honour the user:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    transition-duration: .01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## 8. Imagery

- **Screenshots** sit in a framed surface: 12px radius, `1.5px` border, 8px
  padding — like a photo in an album. Light: cream frame,
  `--dcs-slate-200` border. Dark: `--dcs-deep-100` frame, `--dcs-night-700`
  border. Same album-photo idea, darker album.
- **Pixel art and sprites** must never be smoothed:
  `image-rendering: pixelated` on any upscaled sprite, and only integer scales
  (2×, 3×, 4×). Light sprites on a dark ground will look slightly haloed — that
  is the display, not a defect. Do not add a glow, an outline, or a drop shadow
  to compensate.
- **Never dim gameplay media.** No `filter: brightness()` or opacity on
  screenshots, GIFs or sprites to "make them fit" the dark scheme. A bright game
  is bright; the frame is what integrates it, not a filter that misrepresents
  what the thing actually looks like.
- **GIFs** of gameplay: keep under 3MB, loop, and give them the same frame.
  Prefer a poster + click-to-play video over an autoplaying GIF.
- **Illustration** follows §4: palette stroke, flat fill from the palette.
- **Logos and icons shipped as flat PNGs** need a dark variant or an SVG with
  `currentColor`. The theme's habit of `filter: invert(100%)` on footer images
  produces the wrong hue for anything that isn't monochrome — replace those
  rules rather than inheriting them (§10).
- Every image needs `alt`. A screenshot's alt describes *what is happening in
  the game*, not "screenshot".

---

## 9. Voice

Short sentences. First person singular — this is one person's site.
Enthusiastic about the games, unembarrassed about the jank. Say what a project
actually is ("a broken little Pico-8 racer I made in a weekend"), not what it
aspires to be. Lowercase is fine in labels; avoid exclamation marks stacking up.
No marketing verbs — nothing "leverages", "empowers" or "delivers".

Project statuses, used consistently: **concept**, **prototype**, **playable**,
**released**, **abandoned**. Abandoned is a legitimate, interesting status —
say it plainly.

---

## 10. Wiring it into the theme

> **Where this lives today.** The site is hand-written static HTML, and the
> palette below is already declared as custom properties in
> [`assets/css/tokens.css`](../assets/css/tokens.css) — that file is the source of
> truth, and §10.4 is the shape of it. The SCSS in §10.1–10.3 is the mapping to
> apply *if* the site moves onto the Jekyll theme; it is not in the repo yet.

The palette lives in one place, not in ad-hoc CSS. `data-color-scheme="dark"`
is set **on `<body>`** (by [`assets/js/color-scheme.js`](../assets/js/color-scheme.js),
plus a copy of the read inlined in each page so the attribute lands before first
paint), with precedence stored setting → site default → `prefers-color-scheme`.
Light is the no-attribute state.

### 10.1 Light scheme

**`assets/_scss/colors/light-colors.scss`** — replace the scheme definitions at
the top of the file:

```scss
// light color scheme definitions — DeskCanSaw, sampled from sample.png
$brand-color-light:           #205e6f;  // deep-sky
$main-background-light:       #afdde9;  // sky
$button-color-light:          #495663;  // slate
$menu-background-light:       #f9f9f9;  // paper
$header-color-light:          #21272d;  // ink
$container-background-light:  #f4eed7;  // cream
$hr-color-light:              #ccd0d3;  // slate-200
$anchor-text-color-light:     #205e6f;  // deep-sky
```

Then in `%body-main-styles-colors-light`, set
`--body-anchor-hover-text-color: #21272d;` and `--body-text-color: #333c45;`.

### 10.2 Dark scheme

**`assets/_scss/colors/dark-colors.scss`** — the scheme definitions at the top:

```scss
// dark color scheme definitions — DeskCanSaw night
$brand-color-dark:            #afdde9;  // sky, promoted to accent
$main-background-dark:        #0e1519;  // night
$button-color-dark:           #9aabb3;  // slate-400
$menu-background-dark:        #172a33;  // deep
$header-color-dark:           #f4eed7;  // cream, promoted to headings
$container-background-dark:   #172a33;  // deep
$hr-color-dark:               #2f4753;  // night-700
$anchor-text-color-dark:      #afdde9;  // sky
```

Then in `%body-main-styles-colors-dark`:

```scss
--body-anchor-hover-text-color: #e9f5f9;  // sky-100
--body-text-color: #cbd8de;               // mist
```

### 10.3 Kill the theme's glows

Stock `dark-colors.scss` ships white blur shadows that violate §4. Zero every
one of them:

| Placeholder | Variable | Stock value | Set to |
| --- | --- | --- | --- |
| `%default-colors-dark` | `--multipurpose-container-shadow` | `0 0px 5px #ffffff33` | `none` |
| `%thumbnails-colors-dark` | `--thumbnail-shadow` | `0 0px 5px #ffffff42` | `none` |
| `%thumbnails-colors-dark` | `--thumbnail-hover-shadow` | `0 7px 30px -8px #fefdfc4d` | `none` |
| `%sliding-msg-box-colors-dark` | `--sliding-msg-box-header-shadow-color` | `#fefdfc4d` | `transparent` |
| `%scroll-to-top-colors-dark` | `--scroll-to-top-shadow-color` | `#a5a5a585` | `transparent` |
| `%searchresult-colors-dark` | `--searchresult-shadow-color` | `#ffffff30` | `transparent` |
| `%consent-bar-colors-dark` | `--consent-bar-shadow-color` | `#ffffff55` | `transparent` |
| `%button-colors-dark` | `--button-shadow-color` | `#888b8b55` | `transparent` |
| `%button-colors-dark` | `--button-active-shadow-color` | `#ffffff20` | `transparent` |
| `%slide-switch-colors-dark` | `--slide-switch-slider-shadow-color` | `#888b8b55` | `transparent` |
| `%table-of-contents-colors-dark` | `--table-of-contents-shadow-color` | `#888b8b55` | `transparent` |
| `%home-heading-colors-dark` | `--home-heading-shadow-color` | `#888b8b55` | `transparent` |

`--searchbox-focus-shadow-color: #e8a78ea0` is the exception worth keeping —
it is already peach-adjacent. Set it to `#e9c6af` and let it be the search
field's focus affordance.

### 10.4 Raw tokens and semantic aliases

The tokens are declared once, in the `:root` block of
[`assets/css/tokens.css`](../assets/css/tokens.css), and the semantic aliases are
re-pointed under the dark attribute. That file also carries the type, spacing,
shape and motion tokens (§3.1, §4, §5, §7); the excerpt below is the colour half
of it:

```css
:root {
  /* light side */
  --dcs-sky:        #afdde9;
  --dcs-sky-100:    #e9f5f9;
  --dcs-sky-200:    #d3ecf3;
  --dcs-sky-600:    #7a9ba3;
  --dcs-deep-sky:   #205e6f;
  --dcs-cream:      #f4eed7;
  --dcs-paper:      #f9f9f9;
  --dcs-ice:        #ecf0f1;
  --dcs-peach:      #e9c6af;
  --dcs-peach-100:  #f9efe9;
  --dcs-peach-600:  #a38b7a;
  --dcs-rust:       #7e4f30;
  --dcs-slate:      #495663;
  --dcs-slate-400:  #9ba2a9;
  --dcs-slate-200:  #ccd0d3;
  --dcs-ink:        #21272d;
  --dcs-ink-700:    #333c45;

  /* night side */
  --dcs-night:      #0e1519;
  --dcs-deep:       #172a33;
  --dcs-deep-100:   #233d48;
  --dcs-night-700:  #2f4753;
  --dcs-mist:       #cbd8de;
  --dcs-slate-500:  #768f9a;
  --dcs-sky-dim:    #25454f;
  --dcs-peach-dim:  #46372f;
  --dcs-peach-tint: #f0d7c7;

  /* semantic aliases — light values */
  --dcs-bg: var(--dcs-sky);
  --dcs-surface: var(--dcs-cream);
  --dcs-surface-raised: var(--dcs-paper);
  --dcs-text: var(--dcs-ink-700);
  --dcs-heading: var(--dcs-ink);
  --dcs-muted: var(--dcs-slate);
  --dcs-border: var(--dcs-sky-600);
  --dcs-border-strong: var(--dcs-slate);
  --dcs-link: var(--dcs-deep-sky);
  --dcs-link-hover: var(--dcs-ink);
  --dcs-warm-text: var(--dcs-rust);
  --dcs-stroke: var(--dcs-slate);
}

body[data-color-scheme="dark"] {
  --dcs-slate-400: #9aabb3;

  --dcs-bg: var(--dcs-night);
  --dcs-surface: var(--dcs-deep);
  --dcs-surface-raised: var(--dcs-deep-100);
  --dcs-text: var(--dcs-mist);
  --dcs-heading: var(--dcs-cream);
  --dcs-muted: var(--dcs-slate-400);
  --dcs-border: var(--dcs-night-700);
  --dcs-border-strong: var(--dcs-slate-500);
  --dcs-link: var(--dcs-sky);
  --dcs-link-hover: var(--dcs-sky-100);
  --dcs-warm-text: var(--dcs-peach);
  --dcs-stroke: var(--dcs-slate-400);
}
```

Component CSS then uses the **aliases** (`var(--dcs-surface)`), never the raw
scheme-side tokens. Raw tokens are only for values identical in both schemes —
illustration fills, the peach accent. Inside the theme's own SCSS, reach for the
theme's `get_scheme()` mixin instead; the aliases are for the component CSS the
site adds on top, which the mixin doesn't reach.

---

## 11. Checklist

Before shipping a page:

- [ ] Roughly 75% of the viewport is the ground colour; there is exactly **one**
      peach element — and the active nav item counts.
- [ ] All body text comes from that scheme's text scale — never peach on cream,
      never slate, rust or deep-sky on night.
- [ ] Nothing has a blurred shadow; in dark, nothing has a shadow at all,
      including the theme's stock white glows.
- [ ] In dark: no text is pure white, no ground is pure black.
- [ ] Every border that carries meaning (inputs, active state, selection) is
      `--dcs-slate` / `--dcs-slate-500` or a surface-value change — never
      `--dcs-night-700` alone.
- [ ] Every interactive element has a visible `:focus-visible` ring with
      `outline-offset: 2px`.
- [ ] Pixel type is ≥16px, whole-pixel sized, and never a paragraph. No
      `font-weight: 300` in dark; Silkscreen is `400` below 32px there.
- [ ] Sprites are integer-scaled, `image-rendering: pixelated`, and undimmed.
- [ ] The page works in both schemes — toggle it and read it. The peach primary
      button should not move, resize or change colour, and the toggle itself
      does not animate.
- [ ] `prefers-reduced-motion` is honoured.
- [ ] Every image has meaningful `alt` text.
