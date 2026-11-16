import unicodedata
import pandas as pd
import pywhatkit as kit


def limpar_slug(texto):
  # Remove acentos (ex: ç -> c, á -> a) e converte para minúsculas
  nfkd = unicodedata.normalize("NFKD", str(texto))
  palavra_sem_acento = "".join(
      [c for c in nfkd if not unicodedata.combining(c)]
  )
  return (
      palavra_sem_acento.lower()
      .replace(" ", "-")
      .replace("ç", "c")
      .replace(".", "")
  )


# 1. Carregar o arquivo de leads gerado pelo bot
try:
  df = pd.read_csv("leads.csv")
  print("Colunas detetadas no CSV:", df.columns.tolist())
except Exception as e:
  print(f"Erro ao ler o ficheiro leads.csv: {e}")
  exit()

# 2. Verificar se existem dados no CSV
if df.empty:
  print("O ficheiro leads.csv está vazio.")
  exit()

# 3. Percorrer os leads para extrair as informações corretas
for index, lead in df.iterrows():
  # Identificar o nome da empresa (procura em português ou inglês)
  nome_empresa = lead.get("nome_empresa", lead.get("name", "Empresa Local"))

  # Identificar a cidade
  cidade = lead.get("cidade", lead.get("city", "Parana"))

  # Identificar o telefone / WhatsApp
  telefone = str(
      lead.get("whatsapp", lead.get("phone", lead.get("telefone", "")))
  ).strip()

  # Se o telefone estiver vazio ou inválido, passa para o próximo
  if not telefone or telefone.lower() == "nan" or telefone.lower() == "none":
    continue

  # Limpar caracteres não numéricos do telefone (deixa apenas os dígitos)
  telefone_limpo = "".join(filter(str.isdigit, telefone))

  # Garantir que o DDI do Brasil (55) está incluído se faltar
  if not telefone_limpo.startswith("55") and len(telefone_limpo) <= 11:
    telefone_limpo = "55" + telefone_limpo

  # Criar o slug limpo (sem acentos ou caracteres especiais para evitar 404)
  cidade_slug = limpar_slug(cidade)
  empresa_slug = limpar_slug(nome_empresa)
  slug = f"{cidade_slug}-{empresa_slug}"

  link_site = (
      f"https://gustavojuniordefreitas778-creator.github.io/bot-cacador-leads/public/{slug}/"
  )

  # Mensagem de prospecção personalizada
  mensagem = (
      f"Olá! Tudo bem? Meu nome é Gustavo e desenvolvi uma demonstração de site"
      f" para a {nome_empresa}, negócio local de {cidade}. Gostaria de apresentar"
      f" a proposta e saber o que acha. Você pode conferir a demonstração"
      f" aqui: {link_site}"
  )

  print(f"\n----------------------------------------")
  print(f"A enviar para o cliente: {nome_empresa}")
  print(f"Número de destino: +{telefone_limpo}")
  print(f"Link da página: {link_site}")

  # Envia automaticamente para o número do cliente via WhatsApp Web
  kit.sendwhatmsg_instantly(f"+{telefone_limpo}", mensagem, wait_time=15, tab_close=True)

  # Parar no primeiro envio para teste seguro
  break