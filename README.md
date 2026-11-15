# Bot Caçador

Projeto Python para pesquisa manual de estabelecimentos sem site cadastrado no OpenStreetMap e geração de landing pages estáticas para clientes.

## Pesquisa

O pesquisador consulta a Overpass API para Foz do Iguaçu e Ciudad del Este e cria `leads.csv` com nome, cidade, categoria, coordenadas e link do OpenStreetMap. Não coleta e-mails, não envia propostas e não contata empresas. Revise os resultados: ausência de site no OSM não confirma que o estabelecimento não tenha site.

```powershell
python -m pip install -r requirements.txt
python bot_cacador.py
python bot_cacador.py --cities "Foz do Iguaçu" --output dados/foz.csv
```

Use os dados de acordo com os termos do OpenStreetMap/Overpass e a legislação aplicável. Faça contato comercial somente de forma legítima, identificada e consentida, respeitando pedidos de descadastro e regras locais.

## Gerar landing page

Copie `data/cliente.example.json`, substitua os dados e execute:

```powershell
python gerador_site.py data/cliente.example.json --output public
```

O resultado será gravado em `public/<slug>/index.html`, pronto para ser hospedado em um serviço estático. O gerador escapa os valores textuais e valida o número do WhatsApp. A publicação em hospedagem externa depende de configurar e autorizar o provedor escolhido.

Campos obrigatórios: `nome_empresa`, `cidade`, `whatsapp` e `descricao`. `slug` é opcional; `servicos` deve ser uma lista de textos. O campo opcional `categoria` aceita valores do OpenStreetMap como `car_repair`, `car_parts`, `pharmacy`, `clinic`, `restaurant`, `cafe`, `bakery`, `hairdresser`, `dentist` e `hardware`. Cada grupo define automaticamente cores e ícone; categorias desconhecidas usam o tema neutro.

Também é possível usar um CSV com cabeçalho, incluindo o `leads.csv` criado pelo pesquisador. O CSV precisa conter `nome` (ou `nome_empresa`), `cidade` e `categoria`; informe o WhatsApp e a descrição comercial ausentes pela linha de comando:

```powershell
python gerador_site.py leads.csv --csv-row 1 --whatsapp 5545999999999 --descricao "Serviços e atendimento da empresa." --output public
```

`--csv-row` seleciona o registro, começando em 1 e sem contar o cabeçalho. As opções `--whatsapp` e `--descricao` também podem substituir os valores fornecidos no arquivo.

## GitHub Actions

Em **Actions**, execute manualmente o workflow **Pesquisa de estabelecimentos sem site**. O CSV ficará disponível como artefato por sete dias. A execução não é agendada e não envia mensagens.