# Instale a dependência opcional com: pip install pywhatkit
# O WhatsApp Web deve estar conectado no navegador padrão para o envio.

from __future__ import annotations

import time
import webbrowser
from urllib.parse import urlencode

DESTINATARIO = "+5545999046969"
MENSAGEM = (
    "Olá! Tudo bem? Meu nome é Gustavo e desenvolvi uma demonstração de site "
    "para a Farma Util, negócio local de Foz do Iguaçu. Gostaria de apresentar "
    "a proposta e saber o que acha. Você pode conferir a demonstração aqui: "
    f"{"https://gustavojuniordefreitas778-creator.github.io/bot-cacador-leads/"}"
)
TEMPO_CARREGAMENTO = 20


def main() -> None:
    try:
        import pywhatkit
    except ImportError:
        parametros = urlencode({"phone": DESTINATARIO, "text": MENSAGEM})
        url = f"https://web.whatsapp.com/send?{parametros}"
        print("pywhatkit não está instalado; abrindo a mensagem no WhatsApp Web.")
        webbrowser.open(url)
        time.sleep(TEMPO_CARREGAMENTO)
        print("A mensagem está preenchida. Confira o destinatário e clique em Enviar.")
        return

    print(f"Aguardando {TEMPO_CARREGAMENTO} segundos para carregar o WhatsApp Web...")
    pywhatkit.sendwhatmsg_instantly(
        DESTINATARIO,
        MENSAGEM,
        wait_time=TEMPO_CARREGAMENTO,
        tab_close=False,
    )
    print("Mensagem enviada.")


if __name__ == "__main__":
    main()
