import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("transactions.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount_cents INTEGER NOT NULL,
            payment_method TEXT NOT NULL,
            card_last4 TEXT NOT NULL,
            status TEXT NOT NULL,
            reason TEXT,
            auth_code TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_transaction(amount_cents, payment_method, card_last4, status, reason=None, auth_code=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO transactions (
            amount_cents,
            payment_method,
            card_last4,
            status,
            reason,
            auth_code,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        amount_cents,
        payment_method,
        card_last4,
        status,
        reason,
        auth_code,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def listar_transacoes():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            amount_cents,
            status
        FROM transactions
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cur.fetchall()

    conn.close()

    return rows


def estorno_transacao(transaction_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT status
        FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    row = cur.fetchone()

    if not row:
        conn.close()
        return False, "Transacao nao encontrada"

    if row[0] != "APPROVED":
        conn.close()
        return False, "Somente transacoes aprovadas podem ser estornadas"

    cur.execute("""
        UPDATE transactions
        SET status = 'REFUNDED',
            reason = 'Transacao estornada'
        WHERE id = ?
    """, (transaction_id,))

    conn.commit()
    conn.close()

    return True, "Transacao estornada com sucesso"