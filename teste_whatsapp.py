import pandas as pd
import pywhatkit as kit
import unicodedata

def limpar_slug(texto):
    nfkd = unicodedata.normalize('NFKD', str(texto))
    palavra_sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return palavra_sem_acento.lower().replace(' ', '-').replace('ç', 'c').replace('.', '')

try:
    df = pd.read_csv("leads.csv")
except Exception as e:
    print(f"Erro ao ler o ficheiro leads.csv: {e}")
    exit()

if df.empty:
    print("O ficheiro leads.csv está vazio.")
    exit()

for index, lead in df.iterrows():
    nome_empresa = lead.get("nome_empresa", lead.get("name", "Empresa Local"))
    cidade = lead.get("cidade", lead.get("city", "Parana"))
    telefone = str(lead.get("whatsapp", lead.get("phone", lead.get("telefone", "")))).strip()

    if not telefone or telefone.lower() == "nan" or telefone.lower() == "none":
        continue

    telefone_limpo = "".join(filter(str.isdigit, telefone))
    if not telefone_limpo.startswith("55") and len(telefone_limpo) <= 11:
        telefone_limpo = "55" + telefone_limpo

    cidade_slug = limpar_slug(cidade)
    empresa_slug = limpar_slug(nome_empresa)
    slug = f"{cidade_slug}-{empresa_slug}"

    link_site = f"https://gustavojuniordefreitas778-creator.github.io/bot-cacador-leads/public/{slug}/"

    mensagem = (
        f"Olá! Tudo bem? Meu nome é Gustavo e desenvolvi uma demonstração de site "
        f"para a {nome_empresa}, negócio local de {cidade}. Gostaria de apresentar a proposta "
        f"e saber o que acha. Você pode conferir a demonstração aqui: {link_site}"
    )

    print(f"\n----------------------------------------")
    print(f"A enviar para o cliente: {nome_empresa}")
    print(f"Número de destino: +{telefone_limpo}")
    print(f"Link da página: {link_site}")

    kit.sendwhatmsg_instantly(f"+{telefone_limpo}", mensagem, wait_time=15, tab_close=True)
    break