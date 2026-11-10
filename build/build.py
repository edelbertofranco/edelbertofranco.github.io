#!/usr/bin/env python3
"""Gera o site edelbertofranco.github.io a partir de content/*.json.

Uso: python build/build.py [pasta_de_saida]   (padrao: _site)
Somente biblioteca padrao do Python. Ingles na raiz, portugues em /pt/.
O conteudo e editado em admin.html (ou diretamente nos arquivos JSON).
"""
import os, sys, json, html, shutil, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, '_site')
SITE = "https://edelbertofranco.github.io/"
NOW = int(time.strftime('%Y'))
BUILD = time.strftime('%Y%m%d%H%M')
E = html.escape
ASSETS = ['style.css', 'site.js', 'admin.html', 'admin.js', 'images', 'README.md']


def load(name):
    with open(os.path.join(ROOT, 'content', name + '.json'), encoding='utf-8') as f:
        return json.load(f)


PROFILE, NEWS, LINES = load('profile'), load('news'), load('lines')
PUBS, HIGHLIGHTS = load('publications'), load('highlights')
SUP, BOARDS, PROJECTS = load('supervision'), load('boards'), load('projects')
RECOG, CONTRIB, METRICS = load('recognition'), load('contributions'), load('metrics')
TEACH, TOPICS, MAP = load('teaching'), load('topics'), load('map')
PROJ_BY_TITLE = {x['title']: x for x in PROJECTS}
PUB_BY_ID = {p['id']: p for p in PUBS}
SCH = METRICS['scholar']

NAV = [("index.html", "Home", "Início"), ("research.html", "Research", "Pesquisa"), ("publications.html", "Publications", "Publicações"),
       ("team.html", "Team", "Equipe"), ("teaching.html", "Teaching", "Ensino"), ("temas.html", "Thesis topics", "Temas"),
       ("pq.html", "CNPq PQ", "Indicadores PQ")]

SUN = '<svg class="i-sun" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
MOON = '<svg class="i-moon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>'
FLAG_BR = ('<svg class="flag" viewBox="0 0 28 20" width="28" height="20" aria-hidden="true"><rect width="28" height="20" rx="3" fill="#009c3b"/>'
           '<path d="M14 2.6 25 10 14 17.4 3 10z" fill="#ffdf00"/><circle cx="14" cy="10" r="4.6" fill="#002776"/>'
           '<path d="M9.6 9.1c2.9-.6 6.1-.1 8.7 1.5" stroke="#fff" stroke-width=".9" fill="none"/></svg>')
FLAG_US = ('<svg class="flag" viewBox="0 0 28 20" width="28" height="20" aria-hidden="true"><clipPath id="fu"><rect width="28" height="20" rx="3"/></clipPath><g clip-path="url(#fu)">'
           '<rect width="28" height="20" fill="#fff"/>' + ''.join(f'<rect y="{i*20/13:.2f}" width="28" height="{20/13:.2f}" fill="#b22234"/>' for i in range(0, 13, 2)) +
           '<rect width="12.5" height="10.8" fill="#3c3b6e"/>' + ''.join(f'<circle cx="{1.8+2.2*c:.1f}" cy="{1.6+2.5*r:.1f}" r=".55" fill="#fff"/>' for r in range(4) for c in range(5)) + '</g></svg>')

HEAD_JS = """<script>
(function(){var d=document.documentElement;
try{var t=localStorage.getItem('theme');if(t==='light'||t==='dark')d.setAttribute('data-theme',t);}catch(e){}
window.__toggleTheme=function(){var mq=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
 var cur=d.getAttribute('data-theme')||mq;var nx=cur==='dark'?'light':'dark';
 if(nx===mq){d.removeAttribute('data-theme');try{localStorage.removeItem('theme');}catch(e){}}
 else{d.setAttribute('data-theme',nx);try{localStorage.setItem('theme',nx);}catch(e){}}
 try{window.dispatchEvent(new Event('themechange'));}catch(e){}};
window.__setLang=function(l){try{localStorage.setItem('lang',l);}catch(e){}};
try{var q=new URLSearchParams(location.search).get('lang');var s=null;
 if(q==='pt'||q==='en'){try{localStorage.setItem('lang',q);}catch(e){}s=q;}
 if(!s){try{s=localStorage.getItem('lang');}catch(e){}}
 if(!s){var n=((navigator.languages&&navigator.languages[0])||navigator.language||'en').toLowerCase();s=n.indexOf('pt')===0?'pt':'en';}
 var cur=d.lang.slice(0,2);
 if(s!==cur){location.replace('__ALT__'+location.hash);}
}catch(e){}})();
</script>"""

CRIT = ("https://www.gov.br/cnpq/pt-br/assuntos/comites-assessoramento/paginas-dos-cas/ciencia-da-computacao-cc/criterios/"
        "criterios-para-avaliacao-de-bolsas-de-produtividade-na-chamada-de-2026-do-ca-cc")


def authors_html(p):
    out = []
    for a in [x.strip() for x in p['authors'].split(',') if x.strip()]:
        if a == 'E. F. Silva':
            out.append('<strong>E. F. Silva</strong>')
        elif a in p.get('students', []):
            out.append(f'<span class="st">{E(a)}</span>')
        else:
            out.append(E(a))
    if len(out) > 8:
        mine = [i for i, x in enumerate(out) if 'E. F. Silva' in x]
        out = out[:3] + ['…'] + ([out[mine[0]]] if mine and mine[0] >= 3 else []) + ['et al.']
    return ', '.join(out)


def write_pubs_js():
    data = [dict(y=p['year'], t=p['type'], title=p['title'], a=authors_html(p), v=p['venue'], doi=p.get('doi', ''),
                 st=p.get('students', []), first=p.get('first', False), single=p.get('single', False), award=p.get('award') or '')
            for p in sorted(PUBS, key=lambda p: -p['year'])]
    cites = {int(k): v for k, v in METRICS['citations'].items()}
    with open(os.path.join(OUT, 'pubs.js'), 'w', encoding='utf-8') as f:
        f.write('/* Gerado por build/build.py a partir de content/publications.json. */\nwindow.PUBS=' + json.dumps(data, ensure_ascii=False) +
                ';\nwindow.CITES=' + json.dumps(cites) + ';\n')


def build(L):
    pt = L == 'pt'
    t = (lambda en, p: p) if pt else (lambda en, p: en)
    b = lambda d: (d or {}).get(L, '') if isinstance(d, dict) else (d or '')   # campo bilingue
    R = '../' if pt else ''
    lang_attr = 'pt-BR' if pt else 'en'

    def page(fname, title, body, scripts=False, desc=None):
        nav = ''.join(f'<li><a href="{f}" class="{"active " if f == fname else ""}{"pq" if f == "pq.html" else ""}">{t(en, p)}</a></li>' for f, en, p in NAV)
        other = 'en' if pt else 'pt'
        other_href = ('../' + fname if pt else 'pt/' + fname) + f'?lang={other}'
        js = f'<script src="{R}pubs.js?v={BUILD}"></script>' if scripts else ''
        d = desc or t("Edelberto Franco Silva, Associate Professor at UFJF: computer networks and cybersecurity.",
                      "Edelberto Franco Silva, Professor Associado da UFJF: redes de computadores e cibersegurança.")
        alt = ('../' + fname) if pt else ('pt/' + fname)
        doc = f"""<!doctype html>
<html lang="{lang_attr}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(d)}">
<meta name="author" content="Edelberto Franco Silva">
<link rel="alternate" hreflang="en" href="{SITE}{fname}">
<link rel="alternate" hreflang="pt-BR" href="{SITE}pt/{fname}">
<link rel="alternate" hreflang="x-default" href="{SITE}{fname}">
{HEAD_JS.replace('__ALT__', alt)}
<meta name="color-scheme" content="light dark">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap">
<link rel="stylesheet" href="{R}style.css?v={BUILD}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%231f4e8c'/%3E%3Ctext x='32' y='42' font-family='Arial' font-size='28' font-weight='700' fill='white' text-anchor='middle'%3EEF%3C/text%3E%3C/svg%3E">
</head>
<body>
<header class="site"><div class="wrap">
<a class="brand" href="index.html">Edelberto Franco Silva</a>
<nav aria-label="{t('Main', 'Principal')}"><ul>{nav}</ul></nav>
<div class="tools">
<a class="tool lang-switch" href="{other_href}" hreflang="{'en' if pt else 'pt-BR'}" data-lang="{other}" onclick="__setLang('{other}')" aria-label="{t('Ver em português', 'View in English')}" title="{t('Ver em português', 'View in English')}">{FLAG_US if pt else FLAG_BR}</a>
<button class="tool theme-switch" type="button" onclick="__toggleTheme()" aria-label="{t('Toggle light/dark theme', 'Alternar tema claro/escuro')}" title="{t('Toggle light/dark theme', 'Alternar tema claro/escuro')}">{SUN}{MOON}</button>
</div>
</div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">
<span>Edelberto Franco Silva · DCC/UFJF · {E(PROFILE['email'].replace('@', ' [at] '))}</span>
<span>{t("Updated", "Atualizado em")} {E(b(PROFILE['updated']))} {t("from the Lattes CV · Built with the assistance of Claude Opus 5.5 (Anthropic)", "a partir do Currículo Lattes · Construído com auxílio do Claude Opus 5.5 (Anthropic)")}</span>
</div></footer>
{js}<script src="{R}site.js?v={BUILD}"></script>
</body>
</html>
"""
        path = os.path.join(OUT, 'pt' if pt else '', fname)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(doc)

    LINKS = '<ul class="links">' + ''.join(f'<li><a href="{E(l["url"])}">{E(l["label"])}</a></li>' for l in PROFILE['links']) + '</ul>'
    areas_html = ''.join(f'<div class="area"><img src="{R}images/{E(a["image"])}" alt="" width="96" height="96"><h3>{E(b(a["title"]))}</h3><p>{E(b(a["text"]))}</p></div>' for a in LINES['areas'])

    def pub_li(p, note=''):
        doi = f' <a href="https://doi.org/{E(p["doi"])}">doi</a>' if p.get('doi') else ''
        aw = f'<span class="badge award">{E(b(p["award"]))}</span>' if p.get('award') else ''
        n = f'<br><span class="small">{E(note)}</span>' if note else ''
        return (f'<li class="pub"><span class="title">{E(p["title"])}</span>{aw}<br>'
                f'<span class="meta">{authors_html(p)}. <span class="venue">{E(p["venue"])}</span>, {p["year"]}.{doi}</span>{n}</li>')

    def news_li(n):
        img = n.get('image')
        th = f'<img class="news-thumb" src="{R}images/news/{E(img)}" alt="" loading="lazy" width="120" height="120">' if img else '<span class="news-thumb blank" aria-hidden="true"></span>'
        return f'<li>{th}<div><span class="date">{E(n["date"])}</span><span>{b(n["text"])}</span></div></li>'

    big_html = ''.join(f'<div class="bigline"><img src="{R}images/{E(x["image"])}" alt="" width="88" height="88"><div><h3>{E(b(x["title"]))}</h3><p>{E(b(x["text"]))}</p>'
                       f'<ul class="tags small">{"".join(f"<li>{E(b(g))}</li>" for g in x.get("tags", []))}</ul></div></div>' for x in LINES['big'])

    CTA = f"""<a class="cta" href="pq.html">
  <span class="cta-icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6"/><rect x="12" y="8" width="3" height="10"/><rect x="17" y="5" width="3" height="13"/></svg></span>
  <span class="cta-text"><strong>{t("CNPq evaluation · Research Productivity Fellowship", "Avaliação CNPq · Bolsa de Produtividade em Pesquisa")}</strong>
  <span>{t("Publications, supervision, examination boards, recognition and projects over the last 5 and 10 years, organized by the CA-CC criteria (2026 call).",
           "Produção, orientações, bancas, reconhecimento e projetos dos últimos 5 e 10 anos, organizados segundo os critérios do CA-CC (chamada 2026).")}</span></span>
  <span class="cta-go">{t("View indicators", "Ver indicadores")} →</span>
</a>"""

    # ---------------------------------------------------------- HOME
    home = f"""
<div class="hero">
  <div><img class="photo" src="{R}{E(PROFILE['photo'])}" alt="Edelberto Franco Silva"
    onerror="this.outerHTML='&lt;div class=&quot;photo-fallback&quot;&gt;EF&lt;/div&gt;'"></div>
  <div>
    <h1>{E(PROFILE['name'])}</h1>
    <p class="role">{b(PROFILE['role'])}</p>
    {LINKS}
  </div>
</div>
{CTA}
<section>
<h2>{t("About", "Sobre")}</h2>
{b(PROFILE['about'])}
</section>

<section>
<h2>{t("Research lines", "Linhas de pesquisa")}</h2>
<div class="biglines">{big_html}</div>
<p class="small" style="margin-top:14px"><a href="temas.html">{t("Detailed topics and supervision opportunities", "Temas detalhados e oportunidades de orientação")} →</a> · <a href="research.html">{t("Projects and collaborations", "Projetos e colaborações")} →</a></p>
</section>

<section>
<h2>{t("News", "Notícias")}</h2>
<ul class="clean news">{''.join(news_li(n) for n in NEWS)}</ul>
</section>

<section>
<h2>{t("Selected publications", "Publicações selecionadas")}</h2>
<ul class="clean">{''.join(pub_li(PUB_BY_ID[i]) for i in PROFILE.get('selected', []) if i in PUB_BY_ID)}</ul>
<p class="small" style="margin-top:12px"><a href="publications.html">{t("All publications", "Todas as publicações")} →</a></p>
</section>

<section>
<h2>{t("Prospective students", "Interessados em orientação")}</h2>
<p>{b(PROFILE['prospective'])}</p>
</section>
"""
    page("index.html", "Edelberto Franco Silva", home)

    # ---------------------------------------------------------- PUBLICATIONS
    CHIPS = ''.join(f'<button class="chip" data-type-chip="{k}" aria-pressed="false">{n}<span class="n"></span></button>' for k, n in [
        ("all", t("All", "Todas")), ("J", t("Journals", "Periódicos")), ("CI", t("International conferences", "Conf. internacionais")),
        ("CN", t("National conferences", "Eventos nacionais")), ("B", t("Chapters", "Capítulos"))])
    first_year = min(p['year'] for p in PUBS if p['year'])
    pubs_page = f"""
<div class="page-title"><h1>{t("Publications", "Publicações")}</h1>
<p class="muted">{t("Full papers registered in the Lattes CV (duplicates removed). Names with a dotted underline are supervised students.",
                    "Artigos completos registrados no Currículo Lattes (sem duplicatas). Nomes com sublinhado pontilhado são orientandos.")}
{t("Profiles", "Perfis")}: <a href="https://scholar.google.com/citations?user=StW3AKUAAAAJ">Google Scholar</a> ·
<a href="https://dblp.org/pid/241/2605.html">DBLP</a> · <a href="https://lattes.cnpq.br/3987091765361506">Lattes</a>.</p></div>
<section>
<div class="controls">
<label class="small muted" for="period">{t("Period", "Período")}</label>
<select id="period" class="chip">
<option value="{NOW-5}-{NOW}">{t("Last 5 years", "Últimos 5 anos")} ({NOW-5}–{NOW})</option>
<option value="{NOW-10}-{NOW}">{t("Last 10 years", "Últimos 10 anos")} ({NOW-10}–{NOW})</option>
<option value="{first_year}-{NOW}" selected>{t("All", "Todo o período")} ({first_year}–{NOW})</option>
</select>
</div>
<div class="controls" role="group" aria-label="{t('Type', 'Tipo')}">{CHIPS}</div>
<div id="publist"></div>
</section>
"""
    page("publications.html", t("Publications", "Publicações") + " · Edelberto Franco Silva", pubs_page, scripts=True)

    # ---------------------------------------------------------- helpers
    def yrs(a, b_):
        cur = t('present', 'atual')
        if not a: return cur if b_ is None else str(b_)
        if b_ is None: return f'{a}–{cur}'
        return str(a) if a == b_ else f'{a}–{b_}'
    def fr(a, b_): return f' data-from="{a or 0}"' + (f' data-to="{b_}"' if b_ is not None else '')
    ROLE = {'Coordenador': t('Coordinator', 'Coordenador'), 'Pesquisador': t('Researcher', 'Pesquisador')}
    def li_item(a, b_, text, badge='', coord=False):
        bd = f' <span class="badge{" coord" if coord else ""}">{E(badge)}</span>' if badge else ''
        return f'<li{fr(a, b_)}><span class="year">{yrs(a, b_)}</span><span>{E(text)}{bd}</span></li>'
    def proj_li(x):
        txt = x['title'] + (f' ({x["funder"]})' if x.get('funder') else '')
        return li_item(x['start'], x.get('end'), txt, ROLE.get(x['role'], x['role']), x['role'] == 'Coordenador')

    # ---------------------------------------------------------- PQ
    def li_sup(x, extra=''):
        nx = b(x.get('next'))
        d = f' <span class="muted small">{t("Next step", "Destino")}: {E(nx)}</span>' if nx else ''
        ex = f' <span class="badge award">{E(extra)}</span>' if extra else ''
        return f'<li{fr(x["year"], x["year"])}><strong>{E(x["name"])}</strong> ({x["year"]}){ex}<br><span class="small">{E(x["title"])}</span>{d}</li>'
    msc_done = ''.join(li_sup(x, x.get('award', '') if pt else x.get('award', '').replace('Melhor Dissertação', 'Best Dissertation')) for x in SUP['msc_done'])
    tcc_done = ''.join(li_sup(x) for x in SUP['tcc_done'])
    ic_done = ''.join(li_sup(x) for x in SUP['ic_done'])
    msc_on = ''.join(f'<li><strong>{E(x["name"])}</strong> ({t("since", "desde")} {x["since"]})</li>' for x in SUP['msc_ongoing'])
    tcc_on = ''.join(f'<li><strong>{E(x["name"])}</strong><br><span class="small">{E(x["title"])}</span></li>' for x in SUP['tcc_ongoing'])
    ic_on = ''.join(f'<li><strong>{E(x["name"])}</strong><br><span class="small">{E(x["title"])}</span></li>' for x in SUP['ic_ongoing'])

    def recog(cat): return ''.join(li_item(x['start'], x.get('end'), b(x['text'])) for x in RECOG if x['category'] == cat)
    tech = ''.join(li_item(x['start'], x.get('end'), b(x['text']), b(x['category'])) for x in CONTRIB)
    proj = ''.join(proj_li(x) for x in PROJECTS)

    LVL = {"D": t("Doctorate", "Doutorado"), "M": t("Master's", "Mestrado"), "Q": t("M.Sc. qualifying exam", "Qualificação de mestrado")}
    def li_banca(x):
        ext = '' if x['institution'].startswith('UFJF') else f' <span class="badge">{t("external", "externa")}</span>'
        return (f'<li{fr(x["year"], x["year"])} data-lvl="{x["level"]}"><strong>{E(x["name"])}</strong> ({x["year"]}) · {LVL.get(x["level"], x["level"])}, '
                f'{E(x["institution"])}{ext}<br><span class="small">{E(x["title"])}</span></li>')
    bancas_html = ''.join(li_banca(x) for x in BOARDS['items'])
    tcc_by = {int(k): v for k, v in BOARDS['tcc_by_year'].items()}
    tcc_bancas_html = ''.join(f'<li{fr(y, y)}>{y}: {n}</li>' for y, n in sorted(tcc_by.items(), reverse=True))
    tcc_marks = ''.join(f'<li{fr(y, y)}></li>' * n for y, n in tcc_by.items())
    hl_html = ''.join(pub_li(PUB_BY_ID[h['pub']], b(h['note'])) for h in HIGHLIGHTS if h['pub'] in PUB_BY_ID)

    pq = f"""
<div class="page-title">
<p class="kicker">{t("CNPq Research Productivity Fellowship", "Bolsa de Produtividade em Pesquisa · CNPq")}</p>
<h1>{t("Evaluation indicators (CA-CC)", "Indicadores para avaliação (CA-CC)")}</h1>
<p class="muted">{t(f'Output and activities organized according to the <a href="{CRIT}">criteria of the CNPq Computer Science Advisory Committee for the 2026 call</a> (published 21/10/2026, in Portuguese). Data extracted from the <a href="https://lattes.cnpq.br/3987091765361506">Lattes CV</a>, with duplicates removed. Titles are kept in their original language.',
                    f'Produção e atividades organizadas segundo os <a href="{CRIT}">critérios do Comitê de Assessoramento de Ciência da Computação para a chamada de 2026</a> (publicados em 21/10/2026). Dados extraídos do <a href="https://lattes.cnpq.br/3987091765361506">Currículo Lattes</a>, sem duplicatas.')}</p>
<p class="note">{t("<strong>AI-use statement:</strong> this page was built with the assistance of Claude Opus 5.5 (Anthropic), which extracted and organized data from the Lattes CV and Google Scholar. The author is responsible for the content, and the Lattes CV remains the official source.",
                   "<strong>Declaração de uso de IA:</strong> esta página foi construída com auxílio do Claude Opus 5.5 (Anthropic), que extraiu e organizou os dados do Currículo Lattes e do Google Scholar. O conteúdo é de responsabilidade do autor e o Lattes permanece a fonte oficial.")}</p>
</div>

<div class="period-bar">
<div class="controls" style="margin:0">
<label class="small" for="period"><strong>{t("Evaluation period", "Período de avaliação")}</strong></label>
<select id="period" class="chip">
<option value="{NOW-5}-{NOW}" selected>{t("Last 5 years", "Últimos 5 anos")} ({NOW-5}–{NOW})</option>
<option value="{NOW-10}-{NOW}">{t("Last 10 years", "Últimos 10 anos")} ({NOW-10}–{NOW})</option>
<option value="{first_year}-{NOW}">{t("Whole career", "Toda a carreira")}</option>
</select>
<span class="small muted">{t("Level C considers the previous five years; levels B and A, the previous decade.", "O nível C considera o quinquênio anterior; os níveis B e A, o decênio.")}</span>
</div>
<div class="toc"><a href="#resumo">{t("Summary", "Resumo")}</a><a href="#destaques">{t("Highlights", "Destaques")}</a><a href="#c1">1. {t("Publications", "Produção")}</a><a href="#c2">2. {t("Supervision", "Formação de RH")}</a><a href="#c3">3. {t("Recognition", "Reconhecimento")}</a><a href="#c4">4. {t("Technology transfer", "Contribuições tecnológicas")}</a><a href="#c5">5. {t("Projects", "Projetos e redes")}</a></div>
</div>

<section id="resumo">
<h2>{t("Summary for the period", "Resumo do período")} <span class="muted small" data-period-label></span></h2>
<div class="tiles">
<div class="tile"><div class="v" data-pubcount="J,CI"></div><div class="l">{t("International output (journals and international conferences)", "Produção internacional (periódicos e conf. internacionais)")}</div></div>
<div class="tile"><div class="v" data-pubcount="J"></div><div class="l"><span class="dot J"></span>{t("Journal articles", "Artigos em periódicos")}</div></div>
<div class="tile"><div class="v" data-pubcount="CI"></div><div class="l"><span class="dot CI"></span>{t("International conference papers", "Artigos em conferências internacionais")}</div></div>
<div class="tile"><div class="v" data-pubcount="CN"></div><div class="l"><span class="dot CN"></span>{t("National conference papers", "Artigos em eventos nacionais")}</div></div>
<div class="tile"><div class="v" data-count="#msc-done > li"></div><div class="l">{t("M.Sc. supervisions completed", "Mestrados orientados (concluídos)")}</div></div>
<div class="tile"><div class="v">{len(SUP['msc_ongoing'])}</div><div class="l">{t("M.Sc. supervisions ongoing", "Mestrados em andamento")}</div></div>
<div class="tile"><div class="v" data-count="#tcc-done > li, #ic-done > li"></div><div class="l">{t("Undergraduate theses and research projects completed", "TCC e IC concluídos")}</div></div>
<div class="tile"><div class="v" data-count="#bancas > li[data-lvl=D], #bancas > li[data-lvl=M]"></div><div class="l">{t("M.Sc. and D.Sc. examination boards", "Bancas de mestrado e doutorado")}</div></div>
<div class="tile"><div class="v" data-count="#proj > li:has(.coord)"></div><div class="l">{t("Projects coordinated", "Projetos coordenados")}</div></div>
<div class="tile"><div class="v">{SCH['since']}</div><div class="l">{t("Citations since", "Citações desde")} {NOW-5} (Google Scholar, {E(SCH['when'])})</div></div>
<div class="tile"><div class="v">{SCH['h']}</div><div class="l">{t("h-index", "Índice h")} ({SCH['h_since']} {t("since", "desde")} {NOW-5}); i10 = {SCH['i10']}</div></div>
</div>
<div class="grid2" style="margin-top:20px">
<div class="card"><h3>{t("Publications per year", "Publicações por ano")}</h3><div id="pubchart" data-label="{t('Publications per year and type', 'Publicações por ano e tipo')}"></div>
<div class="legend"><span><span class="dot J"></span>{t("Journals", "Periódicos")}</span><span><span class="dot CI"></span>{t("International conferences", "Conf. internacionais")}</span><span><span class="dot CN"></span>{t("National conferences", "Eventos nacionais")}</span></div></div>
<div class="card"><h3>{t("Citations per year (Google Scholar)", "Citações por ano (Google Scholar)")}</h3><div id="citechart" data-label="{t('Citations per year', 'Citações por ano')}"></div>
<p class="small muted" style="margin:6px 0 0">{t("Total", "Total")}: {SCH['total']} {t("citations.", "citações.")} {NOW} {t("is partial.", "parcial.")}</p></div>
</div>
</section>

<section id="destaques">
<p class="criterion">{t("Curriculum summary (súmula)", "Súmula curricular")}</p>
<h2>{t("Highlighted results", "Resultados em destaque")}</h2>
<p class="small muted">{t("The súmula allows up to 5 results (1,000 words), at least 3 of them scientific, technological or innovation outputs.", "A súmula admite até 5 resultados (1.000 palavras), sendo ao menos 3 de produção científica, tecnológica ou de inovação.")}</p>
<ul class="clean">{hl_html}</ul>
</section>

<section id="c1">
<p class="criterion">{t("Criterion 1", "Critério 1")}</p>
<h2>{t("Bibliographic production", "Produção bibliográfica")}</h2>
<p class="small muted">{t("The CA-CC considers this the most important criterion, with emphasis on high-impact international venues, regularity and leading authorship. Names with a dotted underline are supervised students; labels mark first author, sole author and awards.",
                         "O CA-CC considera este o critério mais importante, com ênfase em veículos internacionais de alto impacto, regularidade e protagonismo. Nomes com sublinhado pontilhado indicam orientandos; as etiquetas indicam 1º autor, autor único e prêmios.")}</p>
<div class="controls" role="group" aria-label="{t('Type', 'Tipo')}">{CHIPS}</div>
<div id="publist"></div>
</section>

<section id="c2">
<p class="criterion">{t("Criterion 2", "Critério 2")}</p>
<h2>{t("Training of human resources", "Formação de recursos humanos")}</h2>
<p class="small muted">{t('Completed and ongoing supervision, undergraduate research, examination boards and student participation in results (see the "student" label in criterion 1).',
                         'Orientações concluídas e em andamento, iniciação científica, participação em bancas e participação de orientandos nos resultados (ver etiqueta "orientando" no critério 1).')}</p>
<div class="grid2">
<div class="card"><h3>{t("M.Sc.: completed", "Mestrado: concluídas")} (<span data-count="#msc-done > li"></span>)</h3><ul class="clean" id="msc-done">{msc_done}</ul></div>
<div class="card"><h3>{t("Ongoing", "Em andamento")}</h3>
<p class="small muted" style="margin:0">{t("M.Sc. (PPGCC/UFJF)", "Mestrado (PPGCC/UFJF)")}</p><ul class="clean">{msc_on}</ul>
<p class="small muted" style="margin:10px 0 0">{t("Undergraduate research", "Iniciação científica")}</p><ul class="clean">{ic_on}</ul>
<p class="small muted" style="margin:10px 0 0">{t("Undergraduate theses (TCC)", "Trabalhos de conclusão de curso")}</p><ul class="clean">{tcc_on}</ul></div>
</div>
<div class="grid2" style="margin-top:20px">
<div class="card"><h3>{t("Undergraduate research: completed", "Iniciação científica: concluídas")} (<span data-count="#ic-done > li"></span>)</h3><ul class="clean" id="ic-done">{ic_done}</ul></div>
<div class="card"><h3>{t("Undergraduate theses: completed", "TCC: concluídos")} (<span data-count="#tcc-done > li"></span>)</h3><ul class="clean" id="tcc-done">{tcc_done}</ul></div>
</div>
<div class="card" style="margin-top:20px"><h3>{t("Examination boards", "Participação em bancas")}</h3>
<p class="small muted" style="margin:0 0 6px">{t("In the period", "No período")}: <strong data-count="#bancas > li[data-lvl=D]"></strong> {t("doctoral", "de doutorado")}, <strong data-count="#bancas > li[data-lvl=M]"></strong> {t("master's", "de mestrado")} {t("and", "e")} <strong data-count="#bancas > li[data-lvl=Q]"></strong> {t("qualifying", "de qualificação")}, {t("of which", "sendo")} <strong data-count="#bancas > li:has(.badge)"></strong> {t("outside UFJF", "externas à UFJF")}; {t("and", "e")} <strong data-count="#bancas-tcc-n li"></strong> {t("undergraduate", "de TCC")}.</p><ul id="bancas-tcc-n" style="display:none">{tcc_marks}</ul>
<ul class="clean" id="bancas">{bancas_html}</ul>
<p class="small muted" style="margin:10px 0 0">{t("Undergraduate thesis boards per year", "Bancas de TCC por ano")}:</p><ul class="tags" id="bancas-tcc">{tcc_bancas_html}</ul></div>
<p class="small muted" style="margin-top:12px">{t(f"The Lattes CV also lists {SUP['other_count']} other supervisions (professional training). Courses taught are listed under", f"Também constam no Lattes {SUP['other_count']} orientações de outra natureza (treinamento profissional). Disciplinas em")} <a href="teaching.html">{t("Teaching", "Ensino")}</a>.</p>
</section>

<section id="c3">
<p class="criterion">{t("Criterion 3", "Critério 3")}</p>
<h2>{t("National and international recognition", "Reconhecimento nacional e internacional")}</h2>
<p class="small muted">{t("Program committees, event organization, editorial roles, awards, research grants and leadership in graduate coordination, scientific societies and committees.",
                         "Comitês de programa, organização de eventos, editoria, prêmios, bolsas de pesquisa e liderança em coordenação de pós-graduação, sociedades científicas e comitês.")}</p>
<div class="grid2">
<div class="card"><h3>{t("Event organization", "Organização de eventos")}</h3><ul class="clean timeline">{recog("Organização")}</ul>
<h3>{t("Program committees", "Comitês de programa")}</h3><ul class="clean timeline">{recog("Comitês de programa")}</ul></div>
<div class="card"><h3>{t("Awards", "Prêmios")}</h3><ul class="clean timeline">{recog("Prêmios")}</ul>
<h3>{t("Editorial and review", "Editoria e revisão")}</h3><ul class="clean timeline">{recog("Editorial")}{recog("Revisão")}</ul>
<h3>{t("Research grants", "Bolsas de pesquisa")}</h3><ul class="clean timeline">{recog("Bolsas")}</ul>
<h3>{t("Leadership, societies and committees", "Liderança, sociedades e comitês")}</h3><ul class="clean timeline">{recog("Sociedades e comitês")}</ul></div>
</div>
</section>

<section id="c4">
<p class="criterion">{t("Criterion 4", "Critério 4")}</p>
<h2>{t("Technological, social and governmental contributions", "Contribuições tecnológicas, sociais e governamentais")}</h2>
<p class="small muted">{t("Registered software, technology transfer, services in production and impact on public policy.", "Software registrado, transferência de tecnologia, serviços em produção e impacto em políticas públicas.")}</p>
<ul class="clean timeline">{tech}</ul>
</section>

<section id="c5">
<p class="criterion">{t("Criterion 5", "Critério 5")}</p>
<h2>{t("Projects and research networks", "Projetos e redes de pesquisa")}</h2>
<p class="small muted">{t("Role in each project (coordinator or researcher) and funder, as in the Lattes CV.", "Papel em cada projeto (coordenador ou pesquisador) e financiador, conforme o Lattes.")}</p>
<ul class="clean timeline" id="proj">{proj}</ul>
<h3>{t("Collaborations", "Colaborações")}</h3>
<p>{b(PROFILE['collaborations']['summary'])}</p>
</section>
"""
    page("pq.html", t("CNPq PQ indicators", "Indicadores PQ") + " · Edelberto Franco Silva", pq, scripts=True,
         desc=t("Publications, supervision and recognition of Edelberto Franco Silva organized by the CNPq CA-CC criteria.",
                "Indicadores de produção, formação de recursos humanos e reconhecimento de Edelberto Franco Silva organizados segundo os critérios do CA-CC do CNPq."))


    # ---------------------------------------------------------- MAPA (temas x evidencias)
    PTYPE = {'J': t('Journal', 'Periódico'), 'CI': t('Intl. conf.', 'Conf. internacional'), 'CN': t('Natl. conf.', 'Conf. nacional'), 'B': t('Chapter', 'Capítulo')}
    def ev_pub(pid):
        p = PUB_BY_ID.get(pid)
        if not p:
            return ''
        ttl = E(p['title'])
        if p.get('doi'):
            ttl = f'<a href="https://doi.org/{E(p["doi"])}">{ttl}</a>'
        return f'<li><span class="ev pub">{PTYPE.get(p["type"], p["type"])} {p["year"]}</span> {ttl} <span class="muted">({E(p["venue"])})</span></li>'
    def ev_proj(title):
        x = PROJ_BY_TITLE.get(title)
        if not x:
            return ''
        yr = f'{x["start"]}–{x["end"]}' if x.get('end') else f'{x["start"]}–{t("ongoing", "atual")}'
        fd = f' <span class="muted">({E(x["funder"])})</span>' if x.get('funder') else ''
        return f'<li><span class="ev proj">{t("Project", "Projeto")} {yr}</span> {E(x["title"])}{fd}</li>'
    def map_topic(tp):
        ev = ''.join(ev_pub(i) for i in tp.get('pubs', [])) + ''.join(ev_proj(p) for p in tp.get('projects', []))
        return f'<li class="map-topic"><strong>{E(b(tp["name"]))}</strong><ul class="evid small">{ev}</ul></li>'
    map_html = ''.join(
        f'<div class="card map-group"><div class="tema-head"><img src="{R}images/{E(g["image"])}" alt="" width="64" height="64"><h3>{E(b(g["title"]))}</h3></div>'
        + ''.join(f'<h4 class="map-row">{E(b(r["label"]))}</h4><ul class="clean map-list">{"".join(map_topic(tp) for tp in r["topics"])}</ul>' for r in g['rows'])
        + '</div>' for g in MAP['groups'])
    map_section = (f'<section id="mapa"><h2>{t("Research map", "Mapa de pesquisa")} ({E(MAP["period"])})</h2>'
                   f'<p class="muted">{E(b(MAP["intro"]))} {t("Updated", "Atualizado em")} {E(MAP["updated"])}.</p><div class="grid2">{map_html}</div></section>')

    # ---------------------------------------------------------- RESEARCH
    research = f"""
<div class="page-title"><h1>{t("Research", "Pesquisa")}</h1><p class="muted">{t('Research areas, projects, awards and professional service. A version organized by CNPq criteria is in <a href="pq.html">CNPq PQ</a>.', 'Linhas de pesquisa, projetos, prêmios e atuação profissional. Uma versão organizada pelos critérios do CNPq está em <a href="pq.html">Indicadores PQ</a>.')}</p></div>
<section><h2>{t("Research areas", "Linhas de pesquisa")}</h2><div class="areas">{areas_html}</div></section>
<section>
<h2>{t("Ongoing projects", "Projetos em andamento")}</h2>
<ul class="clean timeline">{''.join(proj_li(x) for x in PROJECTS if x.get('end') is None)}</ul>
<h2 style="margin-top:22px">{t("Past projects", "Projetos concluídos")}</h2>
<ul class="clean timeline">{''.join(proj_li(x) for x in PROJECTS if x.get('end') is not None)}</ul>
</section>
<section><h2>{t("Awards", "Prêmios")}</h2><ul class="clean timeline">{recog("Prêmios")}</ul></section>
<section>
<h2>{t("Professional service", "Atuação profissional")}</h2>
<div class="grid2">
<div class="card"><h3>{t("Editorial and review", "Editoria e revisão")}</h3><ul class="clean timeline">{recog("Editorial")}{recog("Revisão")}</ul></div>
<div class="card"><h3>{t("Leadership and committees", "Liderança e comitês")}</h3><ul class="clean timeline">{recog("Sociedades e comitês")}</ul></div>
</div>
<h3>{t("Conference organization", "Organização de eventos")}</h3>
<ul class="clean timeline">{recog("Organização")}{recog("Comitês de programa")}</ul>
</section>
<section>
<h2>{t("Collaborations", "Colaborações")}</h2>
<div class="grid2">
<div class="card"><h3>{t("International", "Internacionais")}</h3><p>{b(PROFILE['collaborations']['international'])}</p></div>
<div class="card"><h3>{t("National", "Nacionais")}</h3><p>{b(PROFILE['collaborations']['national'])}</p></div>
</div>
</section>
<section><h2>{t("Software registration", "Registro de software")}</h2><p>{b(PROFILE['software'])}</p></section>
"""
    page("research.html", t("Research", "Pesquisa") + " · Edelberto Franco Silva", research)

    # ---------------------------------------------------------- TEAM
    def rows(items, msc=False):
        return ''.join(f'<tr><td>{E(x["name"])}</td><td class="num">{x["year"]}</td><td>{E(x["title"])}</td><td>{E(b(x.get("next")))}</td></tr>' for x in items)
    H = lambda c: f'<thead><tr><th>{t("Name", "Nome")}</th><th>{t("Year", "Ano")}</th><th>{c}</th><th>{t("Next step", "Destino")}</th></tr></thead>'
    team = f"""
<div class="page-title"><h1>{t("Team", "Equipe")}</h1><p class="muted">{t("Current students and alumni, as registered in the Lattes CV. Titles are kept in their original language.", "Alunos atuais e egressos, conforme o Currículo Lattes.")}</p></div>
<section>
<h2>{t("Current students", "Alunos atuais")}</h2>
<div class="grid2">
<div class="card"><h3>{t("M.Sc. (PPGCC/UFJF)", "Mestrado (PPGCC/UFJF)")}</h3><ul class="clean">{''.join(f'<li>{E(x["name"])}</li>' for x in SUP['msc_ongoing'])}</ul>
<h3>{t("Undergraduate research and research grants", "Iniciação científica e bolsistas")}</h3><ul class="clean">{''.join(f'<li>{E(x["name"])}<br><span class="small muted">{E(x["title"])}</span></li>' for x in SUP['ic_ongoing'])}</ul></div>
<div class="card"><h3>{t("Undergraduate theses (TCC)", "Trabalhos de conclusão de curso (TCC)")}</h3><ul class="clean">{''.join(f'<li>{E(x["name"])}<br><span class="small muted">{E(x["title"])}</span></li>' for x in SUP['tcc_ongoing'])}</ul></div>
</div>
</section>
<section>
<h2>{t("Alumni", "Egressos")}</h2>
<h3>{t("M.Sc. dissertations", "Dissertações de mestrado")}</h3>
<div class="table-scroll"><table>{H(t("Dissertation", "Dissertação"))}<tbody>{rows(SUP['msc_done'])}</tbody></table></div>
<h3>{t("Undergraduate theses (TCC)", "Trabalhos de conclusão de curso (TCC)")}</h3>
<div class="table-scroll"><table>{H(t("Thesis", "Trabalho"))}<tbody>{rows(SUP['tcc_done'])}</tbody></table></div>
<h3>{t("Undergraduate research", "Iniciação científica")}</h3>
<div class="table-scroll"><table>{H(t("Project", "Projeto"))}<tbody>{rows(SUP['ic_done'])}</tbody></table></div>
<h3>{t("Professional training (UFJF)", "Treinamento profissional (UFJF)")}</h3>
<p>{E(SUP.get('professional_training', ''))}</p>
</section>
"""
    page("team.html", t("Team", "Equipe") + " · Edelberto Franco Silva", team)

    # ---------------------------------------------------------- TEACHING
    def ctable(items):
        r = ''.join(f'<tr><td>{E(x["term"])}</td><td>{E(x["code"])}</td><td><a href="{E(x["url"])}">{E(x["name"])}</a></td></tr>' for x in items)
        return f'<div class="table-scroll"><table><thead><tr><th>{t("Term", "Semestre")}</th><th>{t("Code", "Código")}</th><th>{t("Course", "Disciplina")}</th></tr></thead><tbody>{r}</tbody></table></div>'
    cur = TEACH['current']
    teaching = f"""
<div class="page-title"><h1>{t("Teaching", "Ensino")}</h1><p class="muted">{t("Undergraduate and graduate courses at DCC/UFJF (taught in Portuguese). Each course page, with schedule and materials, remains on Google Sites.", "Disciplinas de graduação e pós-graduação no DCC/UFJF. As páginas de cada disciplina, com cronograma e material, continuam no Google Sites.")}</p></div>
<section>
<h2>{t("Current term", "Semestre atual")}</h2>
<div class="card">
<h3><a href="{E(cur['url'])}">{E(b(cur['title']))}</a></h3>
<p>{b(cur['schedule'])}</p>
<p class="small muted">{t("Syllabus", "Ementa")}: {E(b(cur['syllabus']))}</p>
</div>
</section>
<section><h2>{t("Undergraduate: previous terms", "Graduação: semestres anteriores")}</h2>{ctable(TEACH['undergraduate'])}</section>
<section><h2>{t("Graduate (PPGCC): previous terms", "Pós-graduação (PPGCC): semestres anteriores")}</h2>{ctable(TEACH['graduate'])}</section>
"""
    page("teaching.html", t("Teaching", "Ensino") + " · Edelberto Franco Silva", teaching)

    # ---------------------------------------------------------- TEMAS
    groups = ''.join(f'<div class="card"><div class="tema-head"><img src="{R}images/{E(g["image"])}" alt="" width="84" height="84"><h3>{E(b(g["title"]))}</h3></div>'
                     f'<ul class="clean">{"".join(f"<li>{b(i)}</li>" for i in g["items"])}</ul></div>' for g in TOPICS['groups'])
    temas = f"""
<div class="page-title"><h1>{t("Thesis topics", "Temas de orientação")}</h1><p class="muted">{t("Undergraduate (TCC and scientific initiation) and graduate. Updated", "Graduação (TCC e iniciação científica) e pós-graduação. Atualizado em")} {E(TOPICS['updated'])}.</p></div>
<section>
<p>{t('These are topics of interest with a well-defined direction, in the broad areas of Computer Networks and Cybersecurity. Other topics in these lines can be discussed. If a topic interests you, <a href="mailto:edelberto.franco@ufjf.br">get in touch</a>.',
      'Esta lista reúne temas de interesse com encaminhamento bem definido, nas grandes áreas de Redes de Computadores e Cibersegurança. Outros temas nessas linhas podem ser discutidos. Se algum tema despertou seu interesse, <a href="mailto:edelberto.franco@ufjf.br">entre em contato</a>.')}</p>
</section>
{map_section}
<section><h2>{t("Other topics of interest", "Outros temas de interesse")}</h2><div class="grid2">{groups}</div></section>
<section>
<h2>{t("Research lines these topics fit into", "Linhas em que os temas se encaixam")}</h2>
<div class="areas">{''.join(f'<div class="area"><img src="{R}images/{E(a["image"])}" alt="" width="96" height="96"><h3>{E(b(a["title"]))}</h3></div>' for a in LINES['areas'])}</div>
</section>
"""
    page("temas.html", t("Thesis topics", "Temas de orientação") + " · Edelberto Franco Silva", temas)
    if not pt:
        page("404.html", "Page not found", f'<div class="page-title"><h1>Page not found / Página não encontrada</h1><p><a href="{SITE}">Home</a></p></div>')


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, 'pt'))
    for a in ASSETS:
        src = os.path.join(ROOT, a)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(OUT, a))
        elif os.path.isfile(src):
            shutil.copy2(src, os.path.join(OUT, a))
    os.makedirs(os.path.join(OUT, 'content'))
    for f in os.listdir(os.path.join(ROOT, 'content')):   # publicado para leitura pelo admin
        shutil.copy2(os.path.join(ROOT, 'content', f), os.path.join(OUT, 'content', f))
    write_pubs_js()
    build('en'); build('pt')
    # 404 usa caminhos absolutos (servido em qualquer profundidade)
    p = os.path.join(OUT, '404.html')
    s = open(p, encoding='utf-8').read().replace(f'href="style.css?v={BUILD}"', f'href="/style.css?v={BUILD}"').replace(f'src="site.js?v={BUILD}"', f'src="/site.js?v={BUILD}"')
    open(p, 'w', encoding='utf-8').write(s)
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    print('site gerado em', OUT, '·', len(PUBS), 'publicações')


if __name__ == '__main__':
    main()
