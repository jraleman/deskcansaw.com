const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = readFileSync(path.join(__dirname, '..', 'assets', 'js', 'game-filters.js'), 'utf8');

function element() {
  const listeners = {};
  return {
    value: '', hidden: true, textContent: '',
    addEventListener(type, listener) {
      (listeners[type] ||= []).push(listener);
    },
    emit(type) {
      for (const listener of listeners[type] || []) listener({ preventDefault() {} });
    }
  };
}

function catalog(games) {
  const fields = {};
  for (const id of ['game-filters', 'game-query', 'game-genre', 'game-mode',
                    'game-results', 'game-empty', 'game-grid']) {
    fields[id] = element();
  }
  const cards = games.map(game => ({
    name: game.name, hidden: false,
    getAttribute(name) {
      if (name === 'data-genres') return JSON.stringify(game.genres || []);
      if (name === 'data-modes') return (game.modes || []).join(' ');
      throw new Error('Unexpected attribute: ' + name);
    },
    querySelector(selector) {
      if (selector === 'h3') return { textContent: game.name };
      if (selector === '[id$="-description"]') {
        return game.description ? { textContent: game.description } : null;
      }
      throw new Error('Unexpected selector: ' + selector);
    }
  }));
  fields['game-grid'].querySelectorAll = () => cards;
  const window = element();
  const frames = [];
  vm.runInNewContext(source, {
    document: { getElementById: id => fields[id] },
    window,
    requestAnimationFrame: callback => frames.push(callback)
  });
  return {
    fields,
    visible: () => cards.filter(card => !card.hidden).map(card => card.name),
    filter(values) {
      for (const [name, value] of Object.entries(values)) {
        fields['game-' + name].value = value;
        fields['game-' + name].emit(name === 'query' ? 'input' : 'change');
      }
    },
    reset() {
      fields['game-filters'].emit('reset');
      for (const name of ['query', 'genre', 'mode']) fields['game-' + name].value = '';
      while (frames.length) frames.shift()();
    },
    restore: () => window.emit('pageshow')
  };
}

test('genre, play mode and case-insensitive search words intersect', () => {
  const page = catalog([
    { name: 'Robot Solo', genres: ['Action', 'Rhythm'], modes: ['solo'] },
    { name: 'Robot Duet', genres: ['Rhythm'], modes: ['solo', 'local'] },
    { name: 'Star Link', description: 'Robots in space', genres: ['Puzzle'], modes: ['online'] }
  ]);
  page.filter({ query: '  ROBOT   rhythm  ', genre: 'Rhythm', mode: 'multiplayer' });
  assert.deepEqual(page.visible(), ['Robot Duet']);
  assert.equal(page.fields['game-results'].textContent, '1 of 3 games');
  page.filter({ genre: 'Puzzle' });
  assert.deepEqual(page.visible(), []);
  assert.equal(page.fields['game-empty'].hidden, false);
  assert.equal(page.fields['game-results'].textContent, '0 of 3 games');
  page.filter({ query: 'SPACE', mode: 'online' });
  assert.deepEqual(page.visible(), ['Star Link']);
  assert.equal(page.fields['game-empty'].hidden, true);
});

test('online is not browser availability, and reset restores unclassified games', () => {
  const page = catalog([
    { name: 'Solo', modes: ['solo'] },
    { name: 'Local', modes: ['solo', 'local'] },
    { name: 'Online', modes: ['online'] },
    { name: 'Unclassified' }
  ]);
  page.filter({ mode: 'multiplayer' });
  assert.deepEqual(page.visible(), ['Local', 'Online']);
  page.filter({ mode: 'online' });
  assert.deepEqual(page.visible(), ['Online']);
  page.filter({ mode: 'solo' });
  assert.deepEqual(page.visible(), ['Solo', 'Local']);
  page.reset();
  assert.deepEqual(page.visible(), ['Solo', 'Local', 'Online', 'Unclassified']);
  assert.equal(page.fields['game-results'].textContent, '4 games');
  assert.equal(page.fields['game-filters'].hidden, false);
  page.filter({ query: 'unclassified' });
  assert.deepEqual(page.visible(), ['Unclassified']);
  page.fields['game-query'].value = '';
  page.fields['game-mode'].value = 'online';
  page.restore();
  assert.deepEqual(page.visible(), ['Online']);
});

test('new genres and games beyond nine work without changing the script', () => {
  const games = Array.from({ length: 12 }, (_, i) => ({
    name: 'Arcade ' + i, genres: ['Arcade'], modes: ['solo']
  }));
  const genre = 'Puzzle & "co-op"';
  games.push({ name: 'Future Game', genres: [genre], modes: ['online'] });
  const page = catalog(games);
  assert.equal(page.visible().length, 13);
  page.filter({ genre, mode: 'online' });
  assert.deepEqual(page.visible(), ['Future Game']);
  page.reset();
  assert.equal(page.visible().length, 13);
});
