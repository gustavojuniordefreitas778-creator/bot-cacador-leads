import time
import pandas as pd
import pywhatkit as kit
import unicodedata

def limpar_slug(texto):
    nfkd = unicodedata.normalize('NFKD', str(texto))
    palavra_sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return palavra_sem_acento.lower().replace(' ', '-').replace('ç', 'c').replace('.', '').strip()

try:
    df = pd.read_csv("leads.csv")
except Exception as e:
    print(f"Erro ao ler leads.csv: {e}")
    exit()

for index, lead in df.iterrows():
    nome_empresa = str(lead.get("nome", "Empresa")).strip()
    cidade = str(lead.get("cidade", "Parana")).strip()
    telefone = str(lead.get("telefone", "")).strip()

    # Ignora linhas sem telefone válido ou vazias
    if not telefone or telefone.lower() == "nan" or telefone.lower() == "none" or telefone == "":
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
    print(f"A enviar para: {nome_empresa} (+{telefone_limpo})")
    print(f"Link: {link_site}")

    # Envia a mensagem de forma instantânea
    kit.sendwhatmsg_instantly(f"+{telefone_limpo}", mensagem, wait_time=15, tab_close=True)
    
    # Pausa de 10 segundos entre cada envio para dar tempo ao WhatsApp Web de fechar o separador e abrir o próximo
    time.sleep(10)