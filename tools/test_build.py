import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

import build


class Tags(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.elements = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class ProfileTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        root_patch = patch.object(build, 'ROOT', self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        image = self.root / 'assets' / 'img' / 'profile' / 'sample.svg'
        image.parent.mkdir(parents=True)
        image.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="4" height="3"/>',
                         encoding='utf-8')

    def image(self):
        return {
            'src': '/assets/img/profile/sample.svg', 'alt': 'An "image" & <detail>.',
            'width': 4, 'height': 3,
            'credit': {
                'title': 'An <illustration>', 'author': 'Artist & illustrator',
                'source': 'https://example.test/source?a=1&b=2',
                'license': 'CC BY 3.0',
                'license_url': 'https://creativecommons.org/licenses/by/3.0/',
                'changes': 'Resized & recolored.',
            },
        }

    def content(self):
        return {
            'profile': [
                {'type': 'intro', 'lead': ' Glitch <hunter> & runner. ',
                 'text': 'I play **my way**.'},
                {'type': 'favorites', 'text': 'The replay & discovery loop.',
                 'items': [
                     {'name': 'One < two', 'platform': 'Port & "Build"',
                      'note': 'A `shortcut` worth replaying.'},
                     {'name': 'Second game', 'platform': 'Mobile'},
                 ]},
                {'type': 'setup', 'text': 'Emulation & hardware.',
                 'items': [
                     {'name': 'Handheld <one>', 'note': 'Physical buttons & portable play.'},
                 ]},
            ],
        }

    def test_profile_panels_escape_copy_and_keep_content_order(self):
        content = self.content()
        content['profile'].append({'type': 'paragraph', 'text': 'Extra **notes**.'})
        build.check_profile(content)
        rendered = build.render_profile(content, '')

        self.assertIn('>Glitch &lt;hunter&gt; &amp; runner.</p>', rendered)
        self.assertIn('<strong>my way</strong>', rendered)
        self.assertIn('<h4>One &lt; two</h4>', rendered)
        self.assertIn('>Port &amp; &quot;Build&quot;</span>', rendered)
        self.assertIn('A <code>shortcut</code> worth replaying.', rendered)
        self.assertIn('<h4>Handheld &lt;one&gt;</h4>', rendered)
        self.assertIn('Physical buttons &amp; portable play.', rendered)
        self.assertLess(rendered.index('One &lt; two'), rendered.index('Second game'))
        self.assertLess(rendered.index('Second game'), rendered.index('What I play on'))
        self.assertTrue(rendered.endswith('<p>Extra <strong>notes</strong>.</p>'))
        self.assertEqual([attrs.get('role') for tag, attrs in Tags(rendered).elements
                          if tag == 'ul'], ['list', 'list'])

    def test_unsupplied_notes_and_hardware_are_not_rendered(self):
        content = self.content()
        content['profile'].pop()
        del content['profile'][1]['items'][0]['note']
        build.check_profile(content)
        rendered = build.render_profile(content, '')

        self.assertIn('The replay &amp; discovery loop.', rendered)
        self.assertIn('<h4>Second game</h4>', rendered)
        self.assertNotIn('profile-note', rendered)
        self.assertNotIn('profile-setup', rendered)
        self.assertNotIn('What I play on', rendered)
        self.assertNotIn('<img ', rendered)
        self.assertNotIn('profile-image-credits', rendered)

    def test_images_are_sized_escaped_and_credited_once(self):
        content = self.content()
        content['profile'][0]['image'] = self.image()
        content['profile'][1]['items'][0]['image'] = self.image()
        content['profile'][1]['items'][0]['image']['alt'] = ''
        content['profile'][2]['items'][0]['image'] = self.image()
        build.check_profile(content)
        rendered = build.render_profile(content, '')
        tags = Tags(rendered).elements
        images = [attrs for tag, attrs in tags if tag == 'img']

        self.assertEqual(len(images), 3)
        self.assertEqual(images[0]['alt'], self.image()['alt'])
        self.assertEqual(images[1]['alt'], '')
        for image in images:
            self.assertEqual((image['width'], image['height']), ('4', '3'))
            self.assertEqual(image['src'], self.image()['src'])
            self.assertEqual(image['loading'], 'lazy')
            self.assertEqual(image['decoding'], 'async')
        source_links = [attrs for tag, attrs in tags if tag == 'a'
                        and attrs.get('href') == self.image()['credit']['source']]
        self.assertEqual(len(source_links), 1)
        self.assertIn('An &lt;illustration&gt;', rendered)
        self.assertIn('Artist &amp; illustrator', rendered)
        self.assertIn('Resized &amp; recolored.', rendered)
        self.assertNotIn('open', next(attrs for tag, attrs in tags if tag == 'details'))

    def test_invalid_image_paths_dimensions_and_alt_report_the_content_key(self):
        cases = {
            'src': ['https://example.test/image.svg', '/assets/img/../../content/site.json',
                    '/assets/img/profile/missing.svg', '/assets/img/profile/sample.svg?q=1'],
            'width': [None, 0, -1, True, 1.5, '4'],
            'height': [None, 0, -1, False, 1.5, '3'],
            'alt': [None, 42],
        }
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    content = self.content()
                    content['profile'][0]['image'] = self.image()
                    content['profile'][0]['image'][field] = value
                    with self.assertRaisesRegex(
                            SystemExit, r'profile\[0\]\.image\.' + field):
                        build.check_profile(content)
        content = self.content()
        content['profile'][1]['items'][0]['image'] = None
        with self.assertRaisesRegex(SystemExit, r'profile\[1\]\.items\[0\]\.image'):
            build.check_profile(content)

    def test_incomplete_or_unsafe_image_credits_fail_before_rendering(self):
        for field in ('title', 'author', 'source', 'license', 'license_url', 'changes'):
            with self.subTest(field=field):
                content = self.content()
                content['profile'][0]['image'] = self.image()
                content['profile'][0]['image']['credit'][field] = ''
                with self.assertRaisesRegex(
                        SystemExit, r'profile\[0\]\.image\.credit\.' + field):
                    build.check_profile(content)
        for field in ('source', 'license_url'):
            for value in ('javascript:alert(1)', '/relative', 'https://', 'https://bad host/',
                          'https://[invalid'):
                with self.subTest(field=field, value=value):
                    content = self.content()
                    content['profile'][0]['image'] = self.image()
                    content['profile'][0]['image']['credit'][field] = value
                    with self.assertRaisesRegex(
                            SystemExit, r'profile\[0\]\.image\.credit\.' + field):
                        build.check_profile(content)

    def test_incomplete_profile_panels_report_the_content_key(self):
        for index, field in ((0, 'lead'), (0, 'text'), (1, 'text'), (2, 'text')):
            for value in (None, '', 42):
                with self.subTest(block=index, field=field, value=value):
                    content = self.content()
                    content['profile'][index][field] = value
                    with self.assertRaisesRegex(
                            SystemExit, r'profile\[{0}\]\.{1}'.format(index, field)):
                        build.check_profile(content)

        for index in (1, 2):
            for value in (None, [], ['not an object']):
                with self.subTest(block=index, items=value):
                    content = self.content()
                    content['profile'][index]['items'] = value
                    with self.assertRaisesRegex(SystemExit, r'profile\[{}\]\.items'.format(index)):
                        build.check_profile(content)

            fields = ('name', 'platform', 'note') if index == 1 else ('name', 'note')
            for field in fields:
                for value in (None, '', 42):
                    with self.subTest(block=index, field=field, value=value):
                        content = self.content()
                        content['profile'][index]['items'][0][field] = value
                        with self.assertRaisesRegex(
                                SystemExit, r'profile\[{0}\]\.items\[0\]\.{1}'.format(index, field)):
                            build.check_profile(content)

    def test_rebuild_updates_profile_without_changing_neighboring_sections(self):
        content = self.content()
        content['profile'][1]['items'][0]['image'] = self.image()
        build.check_profile(content)
        before = '<section id="games">Keep the games.</section>\n<section id="profile">\n'
        after = '\n</section>\n<section id="files">Keep the files.</section>'
        with tempfile.TemporaryDirectory() as temporary:
            page = Path(temporary) / 'index.html'
            page.write_text(before + '  <!-- generated:profile -->old profile'
                            '<!-- /generated:profile -->' + after, encoding='utf-8')

            rendered, original = build.build(page, content)
            self.assertNotEqual(rendered, original)
            self.assertTrue(rendered.startswith(before))
            self.assertTrue(rendered.endswith(after))
            self.assertIn('class="card profile-intro"', rendered)
            self.assertIn('<h4>One &lt; two</h4>', rendered)
            self.assertIn('src="/assets/img/profile/sample.svg"', rendered)
            self.assertIn('<summary>Image credits</summary>', rendered)
            page.write_text(rendered, encoding='utf-8')
            self.assertEqual(build.build(page, content)[0], rendered)


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
                    'genres': ['Arcade'],
                    'modes': ['solo', 'local'],
                },
            },
        }

    def test_launch_button_is_the_only_link_and_card_copy_is_escaped(self):
        content = self.content()
        content['games'][0]['name'] = 'One < two & "three"'
        build.check_game_cards(content)
        rendered = build.render_games(content, '')
        elements = Tags(rendered).elements
        cards = [attrs for tag, attrs in elements if tag == 'article']
        links = [attrs for tag, attrs in elements if tag == 'a']
        icon = next(attrs for tag, attrs in elements if tag == 'svg')

        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]['aria-labelledby'], 'game-one')
        self.assertNotIn('href', cards[0])
        self.assertNotIn('tabindex', cards[0])
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['href'], '/play/one/')
        self.assertEqual(links[0]['aria-label'], 'Launch game: One < two & "three"')
        self.assertEqual(links[0]['aria-describedby'], 'game-one-description')
        self.assertIn('game-card-launch', links[0]['class'].split())
        self.assertEqual(icon['aria-hidden'], 'true')
        self.assertEqual(icon['focusable'], 'false')
        self.assertIn('<h3 id="game-one">One &lt; two &amp; &quot;three&quot;</h3>', rendered)
        self.assertIn('<p id="game-one-description">Tap &lt;then&gt; move &amp; repeat.</p>', rendered)
        self.assertIn('alt="A &quot;small&quot; toy &amp; a target."', rendered)
        self.assertIn('src="/assets/img/games/one.webp"', rendered)
        self.assertIn('width="640" height="640" loading="lazy"', rendered)
        self.assertLess(rendered.index('<img '), rendered.index('<a '))
        self.assertLess(rendered.index('</h3>'), rendered.index('<a '))
        self.assertIn('<span>Launch game</span>', rendered)

    def test_catalog_order_and_new_games_do_not_depend_on_card_metadata(self):
        content = self.content()
        content['games'].insert(0, {'id': 'new', 'slug': 'new', 'name': 'New game'})
        content['game_cards']['retired'] = {
            'description': 'No longer in the catalog.',
            'alt': 'An old game.',
            'genres': ['Retired genre'],
            'modes': ['online'],
        }

        with patch.object(build.catalog, 'warn') as warn:
            build.check_game_cards(content)
        rendered = build.render_games(content, '')

        warn.assert_called_once()
        self.assertIn('game_cards.new', warn.call_args.args[0])
        self.assertLess(rendered.index('/play/new/'), rendered.index('/play/one/'))
        self.assertNotIn('/play/retired/', rendered)
        self.assertEqual(rendered.count('<img '), 1)
        link = next(attrs for tag, attrs in Tags(rendered).elements
                    if tag == 'a' and attrs['href'] == '/play/new/')
        self.assertEqual(link['aria-label'], 'Launch game: New game')
        self.assertNotIn('aria-describedby', link)
        self.assertEqual(rendered.count('aria-describedby='), 1)
        self.assertNotIn('Retired genre', build.render_game_filters(content, ''))

    def test_filter_metadata_is_validated_before_rendering(self):
        for field in ('genres', 'modes'):
            for value in (None, '', [], [''], ['solo', 2], ['solo', 'SOLO']):
                with self.subTest(field=field, value=value):
                    content = self.content()
                    content['game_cards']['one'][field] = value
                    with self.assertRaisesRegex(SystemExit, r'game_cards\.one\.' + field):
                        build.check_game_cards(content)

        for mode in ('browser', 'multiplayer'):
            with self.subTest(mode=mode):
                content = self.content()
                content['game_cards']['one']['modes'] = [mode]
                with self.assertRaisesRegex(SystemExit, r'game_cards\.one\.modes: unknown mode'):
                    build.check_game_cards(content)

    def test_new_genres_and_online_games_reach_filter_options_and_card_data(self):
        content = self.content()
        genre = 'Music & "rhythm" <test>'
        content['game_cards']['one']['genres'] = ['  ' + genre + '  ']
        content['game_cards']['one']['modes'] = ['online']
        build.check_game_cards(content)

        card = next(attrs for tag, attrs in Tags(build.render_games(content, '')).elements
                    if tag == 'article')
        controls = Tags(build.render_game_filters(content, '')).elements
        options = [attrs['value'] for tag, attrs in controls if tag == 'option']
        self.assertEqual(json.loads(card['data-genres']), [genre])
        self.assertEqual(card['data-modes'], 'online')
        self.assertEqual(options.count(genre), 1)
        self.assertIn('online', options)
        self.assertIn('multiplayer', options)
        form = next(attrs for tag, attrs in controls if tag == 'form')
        self.assertIn('hidden', form)

    def test_catalog_grows_beyond_nine_without_inventing_filter_metadata(self):
        content = self.content()
        for i in range(12):
            content['games'].append({'id': 'new{}'.format(i), 'slug': 'new{}'.format(i),
                                     'name': 'New game {}'.format(i)})
        with patch.object(build.catalog, 'warn') as warn:
            build.check_game_cards(content)
        elements = Tags(build.render_games(content, '')).elements
        cards = [attrs for tag, attrs in elements if tag == 'article']
        links = [attrs for tag, attrs in elements if tag == 'a']

        self.assertEqual(len(cards), 13)
        self.assertEqual(warn.call_count, 12)
        self.assertEqual(len(links), len(cards))
        self.assertEqual(links[-1]['href'], '/play/new11/')
        self.assertEqual(json.loads(cards[-1]['data-genres']), [])
        self.assertEqual(cards[-1]['data-modes'], '')
        self.assertIn('>13 games</p>', build.render_game_filters(content, ''))

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
        page.write_text(before + '  <!-- generated:game-filters -->old filters'
                        '<!-- /generated:game-filters -->\n'
                        '  <!-- generated:games -->old cards'
                        '<!-- /generated:games -->' + after, encoding='utf-8')

        rendered, original = build.build(page, content)
        self.assertNotEqual(rendered, original)
        self.assertTrue(rendered.startswith(before))
        self.assertTrue(rendered.endswith(after))
        self.assertIn('class="game-card-art"', rendered)
        self.assertIn('id="game-genre"', rendered)
        page.write_text(rendered, encoding='utf-8')
        self.assertEqual(build.build(page, content)[0], rendered)


class DownloadTests(unittest.TestCase):
    def test_download_links_have_decorative_icons_and_descriptive_names(self):
        elements = Tags(build.render_downloads({}, '')).elements
        links = [attrs for tag, attrs in elements if tag == 'a']
        icons = [attrs for tag, attrs in elements if tag == 'svg']
        desktops = build.catalog.desktops()

        self.assertEqual(len(links), len(desktops))
        self.assertEqual(len(icons), len(desktops))
        for desktop, link, icon in zip(desktops, links, icons):
            with self.subTest(desktop=desktop['slug']):
                self.assertEqual(link['href'], build.catalog.DOWNLOAD_PATH + desktop['file'])
                self.assertIn('download', link)
                self.assertEqual(link['aria-label'], 'Download collection for {} {}'.format(
                    desktop['label'], desktop['arch_label']))
                self.assertEqual(icon['aria-hidden'], 'true')
                self.assertEqual(icon['focusable'], 'false')
                self.assertNotIn('tabindex', icon)
                self.assertEqual(icon['stroke'], 'currentColor')

    def test_download_names_escape_platform_and_architecture_labels(self):
        desktops = (('windows', 'Windows & "portable"', 'x86_64', 'x86 <64>'),)
        with patch.object(build.catalog, 'DESKTOPS', desktops):
            rendered = build.render_downloads({}, '')
        link = next(attrs for tag, attrs in Tags(rendered).elements if tag == 'a')

        self.assertEqual(link['aria-label'], 'Download collection for Windows & "portable" x86 <64>')
        self.assertIn('Windows &amp; &quot;portable&quot; <span class="tag">x86 &lt;64&gt;</span>',
                      rendered)


if __name__ == '__main__':
    unittest.main()
