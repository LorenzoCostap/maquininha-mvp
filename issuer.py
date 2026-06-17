import random

CARDS = {
    "4111111111111111": {
        "pin": "1234",
        "limit_cents": 100000,
        "blocked": False
    },
    "4000000000000002": {
        "pin": "1234",
        "limit_cents": 1000,
        "blocked": False
    },
    "4000000000009995": {
        "pin": "1234",
        "limit_cents": 100000,
        "blocked": True
    }
}

def authorize(card_number: str, pin: str, amount_cents: int):
    card = CARDS.get(card_number)

    if not card:
        return {
            "approved": False,
            "reason": "Cartão não encontrado"
        }

    if card["blocked"]:
        return {
            "approved": False,
            "reason": "Cartão bloqueado"
        }

    if pin != card["pin"]:
        return {
            "approved": False,
            "reason": "Senha inválida"
        }

    if amount_cents > card["limit_cents"]:
        return {
            "approved": False,
            "reason": "Saldo ou limite insuficiente"
        }

    return {
        "approved": True,
        "reason": None,
        "auth_code": str(random.randint(100000, 999999))
    }
