# Maquininha MVP - Simulador no Terminal

Este projeto simula uma maquininha de cartão sem interface gráfica.

## Como rodar

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Em um terminal, rode a API:

```bash
uvicorn api:app --reload
```

3. Em outro terminal, rode a maquininha:

```bash
python pos.py
```

## Cartões de teste

### Aprovado
- Cartão: `4111111111111111`
- Senha: `1234`

### Negado por saldo insuficiente
- Cartão: `4000000000000002`
- Senha: `1234`

### Negado por cartão bloqueado
- Cartão: `4000000000009995`
- Senha: `1234`

## Arquivos

- `pos.py`: simula a maquininha no terminal.
- `api.py`: backend que recebe a transação.
- `issuer.py`: banco emissor fake.
- `database.py`: salva transações em SQLite.
