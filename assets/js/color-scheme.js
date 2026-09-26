/* ==========================================================================
   DeskCanSaw — colour scheme toggle (style-guide.md §7, §10)
   data-color-scheme="dark" on <body>; light is the no-attribute state.
   Precedence: stored setting -> prefers-color-scheme.

   Every page also carries a four-line copy of the read in <body> so the
   attribute is set before first paint and dark users never see a light
   flash. This file owns everything after that.
   ========================================================================== */
(function () {
  var KEY = 'dcs-color-scheme';
  var body = document.body;
  var btn = document.getElementById('scheme-toggle');
  var label = document.getElementById('scheme-label');

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function store(scheme) {
    try { localStorage.setItem(KEY, scheme); } catch (e) {}
  }
  function preferred() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function current() {
    return body.getAttribute('data-color-scheme') === 'dark' ? 'dark' : 'light';
  }

  function apply(scheme) {
    /* The toggle itself never animates (§7): suppress transitions for the
       one frame the swap takes, then hand them back. */
    body.classList.add('theme-switching');
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { body.classList.remove('theme-switching'); });
    });

    if (scheme === 'dark') { body.setAttribute('data-color-scheme', 'dark'); }
    else { body.removeAttribute('data-color-scheme'); }

    if (btn) { btn.setAttribute('aria-pressed', scheme === 'dark' ? 'true' : 'false'); }
    if (label) { label.textContent = scheme === 'dark' ? 'Day' : 'Night'; }
  }

  apply(stored() || preferred());

  if (btn) {
    btn.addEventListener('click', function () {
      var next = current() === 'dark' ? 'light' : 'dark';
      apply(next);
      store(next);
    });
  }
})();
