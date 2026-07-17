# coleta_ima — ponte de dados do IMA para o Preço Realizado

O servidor do sistema (VPS) **não consegue** alcançar o site do IMA (o firewall
do IMA derruba o IP do datacenter). Este repositório resolve isso via
**GitHub Actions**, que roda na rede do GitHub e alcança o IMA:

1. O workflow `.github/workflows/coleta.yml` roda todo dia (09h30 de Brasília),
   executa `coleta.py`, baixa os arquivos públicos de PTV de banana do IMA e
   os commita em `dados/` (com um `dados/index.json`).
2. O app do Preço Realizado baixa esses arquivos **do GitHub** (que ele
   alcança) e importa — de forma automática.

São dados **públicos e sem informação pessoal** (movimento município→município).
Rodar manualmente: aba **Actions → Coleta IMA → Run workflow**.
