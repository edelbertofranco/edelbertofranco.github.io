/* Admin do site: edita content/*.json no GitHub via API (token fine-grained no navegador). */
(() => {
  'use strict';
  const OWNER = 'edelbertofranco', REPO = 'edelbertofranco.github.io', BRANCH = 'main';
  const API = `https://api.github.com/repos/${OWNER}/${REPO}`;
  const $ = (s, r = document) => r.querySelector(s);
  const el = (tag, attrs = {}, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null || v === false) continue;
      if (k === 'class') n.className = v; else if (k === 'text') n.textContent = v;
      else if (k.startsWith('on')) n.addEventListener(k.slice(2), v); else n.setAttribute(k, v === true ? '' : v);
    }
    for (const c of kids.flat()) if (c != null) n.append(c.nodeType ? c : document.createTextNode(c));
    return n;
  };
  const clone = o => JSON.parse(JSON.stringify(o));

  // ------------------------------------------------------------------ esquemas
  const BI = (label, o = {}) => ({ type: 'bi', label, ...o });
  const BIT = (label, o = {}) => ({ type: 'bi', label, multiline: true, ...o });
  const T = (label, o = {}) => ({ type: 'text', label, ...o });
  const TA = (label, o = {}) => ({ type: 'textarea', label, ...o });
  const N = (label, o = {}) => ({ type: 'number', label, ...o });
  const SEL = (label, options, o = {}) => ({ type: 'select', label, options, ...o });
  const OBJ = (fields, o = {}) => ({ type: 'object', fields, ...o });
  const ARR = (item, o = {}) => ({ type: 'array', item, ...o });
  const IMG = (label, dir, o = {}) => ({ type: 'image', label, dir, ...o });
  const yearStart = N('Início (ano)', { hint: 'Deixe 0 se não souber.' });
  const yearEnd = N('Fim (ano)', { nullable: true, hint: 'Vazio = em andamento ("atual").' });
  const today = new Date().getFullYear();
  const pubLabel = p => p ? `${p.year} · ${p.title}` : '';

  const SECTIONS = [
    { group: 'Página inicial' },
    { file: 'news', title: 'Notícias', help: 'Aparecem na página inicial, na ordem da lista (a primeira fica no topo). O texto aceita HTML simples, como <a href="...">link</a> e <em>itálico</em>.',
      schema: ARR(OBJ({ date: T('Data', { hint: 'Ex.: 2026, nov/2026 ou 2023–' }), image: IMG('Foto (opcional)', 'images/news'), text: BIT('Texto (HTML simples)') }),
        { addAt: 'top', summary: x => [x.date, (x.text && (x.text.pt || x.text.en) || '').replace(/<[^>]+>/g, '')], blank: () => ({ date: String(today), image: '', text: { en: '', pt: '' } }) }) },
    { file: 'lines', title: 'Linhas de pesquisa', help: '"Grandes linhas" aparecem na página inicial; "Áreas" aparecem em Pesquisa e em Temas.',
      schema: OBJ({
        big: ARR(OBJ({ image: IMG('Ilustração', 'images'), title: BI('Título'), text: BIT('Descrição'), tags: ARR(BI('Etiqueta'), { compact: true, summary: x => [x.pt || x.en], blank: () => ({ en: '', pt: '' }) }) }),
          { label: 'Grandes linhas (página inicial)', summary: x => [x.title && x.title.pt], blank: () => ({ image: 'network.svg', title: { en: '', pt: '' }, text: { en: '', pt: '' }, tags: [] }) }),
        areas: ARR(OBJ({ image: IMG('Ilustração', 'images'), title: BI('Título'), text: BIT('Descrição') }),
          { label: 'Áreas (Pesquisa e Temas)', summary: x => [x.title && x.title.pt], blank: () => ({ image: 'ai.svg', title: { en: '', pt: '' }, text: { en: '', pt: '' } }) }) }) },
    { file: 'profile', title: 'Perfil e textos', help: 'Nome, foto, apresentação, links e textos fixos.',
      schema: OBJ({
        name: T('Nome'), photo: IMG('Foto', 'images'), role: BIT('Cargo (HTML)'), email: T('E-mail'),
        about: BIT('Sobre (HTML, parágrafos com <p>)', { rows: 8 }), prospective: BIT('Interessados em orientação (HTML)'),
        links: ARR(OBJ({ label: T('Rótulo'), url: T('URL') }, { row: true }), { label: 'Links do cabeçalho', summary: x => [x.label, x.url], blank: () => ({ label: '', url: '' }) }),
        selected: ARR({ type: 'pubref', label: 'Publicação' }, { label: 'Publicações selecionadas (página inicial)', compact: true, blank: () => '' }),
        collaborations: OBJ({ international: BIT('Internacionais (HTML)'), national: BIT('Nacionais (HTML)'), summary: BIT('Resumo para a página PQ (HTML)') }, { label: 'Colaborações' }),
        software: BIT('Registro de software (HTML)'), updated: BI('Data de atualização (rodapé)') }) },
    { group: 'Produção' },
    { file: 'publications', title: 'Publicações', help: 'Autores separados por vírgula, no formato "E. F. Silva". "E. F. Silva" aparece em negrito automaticamente. Em "Orientandos", repita exatamente o nome como está em Autores para ele aparecer sublinhado.',
      schema: ARR(OBJ({
        year: N('Ano'), type: SEL('Tipo', [['J', 'Periódico'], ['CI', 'Conferência internacional'], ['CN', 'Evento nacional'], ['B', 'Capítulo de livro']]),
        title: T('Título'), authors: TA('Autores (separados por vírgula)'), venue: T('Veículo (periódico ou evento)'), doi: T('DOI', { hint: 'Ex.: 10.1109/ACCESS.2026.3733594 (sem https://doi.org/)' }),
        students: ARR(T('Nome'), { label: 'Orientandos coautores', compact: true, blank: () => '' }),
        first: { type: 'bool', label: 'Primeiro autor' }, single: { type: 'bool', label: 'Autor único' },
        award: BI('Prêmio (opcional)', { nullable: true }) }, { rowKeys: ['year', 'type'] }),
        { addAt: 'top', search: true, summary: x => [x.year + ' · ' + ({ J: 'Periódico', CI: 'Conf. int.', CN: 'Nacional', B: 'Capítulo' }[x.type] || x.type), x.title],
          blank: () => ({ id: 'p' + Date.now().toString(36), year: today, type: 'J', title: '', authors: '', venue: '', doi: '', students: [], first: false, single: false, award: null }) }) },
    { file: 'highlights', title: 'Destaques (súmula)', help: 'Resultados em destaque na página Indicadores PQ (até 5, ao menos 3 de produção).',
      schema: ARR(OBJ({ pub: { type: 'pubref', label: 'Publicação' }, note: BIT('Comentário') }), { summary: x => [pubLabel(PUBS().find(p => p.id === x.pub))], blank: () => ({ pub: '', note: { en: '', pt: '' } }) }) },
    { group: 'Formação de RH' },
    { file: 'supervision', title: 'Orientações', help: 'Mestrado, TCC e iniciação científica. "Destino" é opcional (por exemplo, empresa ou programa de pós).',
      schema: OBJ({
        msc_ongoing: ARR(OBJ({ name: T('Nome'), since: N('Desde (ano)') }, { row: true }), { label: 'Mestrado em andamento', summary: x => [x.name, x.since], blank: () => ({ name: '', since: today }) }),
        msc_done: ARR(OBJ({ name: T('Nome'), year: N('Ano'), title: T('Título'), funding: T('Bolsa / financiamento'), award: T('Prêmio (opcional)'), next: BI('Destino (opcional)', { nullable: true }) }),
          { label: 'Mestrado concluído', addAt: 'top', summary: x => [x.year + ' · ' + x.name, x.title], blank: () => ({ name: '', title: '', year: today, award: '', funding: '', next: null }) }),
        tcc_ongoing: ARR(OBJ({ name: T('Nome'), title: T('Tema') }), { label: 'TCC em andamento', summary: x => [x.name, x.title], blank: () => ({ name: '', title: '' }) }),
        tcc_done: ARR(OBJ({ name: T('Nome'), year: N('Ano'), title: T('Título'), next: BI('Destino (opcional)', { nullable: true }) }),
          { label: 'TCC concluído', addAt: 'top', search: true, summary: x => [x.year + ' · ' + x.name, x.title], blank: () => ({ name: '', title: '', year: today, next: null }) }),
        ic_ongoing: ARR(OBJ({ name: T('Nome'), title: T('Projeto') }), { label: 'Iniciação científica em andamento', summary: x => [x.name, x.title], blank: () => ({ name: '', title: '' }) }),
        ic_done: ARR(OBJ({ name: T('Nome'), year: N('Ano'), title: T('Projeto'), funding: T('Bolsa') }),
          { label: 'Iniciação científica concluída', addAt: 'top', summary: x => [x.year + ' · ' + x.name, x.title], blank: () => ({ name: '', title: '', year: today, funding: '' }) }),
        other_count: N('Outras orientações (treinamento profissional), quantidade'),
        professional_training: TA('Treinamento profissional (nomes separados por ";")') }) },
    { file: 'boards', title: 'Bancas', help: 'Bancas de mestrado, doutorado e qualificação. Instituições diferentes de UFJF ganham a etiqueta "externa".',
      schema: OBJ({
        items: ARR(OBJ({ level: SEL('Nível', [['D', 'Doutorado'], ['M', 'Mestrado'], ['Q', 'Qualificação de mestrado']]), year: N('Ano'), institution: T('Instituição'), name: T('Candidato(a)'), title: T('Título') }, { rowKeys: ['level', 'year', 'institution'] }),
          { label: 'Bancas de pós-graduação', addAt: 'top', summary: x => [x.year + ' · ' + ({ D: 'Doutorado', M: 'Mestrado', Q: 'Qualificação' }[x.level] || '') + ' · ' + x.institution, x.name], blank: () => ({ level: 'M', year: today, name: '', title: '', institution: '' }) }),
        tcc_by_year: { type: 'map', label: 'Bancas de TCC por ano', keyLabel: 'Ano', valLabel: 'Quantidade' } }) },
    { group: 'Atuação' },
    { file: 'projects', title: 'Projetos', help: 'Papel e financiador. Projetos sem ano de fim aparecem como "em andamento".',
      schema: ARR(OBJ({ start: yearStart, end: yearEnd, role: SEL('Papel', [['Coordenador', 'Coordenador'], ['Pesquisador', 'Pesquisador']]), funder: T('Financiador'), title: T('Título') }, { rowKeys: ['start', 'end', 'role', 'funder'] }),
        { addAt: 'top', summary: x => [`${x.start || ''}–${x.end || 'atual'} · ${x.role}`, x.title], blank: () => ({ start: today, end: null, title: '', role: 'Coordenador', funder: '' }) }) },
    { file: 'recognition', title: 'Reconhecimento', help: 'Organização de eventos, comitês, prêmios, editoria, revisão, bolsas e liderança. A categoria define a seção onde o item aparece.',
      schema: ARR(OBJ({ start: yearStart, end: yearEnd, category: SEL('Categoria', ['Organização', 'Comitês de programa', 'Prêmios', 'Editorial', 'Revisão', 'Bolsas', 'Sociedades e comitês'].map(c => [c, c])), text: BIT('Texto') }, { rowKeys: ['start', 'end', 'category'] }),
        { addAt: 'top', search: true, summary: x => [`${x.start || ''}${x.end === x.start ? '' : '–' + (x.end || 'atual')} · ${x.category}`, x.text && x.text.pt], blank: () => ({ start: today, end: today, category: 'Organização', text: { en: '', pt: '' } }) }) },
    { file: 'contributions', title: 'Contribuições tecnológicas', help: 'Critério 4 do CA-CC: software, serviços, transferência de tecnologia e políticas.',
      schema: ARR(OBJ({ start: yearStart, end: yearEnd, category: BI('Categoria'), text: BIT('Texto') }, { rowKeys: ['start', 'end'] }),
        { addAt: 'top', summary: x => [`${x.start || ''}–${x.end || 'atual'}`, x.text && x.text.pt], blank: () => ({ start: today, end: null, category: { en: 'Software', pt: 'Software' }, text: { en: '', pt: '' } }) }) },
    { file: 'metrics', title: 'Métricas (Scholar)', help: 'Atualize com os números do seu perfil no Google Scholar. "Desde" corresponde à coluna "Since" do Scholar.',
      schema: OBJ({
        scholar: OBJ({ total: N('Citações (total)'), since: N('Citações (desde)'), h: N('Índice h'), h_since: N('Índice h (desde)'), i10: N('i10'), i10_since: N('i10 (desde)'), when: T('Data da coleta') }, { label: 'Google Scholar', row: true }),
        citations: { type: 'map', label: 'Citações por ano', keyLabel: 'Ano', valLabel: 'Citações' } }) },
    { group: 'Ensino' },
    { file: 'teaching', title: 'Disciplinas', help: 'Disciplina do semestre atual e lista de semestres anteriores (links para o Google Sites).',
      schema: OBJ({
        current: OBJ({ title: BI('Título'), url: T('Link da página da disciplina'), schedule: BIT('Horários (HTML)'), syllabus: BIT('Ementa') }, { label: 'Semestre atual' }),
        undergraduate: ARR(OBJ({ term: T('Semestre'), code: T('Código'), name: T('Disciplina'), url: T('Link') }, { rowKeys: ['term', 'code'] }), { label: 'Graduação (anteriores)', addAt: 'top', summary: x => [x.term + ' · ' + x.code, x.name], blank: () => ({ term: '', code: '', name: '', url: '' }) }),
        graduate: ARR(OBJ({ term: T('Semestre'), code: T('Código'), name: T('Disciplina'), url: T('Link') }, { rowKeys: ['term', 'code'] }), { label: 'Pós-graduação (anteriores)', addAt: 'top', summary: x => [x.term + ' · ' + x.code, x.name], blank: () => ({ term: '', code: '', name: '', url: '' }) }) }) },
    { file: 'topics', title: 'Temas de orientação', help: 'Página Temas. Cada item aceita HTML simples.',
      schema: OBJ({
        updated: T('Atualizado em'),
        groups: ARR(OBJ({ image: IMG('Ilustração', 'images'), title: BI('Título'), items: ARR(BIT('Tema'), { compact: true, summary: x => [x.pt], blank: () => ({ en: '', pt: '' }) }) }),
          { label: 'Grupos', summary: x => [x.title && x.title.pt], blank: () => ({ image: 'network.svg', title: { en: '', pt: '' }, items: [] }) }) }) },
  ];

  // ------------------------------------------------------------------ estado
  const S = { token: '', data: {}, sha: {}, orig: {}, current: 'news', raw: false };
  const PUBS = () => S.data.publications || [];
  const isDirty = f => S.data[f] !== undefined && JSON.stringify(S.data[f]) !== S.orig[f];
  const anyDirty = () => SECTIONS.some(s => s.file && isDirty(s.file));

  function toast(msg, ms = 3500) { const t = $('#toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove('show'), ms); }
  function status(text, kind = '') { $('#statusText').textContent = text; $('#status').className = 'status ' + kind; }
  function refreshDirty() {
    document.querySelectorAll('.side button[data-file]').forEach(b => b.classList.toggle('is-dirty', isDirty(b.dataset.file)));
    $('#saveAll').disabled = !anyDirty();
  }

  // ------------------------------------------------------------------ GitHub API
  async function gh(path, opts = {}) {
    const r = await fetch(path.startsWith('http') ? path : API + path, {
      ...opts, headers: { 'Authorization': 'Bearer ' + S.token, 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', ...(opts.headers || {}) } });
    if (!r.ok) { const e = new Error(`${r.status} ${(await r.json().catch(() => ({}))).message || r.statusText}`); e.status = r.status; throw e; }
    return r.status === 204 ? null : r.json();
  }
  const b64dec = s => new TextDecoder().decode(Uint8Array.from(atob(s.replace(/\n/g, '')), c => c.charCodeAt(0)));
  function b64encBytes(bytes) { let s = ''; for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000)); return btoa(s); }
  const b64enc = str => b64encBytes(new TextEncoder().encode(str));

  async function loadFile(f) {
    const j = await gh(`/contents/content/${f}.json?ref=${BRANCH}`);
    S.sha[f] = j.sha; S.data[f] = JSON.parse(b64dec(j.content)); S.orig[f] = JSON.stringify(S.data[f]);
  }
  async function saveFile(f, msg) {
    const body = { message: msg || `Admin: atualizar ${f}`, content: b64enc(JSON.stringify(S.data[f], null, 1) + '\n'), sha: S.sha[f], branch: BRANCH };
    const j = await gh(`/contents/content/${f}.json`, { method: 'PUT', body: JSON.stringify(body) });
    S.sha[f] = j.content.sha; S.orig[f] = JSON.stringify(S.data[f]);
  }
  async function uploadImage(dir, file) {
    const img = await resizeImage(file, 900);
    const base = file.name.toLowerCase().replace(/\.[^.]+$/, '').normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'imagem';
    const name = `${base}-${Date.now().toString(36).slice(-4)}.${img.ext}`;
    await gh(`/contents/${dir}/${name}`, { method: 'PUT', body: JSON.stringify({ message: `Admin: enviar imagem ${name}`, content: img.b64, branch: BRANCH }) });
    return name;
  }
  function resizeImage(file, max) {
    return new Promise((res, rej) => {
      if (/svg/.test(file.type)) { file.arrayBuffer().then(b => res({ b64: b64encBytes(new Uint8Array(b)), ext: 'svg' })); return; }
      const img = new Image(); const url = URL.createObjectURL(file);
      img.onload = () => {
        const s = Math.min(1, max / Math.max(img.width, img.height));
        const c = document.createElement('canvas'); c.width = Math.round(img.width * s); c.height = Math.round(img.height * s);
        const ctx = c.getContext('2d'); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height); ctx.drawImage(img, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url); res({ b64: c.toDataURL('image/jpeg', 0.85).split(',')[1], ext: 'jpg' });
      };
      img.onerror = () => rej(new Error('Imagem inválida')); img.src = url;
    });
  }
  async function watchDeploy() {
    status('Publicando…', 'busy');
    const t0 = Date.now();
    for (let i = 0; i < 40; i++) {
      await new Promise(r => setTimeout(r, 6000));
      try {
        const j = await gh(`/actions/runs?branch=${BRANCH}&per_page=1`);
        const run = j.workflow_runs && j.workflow_runs[0];
        if (!run || new Date(run.created_at).getTime() < t0 - 60000) continue;
        if (run.status === 'completed') {
          if (run.conclusion === 'success') { status('Publicado', 'ok'); toast('Site publicado. Pode levar alguns instantes para o cache atualizar.'); }
          else { status('Falha na publicação', 'err'); toast('A publicação falhou. Veja os detalhes em Actions no GitHub.', 8000); }
          return;
        }
      } catch (e) { if (e.status === 403 || e.status === 404) { status('Salvo · publicação em andamento', 'ok'); return; } }
    }
    status('Salvo', 'ok');
  }

  // ------------------------------------------------------------------ editores
  function field(label, input, hint) {
    return el('div', { class: 'f' }, label ? el('label', { text: label }) : null, input, hint ? el('div', { class: 'hint', text: hint }) : null);
  }
  function onChange() { refreshDirty(); }

  function render(schema, get, set, ctx = {}) {
    const v = get();
    switch (schema.type) {
      case 'text': case 'number': {
        const inp = el('input', { type: schema.type === 'number' ? 'number' : 'text', value: v == null ? '' : v });
        inp.addEventListener('input', () => {
          if (schema.type === 'number') set(inp.value === '' ? (schema.nullable ? null : 0) : Number(inp.value)); else set(inp.value);
          onChange(); ctx.onSummary && ctx.onSummary();
        });
        return field(schema.label, inp, schema.hint);
      }
      case 'textarea': {
        const ta = el('textarea', { rows: schema.rows || 3 }); ta.value = v || '';
        ta.addEventListener('input', () => { set(ta.value); onChange(); ctx.onSummary && ctx.onSummary(); });
        return field(schema.label, ta, schema.hint);
      }
      case 'bool': {
        const cb = el('input', { type: 'checkbox' }); cb.checked = !!v;
        cb.addEventListener('change', () => { set(cb.checked); onChange(); });
        return el('div', { class: 'f' }, el('label', {}, cb, ' ' + schema.label));
      }
      case 'select': {
        const s = el('select', {}, schema.options.map(([val, lab]) => el('option', { value: val, text: lab })));
        s.value = v; s.addEventListener('change', () => { set(s.value); onChange(); ctx.onSummary && ctx.onSummary(); });
        return field(schema.label, s, schema.hint);
      }
      case 'bi': {
        const cur = v || (schema.nullable ? null : { en: '', pt: '' });
        const mk = lang => {
          const val = cur ? (cur[lang] || '') : '';
          const inp = schema.multiline ? el('textarea', { rows: schema.rows || 3 }) : el('input', { type: 'text' });
          inp.value = val;
          inp.addEventListener('input', () => {
            let o = get(); if (!o) o = { en: '', pt: '' }; o[lang] = inp.value;
            if (schema.nullable && !o.en && !o.pt) set(null); else set(o);
            onChange(); ctx.onSummary && ctx.onSummary();
          });
          return el('div', {}, el('div', { class: 'lang', text: lang === 'pt' ? 'PORTUGUÊS' : 'ENGLISH' }), inp);
        };
        return field(schema.label, el('div', { class: 'bi' }, mk('pt'), mk('en')), schema.hint);
      }
      case 'image': {
        const prefix = schema.dir === 'images' ? 'images/' : schema.dir + '/';
        const val = v || '';
        const shown = () => { const x = get() || ''; return x ? (x.startsWith('images/') ? x : prefix + x) : ''; };
        const thumb = el('img', { class: 'thumb', alt: '' });
        const upd = () => { const s = shown(); thumb.src = s ? s + '?t=' + Date.now() : ''; thumb.style.visibility = s ? 'visible' : 'hidden'; };
        const inp = el('input', { type: 'text', value: val, placeholder: 'nome-do-arquivo.jpg' });
        inp.addEventListener('input', () => { set(inp.value); upd(); onChange(); });
        const fileIn = el('input', { type: 'file', accept: 'image/*', class: 'hidden' });
        fileIn.addEventListener('change', async () => {
          const f = fileIn.files[0]; if (!f) return;
          try { status('Enviando imagem…', 'busy'); let name = await uploadImage(schema.dir, f);
            if (schema.dir === 'images' && ctx.fullPath) name = 'images/' + name;
            inp.value = name; set(name); onChange(); status('Imagem enviada', 'ok'); toast('Imagem enviada. Ela aparece no site quando você salvar e publicar.');
            setTimeout(upd, 1500);
          } catch (e) { status('Erro ao enviar imagem', 'err'); toast('Erro: ' + e.message, 6000); }
        });
        const rm = el('button', { class: 'btn small', type: 'button', text: 'Remover', onclick: () => { inp.value = ''; set(''); upd(); onChange(); } });
        const up = el('button', { class: 'btn small', type: 'button', text: 'Enviar imagem…', onclick: () => fileIn.click() });
        upd();
        return field(schema.label, el('div', { class: 'imgf' }, thumb, inp, up, rm, fileIn), schema.dir === 'images/news' ? 'A imagem é reduzida para no máximo 900 px antes do envio.' : null);
      }
      case 'pubref': {
        const s = el('select', {}, el('option', { value: '', text: '(escolha)' }), PUBS().slice().sort((a, b) => b.year - a.year).map(p => el('option', { value: p.id, text: pubLabel(p).slice(0, 140) })));
        s.value = v || ''; s.addEventListener('change', () => { set(s.value); onChange(); ctx.onSummary && ctx.onSummary(); });
        return field(schema.label, s);
      }
      case 'map': {
        const box = el('div', { class: 'chiplist' });
        const draw = () => {
          box.innerHTML = '';
          const m = get() || {};
          Object.keys(m).sort((a, b) => b.localeCompare(a, undefined, { numeric: true })).forEach(k => {
            const ki = el('input', { type: 'text', value: k }); const vi = el('input', { type: 'number', value: m[k] });
            ki.addEventListener('change', () => { const mm = get(); const val = mm[k]; delete mm[k]; if (ki.value) mm[ki.value] = val; set(mm); onChange(); draw(); });
            vi.addEventListener('input', () => { const mm = get(); mm[k] = Number(vi.value || 0); set(mm); onChange(); });
            box.append(el('div', { class: 'li' }, el('div', {}, ki), el('div', {}, vi), el('button', { class: 'btn small danger', type: 'button', text: '✕', title: 'Remover', onclick: () => { const mm = get(); delete mm[k]; set(mm); onChange(); draw(); } })));
          });
        };
        draw();
        const add = el('button', { class: 'btn small', type: 'button', text: '+ ' + (schema.keyLabel || 'Item'), onclick: () => { const mm = get() || {}; const k = String(today); if (!(k in mm)) mm[k] = 0; else mm['novo'] = 0; set(mm); onChange(); draw(); } });
        return el('div', { class: 'obj' }, el('div', { class: 'otitle', text: schema.label }), el('div', { class: 'small muted', style: 'margin-bottom:6px', text: `${schema.keyLabel} · ${schema.valLabel}` }), box, el('div', { style: 'margin-top:8px' }, add));
      }
      case 'object': {
        if (!v) set({});
        const keys = Object.keys(schema.fields);
        const wrap = el('div', { class: ctx.root ? '' : (schema.label ? 'obj' : '') });
        if (schema.label && !ctx.root) wrap.append(el('div', { class: 'otitle', text: schema.label }));
        const rowKeys = schema.row ? keys.filter(k => ['text', 'number', 'select'].includes(schema.fields[k].type)) : (schema.rowKeys || []);
        if (rowKeys.length) {
          wrap.append(el('div', { class: 'row' }, rowKeys.map(k => render(schema.fields[k], () => get()[k], val => { get()[k] = val; }, ctx))));
        }
        keys.filter(k => !rowKeys.includes(k)).forEach(k => wrap.append(render(schema.fields[k], () => (get() || {})[k], val => { get()[k] = val; }, { ...ctx, root: false, fullPath: k === 'photo' })));
        return wrap;
      }
      case 'array': return renderArray(schema, get, set, ctx);
    }
    return el('div', { text: 'campo desconhecido' });
  }

  function renderArray(schema, get, set, ctx) {
    if (!Array.isArray(get())) set([]);
    const wrap = el('div', { class: ctx.root ? '' : 'obj' });
    const list = el('div');
    const countEl = el('span', { class: 'count' });
    let query = '';
    const summ = (x, i) => {
      const s = schema.summary ? schema.summary(x, i) : [typeof x === 'string' ? x : ''];
      return [String(s[0] == null ? '' : s[0]), s[1] ? String(s[1]) : ''];
    };
    const draw = (openIdx = -1) => {
      list.innerHTML = '';
      const arr = get();
      countEl.textContent = `${arr.length} ${arr.length === 1 ? 'item' : 'itens'}`;
      arr.forEach((x, i) => {
        const [a, b] = summ(x, i);
        if (query && !(a + ' ' + b + ' ' + JSON.stringify(x)).toLowerCase().includes(query)) return;
        const isPrim = !['object', 'array'].includes(schema.item.type) && schema.item.type !== 'bi';
        const actions = el('span', { class: 'item-actions' },
          el('button', { class: 'btn small', type: 'button', title: 'Mover para cima', text: '↑', onclick: e => { e.preventDefault(); if (i > 0) { [arr[i - 1], arr[i]] = [arr[i], arr[i - 1]]; onChange(); draw(); } } }),
          el('button', { class: 'btn small', type: 'button', title: 'Mover para baixo', text: '↓', onclick: e => { e.preventDefault(); if (i < arr.length - 1) { [arr[i + 1], arr[i]] = [arr[i], arr[i + 1]]; onChange(); draw(); } } }),
          el('button', { class: 'btn small danger', type: 'button', title: 'Excluir', text: '✕', onclick: e => { e.preventDefault(); if (confirmDel(a || b)) { arr.splice(i, 1); onChange(); draw(); } } }));
        if (schema.compact || isPrim) {
          const body = render(schema.item, () => get()[i], val => { get()[i] = val; }, { ...ctx, root: false });
          list.append(el('div', { class: 'li', style: 'display:flex;gap:6px;align-items:flex-start;margin-bottom:6px' }, el('div', { style: 'flex:1' }, body), actions));
          return;
        }
        const sumEl = el('span', { class: 'sum' }, el('strong', { text: a }), b ? el('small', { text: b.replace(/<[^>]+>/g, '') }) : null);
        const det = el('details', { class: 'item' }, el('summary', {}, sumEl, actions));
        let built = false;
        const build = () => {
          if (built) return; built = true;
          const body = el('div', { class: 'body' });
          body.append(render(schema.item, () => get()[i], val => { get()[i] = val; }, { ...ctx, root: false, onSummary: () => {
            const [a2, b2] = summ(get()[i], i); sumEl.firstChild.textContent = a2; if (sumEl.children[1]) sumEl.children[1].textContent = b2.replace(/<[^>]+>/g, '');
          } }));
          det.append(body);
        };
        det.addEventListener('toggle', () => { if (det.open) build(); });
        if (i === openIdx) { det.open = true; build(); }
        list.append(det);
      });
    };
    const add = el('button', { class: 'btn small', type: 'button', text: '+ Adicionar', onclick: () => {
      const arr = get(); const item = schema.blank ? schema.blank() : '';
      if (schema.addAt === 'top') { arr.unshift(item); onChange(); query = ''; if (searchIn) searchIn.value = ''; draw(0); }
      else { arr.push(item); onChange(); draw(arr.length - 1); }
    } });
    const head = el('div', { class: 'arr-head' }, schema.label ? el('strong', { text: schema.label }) : null, countEl, add);
    let searchIn = null;
    if (schema.search) {
      searchIn = el('input', { type: 'search', placeholder: 'Filtrar…' });
      searchIn.addEventListener('input', () => { query = searchIn.value.toLowerCase().trim(); draw(); });
      head.append(el('div', { style: 'flex:1' }, searchIn));
    }
    wrap.append(head, list);
    draw();
    return wrap;
  }
  function confirmDel(what) { return window.confirm(`Excluir "${(what || 'este item').slice(0, 80)}"?`); }

  // ------------------------------------------------------------------ telas
  function drawSide() {
    const side = $('#side'); side.innerHTML = '';
    SECTIONS.forEach(s => {
      if (s.group) { side.append(el('h4', { text: s.group })); return; }
      side.append(el('button', { 'data-file': s.file, class: s.file === S.current ? 'active' : '', onclick: () => { S.current = s.file; S.raw = false; drawSide(); drawMain(); } },
        el('span', { text: s.title }), el('span', { class: 'dirty', title: 'Alterações não salvas' })));
    });
    refreshDirty();
  }
  function drawMain() {
    const s = SECTIONS.find(x => x.file === S.current);
    const main = $('#main'); main.innerHTML = '';
    const tools = el('div', { class: 'toolbar' },
      el('button', { class: 'btn small', type: 'button', text: S.raw ? 'Voltar aos formulários' : 'Editar JSON bruto', onclick: () => { S.raw = !S.raw; drawMain(); } }),
      el('button', { class: 'btn small', type: 'button', text: 'Descartar alterações desta seção', onclick: () => { if (isDirty(s.file) && confirm('Descartar as alterações não salvas desta seção?')) { S.data[s.file] = JSON.parse(S.orig[s.file]); drawMain(); refreshDirty(); } } }),
      el('a', { class: 'btn small', href: `https://github.com/${OWNER}/${REPO}/commits/${BRANCH}/content/${s.file}.json`, target: '_blank', rel: 'noopener', text: 'Histórico ↗' }));
    main.append(el('h1', { text: s.title }), el('p', { class: 'help', text: s.help || '' }), tools);
    if (S.raw) {
      const ta = el('textarea', {}); ta.value = JSON.stringify(S.data[s.file], null, 2);
      const apply = el('button', { class: 'btn primary', type: 'button', text: 'Aplicar JSON', onclick: () => {
        try { S.data[s.file] = JSON.parse(ta.value); refreshDirty(); toast('JSON aplicado. Clique em "Salvar e publicar" para gravar.'); } catch (e) { toast('JSON inválido: ' + e.message, 6000); }
      } });
      main.append(el('div', { class: 'raw' }, ta, el('div', { style: 'margin-top:10px' }, apply)));
      return;
    }
    main.append(render(s.schema, () => S.data[s.file], v => { S.data[s.file] = v; }, { root: true }));
  }

  async function saveAll() {
    const files = SECTIONS.filter(s => s.file && isDirty(s.file)).map(s => s.file);
    if (!files.length) return;
    $('#saveAll').disabled = true; status('Salvando…', 'busy');
    try {
      for (const f of files) {
        try { await saveFile(f, `Admin: atualizar ${SECTIONS.find(s => s.file === f).title.toLowerCase()}`); }
        catch (e) {
          if (e.status === 409 || e.status === 422) {   // alguem alterou o arquivo: recarrega sha e tenta de novo
            const j = await gh(`/contents/content/${f}.json?ref=${BRANCH}`); S.sha[f] = j.sha; await saveFile(f);
          } else throw e;
        }
      }
      refreshDirty(); toast('Salvo. O GitHub está publicando o site (1 a 2 minutos).');
      watchDeploy();
    } catch (e) { status('Erro ao salvar', 'err'); toast('Erro ao salvar: ' + e.message, 8000); refreshDirty(); }
  }

  async function start() {
    status('Carregando…', 'busy');
    $('#loginView').classList.add('hidden');
    try {
      const repo = await gh('');
      if (repo.permissions && !repo.permissions.push) throw new Error('O token não tem permissão de escrita (Contents: Read and write).');
      await Promise.all(SECTIONS.filter(s => s.file).map(s => loadFile(s.file)));
      $('#appView').classList.remove('hidden'); $('#logout').classList.remove('hidden');
      drawSide(); drawMain(); status('Conectado', 'ok');
    } catch (e) {
      status('Desconectado'); $('#appView').classList.add('hidden'); $('#loginView').classList.remove('hidden');
      $('#loginErr').textContent = e.status === 401 ? 'Token inválido ou expirado.' : (e.status === 404 ? 'Repositório não encontrado com este token. Confira o "Resource owner" e o acesso ao repositório.' : 'Erro: ' + e.message);
      try { localStorage.removeItem('gh_token'); } catch (_) {}
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    $('#saveAll').addEventListener('click', saveAll);
    $('#logout').addEventListener('click', () => { if (anyDirty() && !confirm('Há alterações não salvas. Sair mesmo assim?')) return; try { localStorage.removeItem('gh_token'); sessionStorage.removeItem('gh_token'); } catch (e) {} location.reload(); });
    $('#loginBtn').addEventListener('click', () => {
      const tk = $('#token').value.trim(); if (!tk) return;
      S.token = tk;
      try { ($('#remember').checked ? localStorage : sessionStorage).setItem('gh_token', tk); } catch (e) {}
      start();
    });
    $('#token').addEventListener('keydown', e => { if (e.key === 'Enter') $('#loginBtn').click(); });
    window.addEventListener('beforeunload', e => { if (anyDirty()) { e.preventDefault(); e.returnValue = ''; } });
    let tk = ''; try { tk = localStorage.getItem('gh_token') || sessionStorage.getItem('gh_token') || ''; } catch (e) {}
    if (tk) { S.token = tk; start(); } else $('#loginView').classList.remove('hidden');
  });
})();
