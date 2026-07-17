# coleta_ima — ponte de dados do IMA para o Preço Realizado

O servidor do sistema (VPS) **não consegue** alcançar o site do IMA (o firewall
do IMA derruba o IP do datacenter). Este repositório resolve isso via
**GitHub Actions**, que roda na rede do GitHub e alcança o IMA:

1. O workflow `.github/workflows/coleta.yml` roda todo dia (09h30 de Brasília),
   executa `coleta.py`, baixa os arquivos públicos de PTV de banana do IMA e
   os commita em `dados/` (com um `dados/index.json`).
2. O app do Preço Realizado baixa esses arquivos **do GitHub** (que ele
   alcança) e importa — de forma automática.

O `index.json` é um objeto `{nome: hash_sha256}` — o app usa o hash para
baixar/reler **só o que mudou** (pula os arquivos de hash igual ao já importado).

**Trava de segurança:** se a coleta não achar nenhum link de PTV na página
(layout do IMA mudou ou a página esvaziou), ou se nenhum arquivo baixar, o job
**falha de propósito** (fica vermelho e avisa) e **não sobrescreve** o
`index.json` bom — o app continua com o último dado válido até alguém conferir.

São dados **públicos e sem informação pessoal** (movimento município→município).
Rodar manualmente: aba **Actions → Coleta IMA → Run workflow**.
