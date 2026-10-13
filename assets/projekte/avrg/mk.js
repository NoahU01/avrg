/* Medienkonzept AVRG: Kapitel, Landingpage-Varianten, Mails, Instagram-Raster mit Großansicht */
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------- Kapitel ---------- */
  var kopf = $('.site-header');
  function setzeOben() { document.documentElement.style.setProperty('--mk-top', (kopf ? kopf.offsetHeight : 84) + 'px'); }
  setzeOben(); window.addEventListener('resize', setzeOben);
  var tabs = $$('.mk-tab'), leiste = $('.mk-kapitel');
  var ALT = {grundidee: 'strategie', zielgruppe: 'strategie', claim: 'strategie', postings: 'social', offen: 'fahrplan'};
  function zeige(id, scrollen) {
    id = ALT[id] || id;
    if (!$('#k-' + id)) id = 'strategie';
    tabs.forEach(function (t) {
      var an = t.dataset.k === id;
      t.setAttribute('aria-selected', an ? 'true' : 'false');
      $('#k-' + t.dataset.k).hidden = !an;
      if (an) t.scrollIntoView({block: 'nearest', inline: 'center'});
    });
    if (scrollen) window.scrollTo({top: leiste.getBoundingClientRect().top + window.scrollY - (kopf ? kopf.offsetHeight : 0) + 1, behavior: 'smooth'});
  }
  tabs.forEach(function (t) {
    t.addEventListener('click', function () { history.replaceState(null, '', '#' + t.dataset.k); zeige(t.dataset.k, true); });
  });
  $$('[data-weiter]').forEach(function (b) {
    b.addEventListener('click', function () { history.replaceState(null, '', '#' + b.dataset.weiter); zeige(b.dataset.weiter, true); });
  });
  $$('.ak-sprung a').forEach(function (a) {
    a.addEventListener('click', function (e) { e.preventDefault(); var k = a.getAttribute('href').slice(1); history.replaceState(null, '', '#' + k); zeige(k, true); });
  });
  zeige(location.hash.slice(1), false);

  /* ---------- Landingpage-Varianten ---------- */
  $$('.mk-variante').forEach(function (b) {
    b.addEventListener('click', function () {
      var v = b.dataset.v;
      $$('.mk-variante').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      $('#mk-lp-bild').src = '/assets/projekte/avrg/lp-vorschau-voll-' + v + '.jpg?v=9';
      $('.ak-browser-seite').scrollTop = 0;
      $('#mk-lp-url').textContent = 'agentur-beispiel.de/neue-altersvorsorge' + (v === '1' ? '' : '-' + v);
      $$('.mk-bausteine').forEach(function (l) { l.hidden = l.dataset.v !== v; });
      $('#mk-lp-link').href = '/projekte/avrg-landingpage-' + v + '.html';
      $('#mk-lp-link').firstChild.textContent = 'Variante ' + v + ' öffnen ';
    });
  });

  /* ---------- Mails ---------- */
  var mtabs = $$('.ak-tab');
  mtabs.forEach(function (t) {
    t.addEventListener('click', function () {
      mtabs.forEach(function (x) {
        var an = x === t;
        x.setAttribute('aria-selected', an ? 'true' : 'false');
        document.getElementById(x.getAttribute('aria-controls')).hidden = !an;
      });
    });
  });

  /* ---------- Postings: fertige Einzelbilder 4:5 ohne Logo ---------- */
  var P = window.AVRG_POSTINGS || [], TH = window.AVRG_THEMEN || {};
  var FOTO = '/assets/projekte/avrg/fotos/';
  function nr(i) { return (i + 1 < 10 ? '0' : '') + (i + 1); }
  function flaeche(p, art) {
    return '<div class="cr cr--' + art + '">' + (p.d ? '<span class="cr__deko">' + p.d + '</span>' : '') +
      '<div class="cr__in"><p class="cr__label">' + p.l + '</p><p class="cr__h cr__mitte">' + p.h + '</p>' + (p.fuss ? '<p class="cr__fuss">' + p.fuss + '</p>' : '') + '</div></div>';
  }
  function creative(p) {
    switch (p.t) {
      case 'weiss': case 'rot': case 'schwarz': return flaeche(p, p.t);
      case 'blase':
        return '<div class="cr"><img class="cr__foto" src="' + FOTO + p.foto + '.jpg" alt="" loading="lazy"><p class="cr__blase">' + p.blase + '</p><span class="cr__tag">' + p.tag + '</span></div>';
      case 'band':
        return '<div class="cr cr--band"><img class="cr__foto" src="' + FOTO + p.foto + '.jpg" alt="" loading="lazy"><div class="cr__in"><p class="cr__h">' + p.h + '</p></div></div>';
      case 'fa':
        return '<div class="cr cr--fa"><div class="cr__frage"><p class="cr__fa-label">Frage</p><p class="cr__h">' + p.q + '</p></div><div class="cr__antwort"><p class="cr__fa-label">Antwort</p><p>' + p.a + '</p></div></div>';
      case 'durch':
        return '<div class="cr cr--durch"><div class="cr__in"><p class="cr__label" style="color:var(--r)">Was du bei uns nicht bekommst</p><div class="cr__mitte"><ul class="cr__weg">' + p.items.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul><p class="cr__h">' + p.h + '</p></div></div></div>';
      case 'check':
        return '<div class="cr cr--check"><div class="cr__in"><p class="cr__label" style="color:rgba(255,255,255,.75)">Neue Altersvorsorge 2027</p><div class="cr__mitte"><p class="cr__h">' + p.h + '</p><ul class="cr__haken">' + p.items.map(function (x) { return '<li><i></i>' + x + '</li>'; }).join('') + '</ul></div></div></div>';
      case 'split':
        return '<div class="cr cr--split"><div class="cr__teil cr__teil--o"><small>Ergebnis A</small><b>Mitnehmen.</b></div><div class="cr__teil cr__teil--u"><small>Ergebnis B</small><b>Abhaken<span>.</span></b></div><span class="cr__oder">oder</span></div>';
      case 'zahl':
        return '<div class="cr cr--zahl"><div class="cr__in"><p class="cr__label" style="color:var(--r)">Countdown</p><div class="cr__mitte"><p class="cr__zahl">' + p.z + '</p><p class="cr__h">' + p.h + '</p></div><p class="cr__fuss">' + p.fuss + '</p></div></div>';
      case 'zitat':
        return '<div class="cr cr--zitat"><div class="cr__in"><p class="cr__anf">“</p><p class="cr__h cr__mitte">' + p.h + '</p></div></div>';
      case 'suche':
        return '<div class="cr cr--suche"><div class="cr__in"><div class="cr__such"><div class="cr__feld"><span class="cr__lupe"></span><span>' + p.q + '<span class="cr__cursor"></span></span></div><ul class="cr__vorsch">' + p.vorschlaege.map(function (x) { return '<li><span>altersvorsorge <b>' + x.replace('… ', '') + '</b></span></li>'; }).join('') + '</ul></div><p class="cr__h">' + p.h + '</p></div></div>';
      case 'chat':
        return '<div class="cr cr--chat"><div class="cr__in"><p class="cr__label" style="color:var(--r)">Neue Altersvorsorge 2027</p><div class="cr__chat"><p class="cr__msg cr__msg--ich"><small>Du</small>' + p.ich + '</p><p class="cr__msg cr__msg--wir"><small>Wir</small>' + p.wir + '</p><span class="cr__tippt"><i></i><i></i><i></i></span></div></div></div>';
      case 'notiz':
        return '<div class="cr cr--notiz"><div class="cr__zettel"><b>' + p.titel + '</b><ul>' + p.items.map(function (x) { return '<li class="' + (x[1] ? 'ok' : 'offen') + '"><i></i><span>' + x[0] + '</span></li>'; }).join('') + '</ul></div><div class="cr__in"><p class="cr__h">' + p.h + '</p></div></div>';
      case 'ticket':
        return '<div class="cr cr--ticket"><div class="cr__in"><p class="cr__h">' + p.h + '</p></div><div class="cr__tk"><div class="cr__tk-haupt"><small>Neue Altersvorsorge 2027</small><b>15 Minuten Klarheit</b><ul><li>Betrifft mich das?</li><li>Wenn ja: wie?</li><li>Habe ich einen Vorteil?</li></ul></div><div class="cr__tk-ab"><span>Kostenlos</span></div></div></div>';
    }
    return '';
  }
  window.AVRG_CREATIVE = creative;
  var raster = $('#ig-raster');
  if (raster) {
    raster.innerHTML = P.map(function (p, i) {
      return '<button type="button" class="ig-kachel" data-i="' + i + '" data-th="' + p.th + '" aria-label="Posting ' + nr(i) + ' öffnen">' + creative(p) +
        '<span class="ig-kachel__info">' + nr(i) + ' · Woche ' + p.w + '<small>' + TH[p.th] + '</small></span></button>';
    }).join('');
    var filter = $('#ig-filter');
    filter.innerHTML = '<button type="button" aria-pressed="true" data-th="">Alle 30</button>' + Object.keys(TH).map(function (k) { return '<button type="button" aria-pressed="false" data-th="' + k + '">' + TH[k] + '</button>'; }).join('');
    $$('button', filter).forEach(function (b) {
      b.addEventListener('click', function () {
        var th = b.dataset.th;
        $$('button', filter).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        $$('.ig-kachel', raster).forEach(function (k) { k.hidden = th && k.dataset.th !== th; });
      });
    });
    var modal = $('#ig-modal'), jetzt = 0, kanal = 'ig';
    function zeigeText() {
      var p = P[jetzt], t = kanal === 'li' ? p.li : p.ig;
      $('#ig-m-text').innerHTML = t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/(#[\wäöüÄÖÜß]+)/g, '<span class="tags">$1</span>');
      $$('.ig-kanal button').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.kanal === kanal ? 'true' : 'false'); });
      var k = $('#ig-kopieren'); k.classList.remove('ist-kopiert'); k.textContent = kanal === 'li' ? 'LinkedIn-Text kopieren' : 'Text kopieren';
    }
    function sichtbar() { return $$('.ig-kachel', raster).filter(function (k) { return !k.hidden; }).map(function (k) { return +k.dataset.i; }); }
    function oeffne(i) {
      jetzt = i; var p = P[i];
      $('#ig-m-bild').innerHTML = creative(p);
      $('#ig-m-format').textContent = 'Posting ' + nr(i) + ' · Woche ' + p.w + ' · ' + TH[p.th];
      $('#ig-m-meta').innerHTML = '<dt>Bild</dt><dd>' + p.bild + '</dd><dt>Ziel</dt><dd>' + p.ziel + '</dd><dt>Format</dt><dd>Einzelbild 4:5 · 1080 × 1350 · Instagram, Facebook, LinkedIn</dd>';
      $('#ig-laden').href = '/assets/projekte/avrg/postings/posting-' + nr(i) + '.jpg';
      $('#ig-laden').setAttribute('download', 'posting-' + nr(i) + '.jpg');
      zeigeText();
      if (!modal.open) modal.showModal();
    }
    raster.addEventListener('click', function (e) { var k = e.target.closest('.ig-kachel'); if (k) oeffne(+k.dataset.i); });
    function blaettere(d) { var l = sichtbar(), pos = l.indexOf(jetzt); oeffne(l[(pos + d + l.length) % l.length]); }
    $('#ig-zurueck').addEventListener('click', function () { blaettere(-1); });
    $('#ig-vor').addEventListener('click', function () { blaettere(1); });
    $('#ig-zu').addEventListener('click', function () { modal.close(); });
    $$('.ig-kanal button').forEach(function (b) { b.addEventListener('click', function () { kanal = b.dataset.kanal; zeigeText(); }); });
    $('#ig-kopieren').addEventListener('click', function () {
      var t = kanal === 'li' ? P[jetzt].li : P[jetzt].ig, k = this;
      (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function () { k.classList.add('ist-kopiert'); k.textContent = 'Kopiert ✓'; }, function () { k.textContent = 'Bitte markieren und kopieren'; });
    });
    modal.addEventListener('click', function (e) { if (e.target === modal) modal.close(); });
    modal.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') blaettere(1); if (e.key === 'ArrowLeft') blaettere(-1); });
  }
})();
