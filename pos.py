import requests
from getpass import getpass
from pathlib import Path
from datetime import datetime
from database import listar_transacoes

API_URL = "http://127.0.0.1:8000/payments/authorize"


def money_to_cents(value: str) -> int:
    normalized = value.replace(",", ".").strip()
    return int(round(float(normalized) * 100))


def choose_payment_method():
    print("\nEscolha o tipo de pagamento:")
    print("1 - Debito")
    print("2 - Credito")

    option = input("> ").strip()

    if option == "1":
        return "DEBIT"

    if option == "2":
        return "CREDIT"

    raise ValueError("Opcao invalida")


def salvar_comprovante(valor, cartao, autorizacao):
    pasta = Path("comprovantes")
    pasta.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo = pasta / f"comprovante_{timestamp}.txt"

    conteudo = f"""
================================
COMPROVANTE LOJISTA
================================
Status: APROVADO
Valor: R$ {valor}
Cartao: ****{cartao}
Autorizacao: {autorizacao}
================================
"""

    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)

    print(f"\nComprovante salvo em: {arquivo}")

def mostrar_historico():
    transacoes = listar_transacoes()

    print("\n================================")
    print("           HISTORICO")
    print("==================================")

    if not transacoes:
        print("Nenhuma transacao encontrada.")
        return
    for tx in transacoes:
        valor = tx[1] / 100

        print(f"\nID: {tx[0]}")
        print(f"Valor: R${valor:.2f}")
        print(f"Status: {tx[2]}")

def realizar_venda():
    print("===================================")
    print("      MAQUININHA MVP TERMINAL")
    print("===================================")

    try:
        amount = input("\nDigite o valor da venda: R$ ")
        amount_cents = money_to_cents(amount)

        payment_method = choose_payment_method()

        card_number = input("\nDigite o numero do cartao: ").strip()
        pin = getpass("Digite a senha: ")

        print("\nProcessando transacao...")

        response = requests.post(
            API_URL,
            json={
                "amount_cents": amount_cents,
                "payment_method": payment_method,
                "card_number": card_number,
                "pin": pin
            },
            timeout=10
        )

        data = response.json()

        print("\n===================================")

        if data["status"] == "APPROVED":
            valor_formatado = f"{amount_cents / 100:.2f}".replace(".", ",")

            print("TRANSAÇÃO APROVADA")
            print("")
            print("================================")
            print("           COMPROVANTE")
            print("================================")
            print("Status: APROVADO")
            print(f"Valor: R$ {valor_formatado}")
            print(f"Cartao: ****{data['card_last4']}")
            print(f"Autorizacao: {data['auth_code']}")
            print("================================")

            salvar_comprovante(
                valor_formatado,
                data["card_last4"],
                data["auth_code"]
            )

        else:
            print("TRANSAÇÃO NEGADA")
            print(f"Motivo: {data['reason']}")
            print(f"Cartao final: {data['card_last4']}")

        print("===================================")

    except requests.exceptions.ConnectionError:
        print("\nErro: API nao esta rodando.")

    except Exception as error:
        print(f"\nErro: {error}")


def main():
    while True:
        print("\n=============================")
        print("     MENU DA MAQUININHA")
        print("===============================")
        print("1- Nova venda")
        print("2 - Historico")
        print("3 - Sair")

        opcao = input("> ").strip()

        if opcao == "1":
            realizar_venda()
        elif opcao == "2":
            mostrar_historico()
        elif opcao == "3":
            print("Encerrando maquininha...")
            break
        else:
            print("Opcao invalida")

if __name__ == "__main__":
    main()