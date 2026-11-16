import csv
import os
import re
from gerador_site import render_page

def criar_slug(texto):
    texto = texto.lower()
    # Remove acentos
    import unicodedata
    nfkd = unicodedata.normalize('NFKD', texto)
    palavra_sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    # Remove caracteres especiais
    slug = re.sub(r'[^a-z0-9]+', '-', palavra_sem_acento)
    return slug.strip('-')

def processar_lote(csv_path="leads.csv", limite=None):
    if not os.path.exists(csv_path):
        print(f"Erro: O arquivo {csv_path} não foi encontrado.")
        return

    print(f"Lendo o arquivo {csv_path}...")
    
    with open(csv_path, mode='r', encoding='utf-8') as arquivo:
        leitor = csv.DictReader(arquivo)
        linhas = list(leitor)
        
    total = len(linhas)
    if limite:
        linhas = linhas[:limite]
        print(f"Processando um lote de {len(linhas)} leads (Total no CSV: {total})...")
    else:
        print(f"Processando todos os {total} leads...")

    sucessos = 0
    erros = 0

    for i, linha in enumerate(linhas, start=1):
        nome = linha.get('nome', '').strip()
        cidade = linha.get('cidade', 'Foz do Iguaçu').strip()
        categoria = linha.get('categoria', 'general').strip()
        
        if not nome:
            continue
            
        slug = criar_slug(f"{cidade}-{nome}")
        
        # Estrutura de dados padrão esperada pelo gerador
        dados_cliente = {
            "nome_empresa": nome,
            "slug": slug,
            "cidade": cidade,
            "categoria": categoria,
            "whatsapp": "5545999999999", # WhatsApp padrão para demonstração
            "descricao": f"Soluções profissionais e atendimento especializado em {cidade}."
        }

        try:
            output_dir = os.path.join("public", slug)
            os.makedirs(output_dir, exist_ok=True)

            print(f"[{i}/{len(linhas)}] Gerando: {nome} ({cidade}) -> public/{slug}/")
            pagina = render_page(dados_cliente)
            output_path = os.path.join(output_dir, "index.html")
            with open(output_path, mode="w", encoding="utf-8") as arquivo:
                arquivo.write(pagina)

            sucessos += 1
        except Exception as e:
            print(f"Erro ao gerar para {nome}: {e}")
            erros += 1

    print("\n==========================================")
    print(f" Processo concluído!")
    print(f" Sucessos: {sucessos} | Erros: {erros}")
    print(f" Os sites foram salvos na pasta 'public/'")
    print("==========================================")

if __name__ == "__main__":
    # Defina um limite (ex: 10) para testar primeiro, ou remova o limite para rodar todos
    processar_lote(limite=10)