"""Coleta os arquivos públicos de PTV de banana do portal do IMA e salva em
dados/. Roda no GitHub Actions (que alcança o IMA); o app na VPS depois baixa
esses arquivos do GitHub (que ele alcança) e importa. É a 'ponte' que a VPS
não consegue fazer direto (o IMA bloqueia o IP do datacenter da VPS).

O índice dados/index.json é um objeto {nome: hash_sha256} — o app usa o hash
para baixar/reler SÓ o que mudou (pula os arquivos de hash igual ao já
importado)."""
import hashlib
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
    # Trava: 0 links = a página do IMA mudou de layout (ou esvaziou). Falhar o
    # job DE PROPÓSITO (fica vermelho e avisa) e NÃO escrever um index.json
    # vazio — o índice bom de ontem fica preservado, o app segue com o que tem.
    if not urls:
        raise SystemExit(
            "ERRO: nenhum link de PTV encontrado na página do IMA — o layout "
            "pode ter mudado. Job falhado de propósito para avisar; o "
            "index.json anterior (bom) foi preservado, sem sobrescrever.")
    idx = {}
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
        idx[nome] = hashlib.sha256(dados).hexdigest()
        print(f"  baixado {nome} ({len(dados)} bytes)")
    # Mesma trava se, apesar de haver links, NENHUM arquivo baixou (IMA instável
    # na hora): não sobrescreve o índice bom com vazio; falha para retentar.
    if not idx:
        raise SystemExit(
            "ERRO: havia %d link(s) mas nenhum arquivo baixou — index.json bom "
            "preservado, sem sobrescrever." % len(urls))
    with open(os.path.join("dados", "index.json"), "w", encoding="utf-8") as f:
        json.dump(dict(sorted(idx.items())), f, ensure_ascii=False, indent=0)
    print(f"TOTAL: {len(idx)} arquivos salvos em dados/")


if __name__ == "__main__":
    main()
