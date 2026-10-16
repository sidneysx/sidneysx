"""
Gera o README estilo "neofetch" para o perfil do GitHub.

Uso:
  1. Edite o bloco CONFIG abaixo com seus dados.
  2. (Opcional) Coloque sua foto como foto.jpg nesta pasta para virar arte ASCII
     -> precisa do Pillow:  pip install pillow
  3. Rode:  python gerar_readme.py
  4. Suba README.md, dark_mode.svg e light_mode.svg no repositório
     com o MESMO nome do seu usuário (ex.: github.com/sidneysousa/sidneysousa).
"""
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

# ======================= CONFIG — edite aqui =======================
USUARIO = "sidneysx"            # seu login do GitHub
NASCIMENTO = date(1998, 10, 30)      # sua data de nascimento (vira o "Uptime")

SECOES = [
    ("header", f"{USUARIO}@github"),
    ("OS", "Debian Linux, Windows"),
    ("Uptime", "AUTO"),            # calculado a partir de NASCIMENTO
    ("Host", "gestto.shop"),
    ("Kernel", "Estudante de Sistemas de Informação"),
    ("IDE", "VS Code, Claude"),
    ("", ""),
    ("Languages.Programming", "JavaScript, PHP, C#, SQL"),
    ("Languages.Computer", "React, Laravel, Tailwind, Unity"),
    ("Languages.Real", "Português"),
    ("Hobbies.Software", "Games, Sites, Self-hosting"),
    ("", ""),
    ("section", "Projetos"),
    ("Gestto", "Sites de catálogo p/ lojas"),
    ("Delivery", "SaaS de delivery (Supabase)"),
    ("Game", "Battle royale em Unity"),
    ("", ""),
    ("section", "Contato"),
    ("Email", "sidneydev10@gmail.com"),
    ("Instagram", "@so.usa.sx"),
    ("LinkedIn", "in/sidney-silva-4372131b5"),
]
# ===================================================================

# largura da coluna de info, em caracteres (cresce sozinha p/ caber a maior linha)
LARGURA_TEXTO = max([46] + [len(k) + len(v) + 5 for k, v in SECOES
                            if k not in ("header", "section", "")])
LINHAS_ASCII = 27
COLUNAS_ASCII = 62   # ~2,3x as linhas, porque cada caractere é alto e estreito

ASCII_PADRAO = r"""
              .:-====-:.
          .-+*#%%%%%%%%#*+-.
        :+#%%%%%%%%%%%%%%%%#+:
      .+%%%%%#*+=----=+*#%%%%%+.
     -#%%%%#=:          :=#%%%%#-
    =%%%%%+.   .-====-.   .+%%%%%=
   -%%%%%=   :*%%%%%%%%*:   =%%%%%-
   *%%%%#   .#%%#=--=#%%#.   #%%%%*
   #%%%%+   =%%%=    =%%%=   +%%%%#
   *%%%%#   .#%%#=--=#%%#.   #%%%%*
   -%%%%%=   :*%%%%%%%%*:   =%%%%%-
    =%%%%%+.   .-====-.   .+%%%%%=
     -#%%%%#=:          :=#%%%%#-
      .+%%%%%#*+=----=+*#%%%%%+.
        :+#%%%%%%%%%%%%%%%%#+:
          .-+*#%%%%%%%%#*+-.
              .:-====-:.

        ____  _     _
       / ___|(_) __| |
       \___ \| |/ _` |
        ___) | | (_| |
       |____/|_|\__,_|
"""

CARACTERES = " .:-=+*#%@"


def foto_para_ascii(caminho):
    """Converte a foto em arte ASCII: partes claras viram caracteres densos,
    o fundo liso (cor dos cantos) vira espaço e tudo fica num recorte redondo."""
    from PIL import Image, ImageOps, ImageFilter
    img = ImageOps.exif_transpose(Image.open(caminho)).convert("RGB")
    lado = min(img.size)
    img = ImageOps.fit(img, (lado, lado))  # recorte quadrado central

    # cor do fundo = média dos cantos superiores
    w, h = img.size
    cantos = [img.getpixel((x, y)) for x in (5, w - 6) for y in (5, 15)]
    fundo = tuple(sum(c[i] for c in cantos) / len(cantos) for i in range(3))

    # caractere tem ~8.6px de largura e 20px de altura de linha
    pequena = img.resize((COLUNAS_ASCII, LINHAS_ASCII), Image.LANCZOS)
    cinza = ImageOps.grayscale(img).filter(ImageFilter.UnsharpMask(radius=4, percent=150))
    cinza = cinza.resize((COLUNAS_ASCII, LINHAS_ASCII), Image.LANCZOS)

    # 1) descobre quais células são "você" (dentro do círculo e diferentes do fundo)
    pessoa = {}
    for y in range(LINHAS_ASCII):
        for x in range(COLUNAS_ASCII):
            dx = (x + 0.5) / COLUNAS_ASCII - 0.5
            dy = (y + 0.5) / LINHAS_ASCII - 0.5
            if dx * dx + dy * dy > 0.25:
                continue
            r, g, b = pequena.getpixel((x, y))
            if ((r - fundo[0]) ** 2 + (g - fundo[1]) ** 2 + (b - fundo[2]) ** 2) ** 0.5 < 28:
                continue
            pessoa[(x, y)] = cinza.getpixel((x, y))

    # 2) equaliza só os tons da pessoa: cada caractere fica com a mesma fatia de pixels
    ordem = sorted(pessoa.values())
    rank = {v: i / max(1, len(ordem) - 1) for i, v in enumerate(ordem)}
    escala = CARACTERES[1:]  # sem o espaço, para a silhueta não sumir

    linhas = []
    for y in range(LINHAS_ASCII):
        linha = ""
        for x in range(COLUNAS_ASCII):
            if (x, y) in pessoa:
                linha += escala[min(len(escala) - 1, int(rank[pessoa[(x, y)]] * len(escala)))]
            else:
                linha += " "
        linhas.append(linha.rstrip())
    return linhas


def uptime(nasc):
    hoje = date.today()
    anos = hoje.year - nasc.year
    meses = hoje.month - nasc.month
    dias = hoje.day - nasc.day
    if dias < 0:
        meses -= 1
        dias += 30
    if meses < 0:
        anos -= 1
        meses += 12
    return f"{anos} anos, {meses} meses, {dias} dias"


TEMAS = {
    "dark": dict(bg="#161b22", borda="#30363d", texto="#c9d1d9",
                 chave="#ffa657", valor="#a5d6ff", ponto="#616e7f"),
    "light": dict(bg="#f6f8fa", borda="#d0d7de", texto="#24292f",
                  chave="#953800", valor="#0a3069", ponto="#c2cfde"),
}


def linha_info(chave, valor, t):
    """Monta uma linha 'Chave: ........ Valor' com tspans coloridos."""
    if chave == "header":
        traco = "—" * max(1, LARGURA_TEXTO - len(valor) - 1)
        return f'<tspan fill="{t["texto"]}">{escape(valor)} {traco}</tspan>'
    if chave == "section":
        traco = "—" * max(1, LARGURA_TEXTO - len(valor) - 3)
        return f'<tspan fill="{t["texto"]}">— {escape(valor)} {traco}</tspan>'
    if not chave:
        return ""
    pontos = "." * max(2, LARGURA_TEXTO - len(chave) - len(valor) - 3)
    return (f'<tspan fill="{t["chave"]}">{escape(chave)}</tspan>'
            f'<tspan fill="{t["texto"]}">: </tspan>'
            f'<tspan fill="{t["ponto"]}">{pontos} </tspan>'
            f'<tspan fill="{t["valor"]}">{escape(valor)}</tspan>')


def gerar_svg(ascii_linhas, tema):
    t = TEMAS[tema]
    altura_linha = 20
    n = max(len(ascii_linhas), len(SECOES))
    altura = n * altura_linha + 60
    largura_arte = max(len(l) for l in ascii_linhas)
    x_info = max(390, int(15 + largura_arte * 8.6 + 35))
    largura = x_info + LARGURA_TEXTO * 8.6 + 30

    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,\'DejaVu Sans Mono\',\'Courier New\',monospace" '
        f'width="{largura:.0f}px" height="{altura}px" font-size="14px">',
        '<style>@font-face{src:local("Consolas"),local("Consolas Bold");'
        'font-family:"ConsolasFallback";font-display:swap;'
        '-webkit-size-adjust:109%;size-adjust:109%;}</style>',
        f'<rect width="{largura:.0f}px" height="{altura}px" fill="{t["bg"]}" '
        f'stroke="{t["borda"]}" rx="15"/>',
        f'<text x="15" y="30" fill="{t["texto"]}" xml:space="preserve">',
    ]
    for i, l in enumerate(ascii_linhas):
        partes.append(f'<tspan x="15" y="{30 + i * altura_linha}">{escape(l)}</tspan>')
    partes.append("</text>")

    partes.append(f'<text x="{x_info}" y="30" fill="{t["texto"]}" xml:space="preserve">')
    for i, (k, v) in enumerate(SECOES):
        if k == "Uptime" and v == "AUTO":
            v = uptime(NASCIMENTO)
        conteudo = linha_info(k, v, t)
        if conteudo:
            partes.append(f'<tspan x="{x_info}" y="{30 + i * altura_linha}">{conteudo}</tspan>')
    partes.append("</text></svg>")
    return "\n".join(partes)


README = f"""<a href="https://github.com/{USUARIO}">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="dark_mode.svg">
    <img alt="{USUARIO} GitHub Profile README" src="light_mode.svg">
  </picture>
</a>
"""


if __name__ == "__main__":
    pasta = Path(__file__).parent
    foto = next((pasta / f for f in ("foto.jpg", "foto.png", "foto.jpeg")
                 if (pasta / f).exists()), None)
    if foto:
        arte = foto_para_ascii(foto)
        print(f"Arte ASCII gerada a partir de {foto.name}")
    else:
        arte = ASCII_PADRAO.strip("\n").splitlines()
        print("Sem foto.jpg — usando arte ASCII padrão")

    for tema in TEMAS:
        (pasta / f"{tema}_mode.svg").write_text(gerar_svg(arte, tema), encoding="utf-8")
    (pasta / "README.md").write_text(README, encoding="utf-8")
    print("Pronto: README.md, dark_mode.svg, light_mode.svg")