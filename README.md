# 💳 Maquininha MVP

Simulação de uma **maquininha de cartão (POS)** e do fluxo de autorização de uma **adquirente**, tudo rodando no terminal. A maquininha envia a venda para uma API em FastAPI, que consulta um **banco emissor fake**, grava a transação em SQLite e devolve aprovado ou negado com o motivo.

![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=flat&logo=sqlite&logoColor=white)

## ✨ Funcionalidades

- **Venda no terminal**: valor, débito ou crédito, número do cartão e senha (digitada sem aparecer na tela)
- **Autorização pelo emissor**: valida cartão, bloqueio, senha e limite, e gera código de autorização
- **Comprovante do lojista** impresso na tela e salvo em `comprovantes/`
- **Histórico** das últimas 20 transações direto na maquininha
- **Estorno** de transações aprovadas
- **Dashboard web** com fechamento de lote: aprovadas, negadas, estornadas e total líquido

## 🔄 Como funciona

```
pos.py (maquininha)  ──POST /payments/authorize──▶  api.py (adquirente)
                                                       │
                                                       ├─▶ issuer.py   (emissor fake: aprova ou nega)
                                                       └─▶ database.py (grava em transactions.db)
```

Os valores trafegam em **centavos** (`amount_cents`) para evitar erro de arredondamento, e só os **4 últimos dígitos** do cartão são salvos.

## ▶️ Como rodar

```bash
pip install -r requirements.txt
```

Em um terminal, suba a API:

```bash
uvicorn api:app --reload
```

Em outro terminal, abra a maquininha:

```bash
python pos.py
```

O dashboard fica em `http://127.0.0.1:8000/dashboard` e a documentação interativa da API em `http://127.0.0.1:8000/docs`.

## 🧪 Cartões de teste

Todos usam a senha `1234`.

| Cartão | Resultado |
|---|---|
| `4111111111111111` | ✅ Aprovado (limite de R$ 1.000,00) |
| `4000000000000002` | ❌ Negado por saldo insuficiente (limite de R$ 10,00) |
| `4000000000009995` | ❌ Negado por cartão bloqueado |

Senha errada ou cartão desconhecido também são negados, cada um com seu motivo.

## 🔌 Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Health check |
| POST | `/payments/authorize` | Autoriza um pagamento |
| POST | `/payments/{id}/refund` | Estorna uma transação aprovada |
| GET | `/dashboard` | Fechamento de lote e últimas transações |

Exemplo de requisição:

```json
{
  "amount_cents": 2590,
  "payment_method": "CREDIT",
  "card_number": "4111111111111111",
  "pin": "1234"
}
```

## 📁 Estrutura

| Arquivo | Papel |
|---|---|
| `pos.py` | Maquininha no terminal: menu, venda, comprovante e histórico |
| `api.py` | Adquirente: autorização, estorno e dashboard |
| `issuer.py` | Banco emissor fake com os cartões de teste |
| `database.py` | Persistência das transações em SQLite |
