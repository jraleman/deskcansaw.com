import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build


class GameCardTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        root_patch = patch.object(build, 'ROOT', self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        self.image = self.root / 'assets' / 'img' / 'games' / 'one.webp'
        self.image.parent.mkdir(parents=True)
        self.image.touch()

    def content(self):
        return {
            'games': [{'id': 'one', 'slug': 'one', 'name': 'One < two'}],
            'game_cards': {
                'one': {
                    'description': 'Tap <then> move & repeat.',
                    'alt': 'A "small" toy & a target.',
                },
            },
        }

    def test_artwork_and_copy_are_escaped_inside_one_named_link(self):
        content = self.content()
        build.check_game_cards(content)
        rendered = build.render_games(content, '')

        self.assertIn('href="/play/one/" aria-labelledby="game-one"', rendered)
        self.assertIn('<h3 id="game-one">One &lt; two</h3>', rendered)
        self.assertIn('<p>Tap &lt;then&gt; move &amp; repeat.</p>', rendered)
        self.assertIn('alt="A &quot;small&quot; toy &amp; a target."', rendered)
        self.assertIn('src="/assets/img/games/one.webp"', rendered)
        self.assertIn('width="640" height="360" loading="lazy"', rendered)
        self.assertEqual(rendered.count('<a '), 1)

    def test_catalog_order_and_new_games_do_not_depend_on_card_metadata(self):
        content = self.content()
        content['games'].insert(0, {'id': 'new', 'slug': 'new', 'name': 'New game'})
        content['game_cards']['retired'] = {
            'description': 'No longer in the catalog.',
            'alt': 'An old game.',
        }

        with patch.object(build.catalog, 'warn') as warn:
            build.check_game_cards(content)
        rendered = build.render_games(content, '')

        warn.assert_called_once()
        self.assertIn('game_cards.new', warn.call_args.args[0])
        self.assertLess(rendered.index('/play/new/'), rendered.index('/play/one/'))
        self.assertNotIn('/play/retired/', rendered)
        self.assertEqual(rendered.count('<img '), 1)

    def test_incomplete_card_copy_reports_its_content_key(self):
        for field in ('description', 'alt'):
            for value in (None, '', 42):
                with self.subTest(field=field, value=value):
                    content = self.content()
                    content['game_cards']['one'][field] = value
                    with self.assertRaisesRegex(SystemExit, r'game_cards\.one\.' + field):
                        build.check_game_cards(content)

        for cards in ([], {'one': 'not an object'}):
            with self.subTest(cards=cards):
                content = self.content()
                content['game_cards'] = cards
                with self.assertRaisesRegex(SystemExit, 'game_cards'):
                    build.check_game_cards(content)

    def test_missing_artwork_fails_before_rendering_a_broken_image(self):
        self.image.unlink()
        with self.assertRaisesRegex(
                SystemExit, r'game_cards\.one: artwork is missing: assets/img/games/one\.webp'):
            build.check_game_cards(self.content())

    def test_rebuild_updates_game_cards_without_changing_surrounding_copy(self):
        content = self.content()
        build.check_game_cards(content)
        page = self.root / 'index.html'
        before, after = '<p>Hand-written intro.</p>\n', '\n<p>Hand-written footer.</p>'
        page.write_text(before + '  <!-- generated:games -->old cards'
                        '<!-- /generated:games -->' + after, encoding='utf-8')

        rendered, original = build.build(page, content)
        self.assertNotEqual(rendered, original)
        self.assertTrue(rendered.startswith(before))
        self.assertTrue(rendered.endswith(after))
        self.assertIn('class="game-card-art"', rendered)
        page.write_text(rendered, encoding='utf-8')
        self.assertEqual(build.build(page, content)[0], rendered)


if __name__ == '__main__':
    unittest.main()
