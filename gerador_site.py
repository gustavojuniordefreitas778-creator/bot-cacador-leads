import os
import sys
import pandas as pd
import unicodedata

def limpar_slug(texto):
    nfkd = unicodedata.normalize('NFKD', str(texto))
    palavra_sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return palavra_sem_acento.lower().replace(' ', '-').replace('ç', 'c').replace('.', '')

def gerar_landing_pages():
    try:
        df = pd.read_csv("leads.csv")
    except Exception as e:
        print(f"Erro ao ler leads.csv: {e}")
        return

    for index, lead in df.iterrows():
        nome_empresa = lead.get("nome_empresa", lead.get("name", "Empresa Local"))
        cidade = lead.get("cidade", lead.get("city", "Parana"))
        
        cidade_slug = limpar_slug(cidade)
        empresa_slug = limpar_slug(nome_empresa)
        slug = f"{cidade_slug}-{empresa_slug}"

        # Caminho da pasta public/<slug>
        pasta_destino = os.path.join("public", slug)
        os.makedirs(pasta_destino, exist_ok=True)

        # Conteúdo HTML de demonstração simples para o cliente
        html_conteudo = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Demonstração - {nome_empresa}</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f4f4f9; color: #333; }}
        h1 {{ color: #007bff; }}
        .card {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: inline-block; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>{nome_empresa}</h1>
        <p>Demonstração de site profissional desenvolvida para negócios locais em {cidade}.</p>
        <p><strong>Entre em contacto para saber mais!</strong></p>
    </div>
</body>
</html>
"""
        caminho_arquivo = os.path.join(pasta_destino, "index.html")
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(html_conteudo)
        
        print(f"Landing page gerada com sucesso em: {caminho_arquivo}")

if __name__ == "__main__":
    gerar_landing_pages()