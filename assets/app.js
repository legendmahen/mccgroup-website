(function () {
  var d = document, h = d.documentElement;
  h.classList.remove('no-js');

  // Mobile menu
  var t = d.querySelector('.nav-toggle'), n = d.getElementById('site-nav');
  if (t && n) {
    t.addEventListener('click', function () {
      var o = n.classList.toggle('open');
      t.setAttribute('aria-expanded', o ? 'true' : 'false');
    });
    d.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && n.classList.contains('open')) { n.classList.remove('open'); t.setAttribute('aria-expanded', 'false'); t.focus(); }
    });
  }


  // Hero carousel
  var hs = d.querySelector('.hero-slider');
  if (hs) {
    var sl = hs.querySelectorAll('.slide'), dt = hs.querySelectorAll('.dots button'), cur = 0, tm = null;
    var rm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var go = function (i) {
      cur = (i + sl.length) % sl.length;
      for (var k = 0; k < sl.length; k++) {
        sl[k].classList.toggle('is-active', k === cur);
        sl[k].setAttribute('aria-hidden', k === cur ? 'false' : 'true');
        if (k === cur) dt[k].setAttribute('aria-current', 'true'); else dt[k].removeAttribute('aria-current');
      }
    };
    var play = function () { stop(); if (!rm) tm = setInterval(function () { go(cur + 1); }, 6500); };
    var stop = function () { if (tm) { clearInterval(tm); tm = null; } };
    hs.querySelector('[data-slide-prev]').addEventListener('click', function () { go(cur - 1); play(); });
    hs.querySelector('[data-slide-next]').addEventListener('click', function () { go(cur + 1); play(); });
    for (var j = 0; j < dt.length; j++) (function (n) { dt[n].addEventListener('click', function () { go(n); play(); }); })(j);
    hs.addEventListener('mouseenter', stop); hs.addEventListener('mouseleave', play);
    hs.addEventListener('focusin', stop); hs.addEventListener('focusout', play);
    go(0); play();
  }

  // Lightbox
  var dlg = d.getElementById('lightbox');
  var shots = Array.prototype.slice.call(d.querySelectorAll('[data-full]'));
  if (dlg && shots.length && dlg.showModal) {
    var img = dlg.querySelector('img'), cap = dlg.querySelector('p'), idx = 0, last = null;
    function show(i) {
      idx = (i + shots.length) % shots.length;
      var b = shots[idx];
      img.src = b.getAttribute('data-full');
      img.alt = b.getAttribute('data-alt') || '';
      cap.textContent = b.getAttribute('data-alt') || '';
    }
    shots.forEach(function (b, i) {
      b.addEventListener('click', function () { last = b; show(i); dlg.showModal(); });
    });
    dlg.querySelector('[data-prev]').addEventListener('click', function () { show(idx - 1); });
    dlg.querySelector('[data-next]').addEventListener('click', function () { show(idx + 1); });
    dlg.querySelector('[data-close]').addEventListener('click', function () { dlg.close(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    dlg.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') show(idx - 1);
      if (e.key === 'ArrowRight') show(idx + 1);
    });
    dlg.addEventListener('close', function () { if (last) last.focus(); });
  }

  // Enquiry error message (PHP handler redirects back with ?error=1)
  if (/[?&]error=1/.test(location.search)) {
    var a = d.querySelector('.alert');
    if (a) { a.classList.add('show'); a.setAttribute('role', 'alert'); }
  }
})();
