from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from database import init_db, save_transaction, listar_transacoes, estorno_transacao
from issuer import authorize

app = FastAPI(title="Maquininha MVP")


class PaymentRequest(BaseModel):
    amount_cents: int = Field(gt=0)
    payment_method: str
    card_number: str
    pin: str


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def health_check():
    return {"status": "online"}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    transacoes = listar_transacoes()

    total = len(transacoes)
    aprovadas = len([tx for tx in transacoes if tx[2] == "APPROVED"])
    negadas = len([tx for tx in transacoes if tx[2] == "DECLINED"])
    estornadas = len([tx for tx in transacoes if tx[2] == "REFUNDED"])

    total_aprovado = sum(tx[1] for tx in transacoes if tx[2] == "APPROVED")
    total_estornado = sum(tx[1] for tx in transacoes if tx[2] == "REFUNDED")
    total_liquido = total_aprovado - total_estornado

    linhas = ""

    for tx in transacoes:
        valor = tx[1] / 100
        acao = ""

        if tx[2] == "APPROVED":
            acao = f'<a href="/refund/{tx[0]}">Estornar</a>'

        linhas += f"""
        <tr>
            <td>{tx[0]}</td>
            <td>R$ {valor:.2f}</td>
            <td>{tx[2]}</td>
            <td>{acao}</td>
        </tr>
        """

    return f"""
    <html>
        <head>
            <title>Dashboard Maquininha</title>
        </head>

        <body style="font-family: Arial; margin: 40px;">
            <h1>Dashboard da Maquininha</h1>

            <h2>Fechamento de Lote</h2>
            <p>Total de transacoes: {total}</p>
            <p>Aprovadas: {aprovadas}</p>
            <p>Negadas: {negadas}</p>
            <p>Estornadas: {estornadas}</p>
            <p>Total aprovado: R$ {total_aprovado / 100:.2f}</p>
            <p>Total estornado: R$ {total_estornado / 100:.2f}</p>
            <h3>Total liquido: R$ {total_liquido / 100:.2f}</h3>

            <h2>Ultimas transacoes</h2>

            <table border="1" cellpadding="10">
                <tr>
                    <th>ID</th>
                    <th>Valor</th>
                    <th>Status</th>
                    <th>Acao</th>
                </tr>
                {linhas}
            </table>
        </body>
    </html>
    """


@app.get("/refund/{transaction_id}")
def refund_from_dashboard(transaction_id: int):
    estorno_transacao(transaction_id)
    return RedirectResponse(url="/dashboard", status_code=302)


@app.post("/payments/{transaction_id}/refund")
def refund_payment(transaction_id: int):
    success, message = estorno_transacao(transaction_id)

    if success:
        return {
            "status": "REFUNDED",
            "message": message,
            "transaction_id": transaction_id
        }

    return {
        "status": "ERROR",
        "message": message,
        "transaction_id": transaction_id
    }


@app.post("/payments/authorize")
def authorize_payment(payload: PaymentRequest):
    issuer_response = authorize(
        card_number=payload.card_number,
        pin=payload.pin,
        amount_cents=payload.amount_cents
    )

    card_last4 = payload.card_number[-4:]

    if issuer_response["approved"]:
        save_transaction(
            amount_cents=payload.amount_cents,
            payment_method=payload.payment_method,
            card_last4=card_last4,
            status="APPROVED",
            auth_code=issuer_response["auth_code"]
        )

        return {
            "status": "APPROVED",
            "message": "Transacao aprovada",
            "auth_code": issuer_response["auth_code"],
            "card_last4": card_last4
        }

    save_transaction(
        amount_cents=payload.amount_cents,
        payment_method=payload.payment_method,
        card_last4=card_last4,
        status="DECLINED",
        reason=issuer_response["reason"]
    )

    return {
        "status": "DECLINED",
        "message": "Transacao negada",
        "reason": issuer_response["reason"],
        "card_last4": card_last4
    }