/* ==========================================================================
   DeskCanSaw — nav scroll-spy
   Marks the side-nav link for the section currently in view with
   aria-current="true"; layout.css styles that state. Progressive: without
   IntersectionObserver the nav is simply never marked.
   ========================================================================== */
(function () {
  if (!('IntersectionObserver' in window)) { return; }

  var links = {};
  var anchors = document.querySelectorAll('.navlist a[href^="#"]');
  if (!anchors.length) { return; }

  Array.prototype.forEach.call(anchors, function (a) {
    links[a.getAttribute('href').slice(1)] = a;
  });

  var sections = Array.prototype.filter.call(
    document.querySelectorAll('[id]'),
    function (el) { return Object.prototype.hasOwnProperty.call(links, el.id); }
  );
  if (!sections.length) { return; }

  var visible = {};

  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });

    /* Two sections can straddle the trigger band; the later one is the one
       being scrolled into. */
    var current = null;
    sections.forEach(function (s) { if (visible[s.id]) { current = s.id; } });

    Object.keys(links).forEach(function (id) {
      if (id === current) { links[id].setAttribute('aria-current', 'true'); }
      else { links[id].removeAttribute('aria-current'); }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });

  sections.forEach(function (s) { obs.observe(s); });
})();
