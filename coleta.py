"""Coleta os arquivos públicos de PTV de banana do portal do IMA e salva em
dados/. Roda no GitHub Actions (que alcança o IMA); o app na VPS depois baixa
esses arquivos do GitHub (que ele alcança) e importa. É a 'ponte' que a VPS
não consegue fazer direto (o IMA bloqueia o IP do datacenter da VPS)."""
import json
import os
import re
import urllib.request

PAGINA = ("https://www.ima.mg.gov.br/14-transparencia/"
          "2599-permissao-de-transito-vegetal-banana-2026")
UA = {"User-Agent": "Mozilla/5.0 (coleta IMA banana Pirapora)"}
RE_LINK = re.compile(
    r'href="(https://www\.ima\.mg\.gov\.br/files/[^"]*PTV[^"]*\.xls[x]?)"', re.I)


def baixar(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()


def main():
    os.makedirs("dados", exist_ok=True)
    html = baixar(PAGINA).decode("utf-8", "replace")
    urls = sorted(set(RE_LINK.findall(html)))
    print(f"{len(urls)} arquivo(s) no índice do IMA")
    idx = []
    for u in urls:
        m = re.search(r"/(\d{5})/", u)
        nome = (f"{m.group(1)}.{u.rsplit('.', 1)[-1]}" if m
                else re.sub(r"\W", "", u)[-16:])
        try:
            dados = baixar(u)
        except Exception as e:
            print(f"  FALHA {nome}: {str(e)[:60]}")
            continue
        with open(os.path.join("dados", nome), "wb") as f:
            f.write(dados)
        idx.append(nome)
        print(f"  baixado {nome} ({len(dados)} bytes)")
    with open(os.path.join("dados", "index.json"), "w", encoding="utf-8") as f:
        json.dump(sorted(idx), f, ensure_ascii=False, indent=0)
    print(f"TOTAL: {len(idx)} arquivos salvos em dados/")


if __name__ == "__main__":
    main()
