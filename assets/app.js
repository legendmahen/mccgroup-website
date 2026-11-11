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
