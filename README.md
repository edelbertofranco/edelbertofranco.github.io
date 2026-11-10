# edelbertofranco.github.io

Site acadêmico de Edelberto Franco Silva (DCC/UFJF), em inglês (raiz) e português (`/pt/`).

## Como funciona

- **Conteúdo**: arquivos JSON em `content/` (notícias, publicações, orientações, bancas, projetos, reconhecimento, métricas, ensino, temas, perfil).
- **Edição**: pela página [`/admin.html`](https://edelbertofranco.github.io/admin.html), que grava os JSON neste repositório pela API do GitHub. Também é possível editar os JSON diretamente.
- **Publicação**: a cada alteração em `main`, o workflow `.github/workflows/pages.yml` roda `python build/build.py` e publica o resultado no GitHub Pages (1 a 2 minutos).
- **Aparência**: `style.css`, `site.js` e imagens em `images/` (fotos de notícias em `images/news/`).

Os arquivos `.html` antigos na raiz do repositório não são mais usados; o site publicado é gerado a partir de `content/`.

## Token para o admin

Crie um *fine-grained personal access token* em GitHub → Settings → Developer settings → Fine-grained tokens, com:
- Resource owner: `edelbertofranco`
- Repository access: somente `edelbertofranco.github.io`
- Permissions: **Contents: Read and write** (e, opcionalmente, **Actions: Read** para ver o status da publicação)

O token fica salvo apenas no seu navegador.
