# The site's content

`site.json` is the source of truth for the parts of the site that would
otherwise be written twice — the Gamer Profile body, the kinds and rules
under Files, and the videos and live streams under Videos.
`tools/build.py` renders it into the `<!-- generated:… -->` blocks of
`index.html`.

The games are not in here. `dcs_games` is the list of games, and
[`../tools/catalog.py`](../tools/catalog.py) reads it straight out of that
Godot project, so the site never keeps a second copy to fall out of date.
`tools/build.py` lists them under `/#games`, and `tools/export_games.py`
exports a page for each one plus `/play/`, which is all of them at once.

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
