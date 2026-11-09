/* Filtros por periodo, contagens, lista de publicacoes e graficos.
   Depende de window.PUBS (pubs.js) e, opcionalmente, window.CITES. */
(function () {
  const NOW = 2026;
  const TYPES = {
    J: { pt: 'Periódicos', en: 'Journals' },
    CI: { pt: 'Conferências internacionais', en: 'International conferences' },
    CN: { pt: 'Conferências nacionais', en: 'National conferences' },
    B: { pt: 'Capítulos', en: 'Book chapters' },
  };
  const lang = document.documentElement.lang.startsWith('pt') ? 'pt' : 'en';
  const state = { from: 2021, to: NOW, type: 'all' };
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  const tip = document.createElement('div'); tip.className = 'tip'; document.body.appendChild(tip);
  function showTip(e, html) { tip.innerHTML = html; tip.style.opacity = 1; tip.style.left = (e.clientX + 12) + 'px'; tip.style.top = (e.clientY + 12) + 'px'; }
  function hideTip() { tip.style.opacity = 0; }

  function inPeriod(from, to) { return to >= state.from && from <= state.to; }
  const pubsIn = () => (window.PUBS || []).filter(p => p.y >= state.from && p.y <= state.to);

  function applyPeriod() {
    $$('[data-from]').forEach(el => {
      const f = +el.dataset.from || 0, t = el.dataset.to ? +el.dataset.to : NOW;
      el.classList.toggle('hidden', !inPeriod(f, t));
    });
    $$('[data-count]').forEach(el => {
      el.textContent = $$(el.dataset.count).filter(x => !x.classList.contains('hidden')).length;
    });
    $$('[data-pubcount]').forEach(el => {
      const k = el.dataset.pubcount;
      el.textContent = pubsIn().filter(p => k === 'all' || k.split(',').includes(p.t)).length;
    });
    $$('[data-period-label]').forEach(el => el.textContent = state.from + '–' + state.to);
    renderPubs(); renderPubChart();
  }

  function renderPubs() {
    const box = $('#publist'); if (!box) return;
    const list = pubsIn().filter(p => state.type === 'all' || p.t === state.type);
    $$('[data-type-chip]').forEach(c => {
      const k = c.dataset.typeChip;
      c.setAttribute('aria-pressed', String(k === state.type));
      const n = c.querySelector('.n'); if (n) n.textContent = pubsIn().filter(p => k === 'all' || p.t === k).length;
    });
    let html = '', year = null;
    list.sort((a, b) => b.y - a.y || a.t.localeCompare(b.t));
    for (const p of list) {
      if (p.y !== year) { if (year !== null) html += '</ul>'; year = p.y; html += `<h3 class="year-h">${year}</h3><ul class="clean">`; }
      const doi = p.doi ? ` <a href="https://doi.org/${esc(p.doi)}">doi</a>` : '';
      const aw = p.award ? (typeof p.award === 'string' ? p.award : p.award[lang]) : '';
      const badges = (aw ? `<span class="badge award">${esc(aw)}</span>` : '') +
        (p.st && p.st.length ? `<span class="badge" title="${lang === 'pt' ? 'Coautoria com orientando(s)' : 'Co-authored with supervised student(s)'}">${lang === 'pt' ? 'orientando' : 'student'}</span>` : '') +
        (p.single ? `<span class="badge">${lang === 'pt' ? 'autor único' : 'sole author'}</span>` : p.first ? `<span class="badge">${lang === 'pt' ? '1º autor' : 'first author'}</span>` : '');
      html += `<li class="pub"><span class="dot ${p.t}" title="${TYPES[p.t][lang]}"></span><span class="title">${esc(p.title)}</span>${badges}<br>` +
        `<span class="meta">${p.a}. <span class="venue">${esc(p.v)}</span>, ${p.y}.${doi}</span></li>`;
    }
    box.innerHTML = list.length ? html + '</ul>' : `<p class="muted">${lang === 'pt' ? 'Nenhuma publicação no período.' : 'No publications in this period.'}</p>`;
  }

  function svgBars(el, years, series, keys, colors, labels) {
    const W = 460, H = 200, L = 30, B = 24, T = 10, R = 6;
    const totals = years.map((_, i) => keys.reduce((s, k) => s + series[k][i], 0));
    const max = Math.max(4, ...totals);
    const step = max <= 10 ? 2 : max <= 30 ? 5 : max <= 120 ? 20 : 50;
    const top = Math.ceil(max / step) * step;
    const y = v => T + (H - T - B) * (1 - v / top);
    const bw = Math.min(34, (W - L - R) / years.length * 0.62);
    const x = i => L + (W - L - R) * (i + 0.5) / years.length;
    let s = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(el.dataset.label || '')}">`;
    for (let v = 0; v <= top; v += step) s += `<line class="grid" x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}"/><text x="${L - 6}" y="${y(v) + 4}" text-anchor="end">${v}</text>`;
    years.forEach((yr, i) => {
      let acc = 0;
      keys.forEach((k, j) => {
        const v = series[k][i]; if (!v) return;
        const y0 = y(acc), y1 = y(acc + v); acc += v;
        const isTop = keys.slice(j + 1).every(k2 => !series[k2][i]);
        const h = Math.max(0, y0 - y1 - 2);
        const r = isTop ? Math.min(4, h / 2) : 0;
        const xx = x(i) - bw / 2, yy = y1;
        s += r ? `<path d="M${xx},${yy + h} V${yy + r} Q${xx},${yy} ${xx + r},${yy} H${xx + bw - r} Q${xx + bw},${yy} ${xx + bw},${yy + r} V${yy + h} Z" fill="${colors[j]}"/>`
               : `<rect x="${xx}" y="${yy}" width="${bw}" height="${h}" fill="${colors[j]}"/>`;
      });
      const detail = keys.map((k, j) => `${labels[j]}: ${series[k][i]}`).join('<br>');
      s += `<rect x="${x(i) - (W - L - R) / years.length / 2}" y="${T}" width="${(W - L - R) / years.length}" height="${H - T - B}" fill="transparent" data-tip="<b>${yr}</b>${keys.length > 1 ? ' · ' + totals[i] : ''}<br>${detail}"/>`;
      s += `<text x="${x(i)}" y="${H - 8}" text-anchor="middle">${yr}</text>`;
    });
    el.innerHTML = s + '</svg>';
    $$('[data-tip]', el).forEach(r => { r.addEventListener('mousemove', e => showTip(e, r.dataset.tip)); r.addEventListener('mouseleave', hideTip); });
  }

  const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  function renderPubChart() {
    const el = $('#pubchart'); if (!el) return;
    const years = []; for (let yv = state.from; yv <= state.to; yv++) years.push(yv);
    const keys = ['J', 'CI', 'CN'];
    const series = Object.fromEntries(keys.map(k => [k, years.map(yv => (window.PUBS || []).filter(p => p.y === yv && p.t === k).length)]));
    svgBars(el, years, series, keys, [css('--s1'), css('--s2'), css('--s3')], keys.map(k => TYPES[k][lang]));
  }
  function renderCiteChart() {
    const el = $('#citechart'); if (!el || !window.CITES) return;
    const years = Object.keys(window.CITES).map(Number).filter(v => v >= 2016);
    svgBars(el, years, { c: years.map(v => window.CITES[v]) }, ['c'], [css('--s1')], [lang === 'pt' ? 'Citações' : 'Citations']);
  }

  document.addEventListener('DOMContentLoaded', () => {
    const sel = $('#period');
    if (sel) {
      const key = 'period:' + location.pathname.split('/').pop();
      try { const saved = localStorage.getItem(key); if (saved && [...sel.options].some(o => o.value === saved)) sel.value = saved; } catch (e) {}
      const set = () => { const [f, t] = sel.value.split('-').map(Number); state.from = f; state.to = t; try { localStorage.setItem(key, sel.value); } catch (e) {} applyPeriod(); };
      sel.addEventListener('change', set); set();
    } else {
      const d = document.body.dataset; state.from = +(d.from || 1900); state.to = +(d.to || NOW); applyPeriod();
    }
    $$('[data-type-chip]').forEach(c => c.addEventListener('click', () => { state.type = c.dataset.typeChip; renderPubs(); }));
    renderCiteChart();
    const rerender = () => { renderPubChart(); renderCiteChart(); };
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    mq.addEventListener('change', rerender);
    // tema: alterna entre claro e escuro; se coincidir com o do sistema, volta a seguir o sistema
    const tb = $('.theme-switch');
    if (tb) tb.addEventListener('click', () => {
      const root = document.documentElement;
      const cur = root.getAttribute('data-theme') || (mq.matches ? 'dark' : 'light');
      const next = cur === 'dark' ? 'light' : 'dark';
      if (next === (mq.matches ? 'dark' : 'light')) { root.removeAttribute('data-theme'); try { localStorage.removeItem('theme'); } catch (e) {} }
      else { root.setAttribute('data-theme', next); try { localStorage.setItem('theme', next); } catch (e) {} }
      rerender();
    });
    // idioma: guarda a escolha explicita
    const ls = $('.lang-switch');
    if (ls) ls.addEventListener('click', () => { try { localStorage.setItem('lang', ls.dataset.lang); } catch (e) {} });
  });
})();
