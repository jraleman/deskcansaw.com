/* Game filters read the generated cards; the catalog and genres have no size limit.
   Without JavaScript, the controls stay hidden and every game's launch link stays available. */
(function () {
  var form = document.getElementById('game-filters');
  if (!form) { return; }

  var query = document.getElementById('game-query');
  var genre = document.getElementById('game-genre');
  var mode = document.getElementById('game-mode');
  var results = document.getElementById('game-results');
  var empty = document.getElementById('game-empty');
  var grid = document.getElementById('game-grid');
  var games = Array.prototype.map.call(grid.querySelectorAll('.game-card'), function (card) {
    var genres = JSON.parse(card.getAttribute('data-genres'));
    var description = card.querySelector('[id$="-description"]');
    return {
      card: card,
      genres: genres,
      modes: card.getAttribute('data-modes').split(' ').filter(Boolean),
      text: [card.querySelector('h3').textContent, description ? description.textContent : '',
             genres.join(' ')].join(' ').toLowerCase()
    };
  });

  function update() {
    var words = query.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    var visible = 0;
    games.forEach(function (game) {
      var matchesGenre = !genre.value || game.genres.indexOf(genre.value) !== -1;
      var matchesMode = mode.value === 'multiplayer'
        ? game.modes.indexOf('local') !== -1 || game.modes.indexOf('online') !== -1
        : !mode.value || game.modes.indexOf(mode.value) !== -1;
      var matchesQuery = words.every(function (word) { return game.text.indexOf(word) !== -1; });
      var matches = matchesGenre && matchesMode && matchesQuery;
      game.card.hidden = !matches;
      if (matches) { visible += 1; }
    });
    var total = games.length + (games.length === 1 ? ' game' : ' games');
    var message = visible === games.length ? total : visible + ' of ' + total;
    if (results.textContent !== message) { results.textContent = message; }
    empty.hidden = visible > 0;
  }

  query.addEventListener('input', update);
  genre.addEventListener('change', update);
  mode.addEventListener('change', update);
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    update();
  });
  form.addEventListener('reset', function () {
    // Native form values reset after the event has been dispatched.
    requestAnimationFrame(update);
  });
  window.addEventListener('pageshow', update);
  update();
  form.hidden = false;
})();
